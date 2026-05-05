import type { FC } from "react";
import { useState, useRef, useCallback } from "react";
import { Mic, MicOff, Volume2, VolumeX } from "lucide-react";
import clsx from "clsx";

interface VoiceRecorderProps {
  onTranscript: (text: string) => void;
  language: string;
  disabled?: boolean;
}

export const VoiceRecorder: FC<VoiceRecorderProps> = ({ onTranscript, language, disabled }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        await processAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Failed to start recording:", error);
      alert("Microphone access denied. Please allow microphone access.");
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsProcessing(true);
    }
  }, [isRecording]);

  const processAudio = async (audioBlob: Blob) => {
    try {
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64Audio = (reader.result as string).split(',')[1];
        
        // Send to WebSocket for realtime transcription
        const ws = new WebSocket(`ws://localhost:8001/api/ws/transcribe`);
        
        ws.onopen = () => {
          ws.send(JSON.stringify({
            audio: base64Audio,
            language: language === 'english' ? 'en' : language === 'swahili' ? 'sw' : undefined
          }));
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if (data.text) {
            onTranscript(data.text);
          }
          setIsProcessing(false);
          ws.close();
        };

        ws.onerror = () => {
          setIsProcessing(false);
          // Fallback: try REST API
          transcribeViaREST(audioBlob);
        };
      };
      reader.readAsDataURL(audioBlob);
    } catch (error) {
      console.error("Audio processing failed:", error);
      setIsProcessing(false);
    }
  };

  const transcribeViaREST = async (audioBlob: Blob) => {
    // Fallback to REST API if WebSocket fails
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    
    try {
      const response = await fetch('http://localhost:8001/api/voice/transcribe', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (data.text) {
        onTranscript(data.text);
      }
    } catch (error) {
      console.error("REST transcription failed:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <button
      type="button"
      onClick={isRecording ? stopRecording : startRecording}
      disabled={disabled || isProcessing}
      className={clsx(
        "flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg transition",
        isRecording 
          ? "bg-red-500 text-white animate-pulse" 
          : "text-white/60 hover:bg-white/10 hover:text-white/80",
        (disabled || isProcessing) && "opacity-40 cursor-not-allowed"
      )}
      title={isRecording ? "Stop recording" : "Start voice input"}
    >
      {isProcessing ? (
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/60 border-t-transparent" />
      ) : isRecording ? (
        <MicOff className="h-4 w-4" />
      ) : (
        <Mic className="h-4 w-4" />
      )}
    </button>
  );
};
