import { useEffect, useMemo, useState } from "react";
import { Download, FileText, Languages, Loader2, LogIn, RefreshCw, Upload } from "lucide-react";
import clsx from "clsx";

type Language = {
  id: number;
  name: string;
  code: string;
  libretranslate_code?: string | null;
  is_active?: boolean;
};

type UploadedBook = {
  id: string;
  title: string;
  status: string;
  message?: string;
};

type TranslationJob = {
  translation_id: string;
  status: string;
  task_id?: string;
  output_format?: string;
};

type JobStatus = {
  job_id: string;
  status: string;
  started_at?: string | null;
  completed_at?: string | null;
  error_message?: string | null;
};

const API_BASE = import.meta.env.VITE_TRANSLATION_API_URL || "http://localhost:8002";
const defaultEmail = "admin@curriculum.edu";
const defaultPassword = "admin123";

const outputFormats = ["pdf", "txt"];

const getErrorMessage = async (response: Response) => {
  try {
    const data = await response.json();
    if (typeof data.detail === "string") return data.detail;
    return JSON.stringify(data.detail || data);
  } catch {
    return response.statusText || "Request failed";
  }
};

export const DocumentTranslationPage = () => {
  const [email, setEmail] = useState(defaultEmail);
  const [password, setPassword] = useState(defaultPassword);
  const [token, setToken] = useState(() => localStorage.getItem("documentTranslationToken") || "");
  const [languages, setLanguages] = useState<Language[]>([]);
  const [sourceLanguageId, setSourceLanguageId] = useState<number>(21);
  const [targetLanguageId, setTargetLanguageId] = useState<number>(1);
  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("");
  const [firstContentPage, setFirstContentPage] = useState(1);
  const [outputFormat, setOutputFormat] = useState("pdf");
  const [file, setFile] = useState<File | null>(null);
  const [book, setBook] = useState<UploadedBook | null>(null);
  const [translation, setTranslation] = useState<TranslationJob | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const authHeaders = useMemo(
    () => (token ? { Authorization: `Bearer ${token}` } : {}),
    [token]
  );

  const targetLanguage = languages.find((language) => language.id === targetLanguageId);

  const setSuccess = (text: string) => {
    setError("");
    setMessage(text);
  };

  const setFailure = (text: string) => {
    setMessage("");
    setError(text);
  };

  const login = async () => {
    setBusy(true);
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) throw new Error(await getErrorMessage(response));
      const data = await response.json();
      localStorage.setItem("documentTranslationToken", data.access_token);
      setToken(data.access_token);
      setSuccess("Connected to the document translation backend.");
    } catch (err) {
      setFailure(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  };

  const loadLanguages = async () => {
    try {
      const response = await fetch(`${API_BASE}/admin/languages`);
      if (!response.ok) throw new Error(await getErrorMessage(response));
      const data = await response.json();
      setLanguages(data);
      const english = data.find((language: Language) => language.code === "en");
      const swahili = data.find((language: Language) => language.code === "sw");
      if (english) setSourceLanguageId(english.id);
      if (swahili) setTargetLanguageId(swahili.id);
    } catch (err) {
      setFailure(err instanceof Error ? err.message : "Could not load languages");
    }
  };

  useEffect(() => {
    void loadLanguages();
  }, []);

  const uploadDocument = async () => {
    if (!token) {
      setFailure("Login first before uploading a document.");
      return;
    }
    if (!file) {
      setFailure("Choose a PDF, DOC, or DOCX file first.");
      return;
    }

    setBusy(true);
    setBook(null);
    setTranslation(null);
    setJobStatus(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("title", title || file.name);
      if (subject) formData.append("subject", subject);
      formData.append("first_content_page", String(firstContentPage));

      const response = await fetch(`${API_BASE}/admin/books/upload`, {
        method: "POST",
        headers: authHeaders,
        body: formData,
      });
      if (!response.ok) throw new Error(await getErrorMessage(response));
      const data = await response.json();
      setBook(data);
      setSuccess(data.message || "Document uploaded. Wait a moment for text extraction before starting translation.");
    } catch (err) {
      setFailure(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  };

  const startTranslation = async () => {
    if (!token || !book) {
      setFailure("Upload a document before starting translation.");
      return;
    }

    setBusy(true);
    setTranslation(null);
    setJobStatus(null);
    try {
      const params = new URLSearchParams({
        content_type: "book",
        content_id: book.id,
        language_id: String(targetLanguageId),
        output_format: outputFormat,
      });
      if (sourceLanguageId) params.set("source_language_id", String(sourceLanguageId));

      const response = await fetch(`${API_BASE}/student/translate?${params.toString()}`, {
        method: "POST",
        headers: authHeaders,
      });
      if (!response.ok) throw new Error(await getErrorMessage(response));
      const data = await response.json();
      setTranslation(data);
      setSuccess("Translation started. Status will update automatically.");
    } catch (err) {
      setFailure(
        err instanceof Error
          ? err.message
          : "Translation could not start. If extraction is still running, wait a few seconds and retry."
      );
    } finally {
      setBusy(false);
    }
  };

  const refreshStatus = async () => {
    if (!token || !translation?.task_id) return;
    try {
      const response = await fetch(`${API_BASE}/student/translate/status/${translation.task_id}`, {
        headers: authHeaders,
      });
      if (!response.ok) throw new Error(await getErrorMessage(response));
      const data = await response.json();
      setJobStatus(data);
      if (data.status === "done") setSuccess("Translation is ready to download.");
      if (data.status === "failed") setFailure(data.error_message || "Translation failed.");
    } catch (err) {
      setFailure(err instanceof Error ? err.message : "Could not refresh status");
    }
  };

  useEffect(() => {
    if (!translation?.task_id) return;
    void refreshStatus();
    const interval = window.setInterval(() => {
      void refreshStatus();
    }, 5000);
    return () => window.clearInterval(interval);
  }, [translation?.task_id, token]);

  const downloadTranslation = async () => {
    if (!token || !translation?.translation_id) return;

    setBusy(true);
    try {
      const response = await fetch(
        `${API_BASE}/student/translate/${translation.translation_id}/download?format=${outputFormat}`,
        { headers: authHeaders }
      );
      if (!response.ok) throw new Error(await getErrorMessage(response));

      const blob = await response.blob();
      const href = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = href;
      link.download = `${book?.title || "translation"}.${outputFormat}`.replace(/[^a-z0-9._-]+/gi, "_");
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(href);
      setSuccess("Download started.");
    } catch (err) {
      setFailure(err instanceof Error ? err.message : "Download failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-0 flex-1 overflow-y-auto bg-zinc-950 text-zinc-100">
      <div className="mx-auto grid max-w-6xl gap-5 px-4 py-6 lg:grid-cols-[360px_1fr]">
        <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-4 shadow-xl shadow-black/20">
          <div className="mb-4 flex items-center gap-2">
            <LogIn className="h-5 w-5 text-emerald-300" />
            <h2 className="text-base font-semibold">Translation Backend</h2>
          </div>

          <div className="space-y-3">
            <label className="block text-sm text-zinc-300">
              Email
              <input
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-white outline-none focus:border-emerald-400"
              />
            </label>
            <label className="block text-sm text-zinc-300">
              Password
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-white outline-none focus:border-emerald-400"
              />
            </label>
            <button
              type="button"
              onClick={login}
              disabled={busy}
              className="flex w-full items-center justify-center gap-2 rounded-md bg-emerald-500 px-3 py-2 text-sm font-semibold text-zinc-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <LogIn className="h-4 w-4" />}
              {token ? "Reconnect" : "Login"}
            </button>
          </div>

          <div className="mt-5 rounded-md border border-zinc-800 bg-zinc-950 p-3 text-xs text-zinc-400">
            <div className="mb-1 font-medium text-zinc-200">Service</div>
            <div>{API_BASE}</div>
            <div className={clsx("mt-2 font-medium", token ? "text-emerald-300" : "text-amber-300")}>
              {token ? "Authenticated" : "Login required for uploads and translations"}
            </div>
          </div>
        </section>

        <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-4 shadow-xl shadow-black/20">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-sky-300" />
                <h2 className="text-base font-semibold">Book & Document Translation</h2>
              </div>
              <p className="mt-1 text-sm text-zinc-400">
                Upload a book or document, translate it asynchronously, then download the translated output.
              </p>
            </div>
            <button
              type="button"
              onClick={loadLanguages}
              className="flex items-center gap-2 rounded-md border border-zinc-700 px-3 py-2 text-sm text-zinc-200 hover:bg-zinc-800"
            >
              <RefreshCw className="h-4 w-4" />
              Languages
            </button>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="block text-sm text-zinc-300">
              Title
              <input
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="Optional document title"
                className="mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-white outline-none focus:border-sky-400"
              />
            </label>
            <label className="block text-sm text-zinc-300">
              Subject
              <input
                value={subject}
                onChange={(event) => setSubject(event.target.value)}
                placeholder="Optional subject/category"
                className="mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-white outline-none focus:border-sky-400"
              />
            </label>
            <label className="block text-sm text-zinc-300">
              Source language
              <select
                value={sourceLanguageId}
                onChange={(event) => setSourceLanguageId(Number(event.target.value))}
                className="mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-white outline-none focus:border-sky-400"
              >
                {languages.map((language) => (
                  <option key={language.id} value={language.id}>{language.name}</option>
                ))}
              </select>
            </label>
            <label className="block text-sm text-zinc-300">
              Target language
              <select
                value={targetLanguageId}
                onChange={(event) => setTargetLanguageId(Number(event.target.value))}
                className="mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-white outline-none focus:border-sky-400"
              >
                {languages.map((language) => (
                  <option key={language.id} value={language.id}>{language.name}</option>
                ))}
              </select>
            </label>
            <label className="block text-sm text-zinc-300">
              First content page
              <input
                type="number"
                min={1}
                value={firstContentPage}
                onChange={(event) => setFirstContentPage(Number(event.target.value))}
                className="mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-white outline-none focus:border-sky-400"
              />
            </label>
            <label className="block text-sm text-zinc-300">
              Output format
              <select
                value={outputFormat}
                onChange={(event) => setOutputFormat(event.target.value)}
                className="mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-white outline-none focus:border-sky-400"
              >
                {outputFormats.map((format) => (
                  <option key={format} value={format}>{format.toUpperCase()}</option>
                ))}
              </select>
            </label>
          </div>

          <div className="mt-4 rounded-lg border border-dashed border-zinc-700 bg-zinc-950 p-4">
            <label className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-md px-4 py-6 text-center hover:bg-zinc-900">
              <Upload className="h-8 w-8 text-zinc-400" />
              <span className="text-sm font-medium text-zinc-200">
                {file ? file.name : "Choose PDF, DOC, or DOCX"}
              </span>
              <span className="text-xs text-zinc-500">Large files are processed in the background.</span>
              <input
                type="file"
                accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                className="hidden"
                onChange={(event) => setFile(event.target.files?.[0] || null)}
              />
            </label>
          </div>

          {(message || error) && (
            <div className={clsx("mt-4 rounded-md border px-3 py-2 text-sm", error ? "border-red-500/40 bg-red-500/10 text-red-200" : "border-emerald-500/40 bg-emerald-500/10 text-emerald-200")}>
              {error || message}
            </div>
          )}

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <button
              type="button"
              onClick={uploadDocument}
              disabled={busy || !file}
              className="flex items-center justify-center gap-2 rounded-md bg-sky-500 px-3 py-2 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
              Upload
            </button>
            <button
              type="button"
              onClick={startTranslation}
              disabled={busy || !book}
              className="flex items-center justify-center gap-2 rounded-md bg-emerald-500 px-3 py-2 text-sm font-semibold text-zinc-950 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Languages className="h-4 w-4" />
              Translate
            </button>
            <button
              type="button"
              onClick={downloadTranslation}
              disabled={!translation?.translation_id || (jobStatus?.status !== "done" && translation.status !== "done")}
              className="flex items-center justify-center gap-2 rounded-md border border-zinc-700 px-3 py-2 text-sm font-semibold text-zinc-100 transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Download className="h-4 w-4" />
              Download
            </button>
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <StatusCard label="Uploaded document" value={book?.title || "None"} detail={book?.id} />
            <StatusCard label="Target" value={targetLanguage?.name || "Select language"} detail={translation?.translation_id} />
            <StatusCard label="Job status" value={jobStatus?.status || translation?.status || "Not started"} detail={jobStatus?.error_message || jobStatus?.completed_at || translation?.task_id} />
          </div>
        </section>
      </div>
    </div>
  );
};

const StatusCard = ({ label, value, detail }: { label: string; value: string; detail?: string | null }) => (
  <div className="min-h-24 rounded-lg border border-zinc-800 bg-zinc-950 p-3">
    <div className="text-xs uppercase tracking-wide text-zinc-500">{label}</div>
    <div className="mt-2 break-words text-sm font-semibold text-zinc-100">{value}</div>
    {detail && <div className="mt-2 break-all text-xs text-zinc-500">{detail}</div>}
  </div>
);
