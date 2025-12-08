"""
App package initialization and compatibility shims.
"""

try:
    import huggingface_hub
    from huggingface_hub import hf_hub_download
    from urllib.parse import urlparse, unquote

    def _parse_hf_url(url: str):
        parsed = urlparse(url)
        parts = [unquote(p) for p in parsed.path.lstrip("/").split("/")]
        if "resolve" not in parts:
            raise ValueError(f"Unsupported hub URL format: {url}")
        idx = parts.index("resolve")
        repo_id = "/".join(parts[:idx])
        revision = parts[idx + 1]
        filename = "/".join(parts[idx + 2 :])
        return repo_id, revision, filename

    if not hasattr(huggingface_hub, "cached_download"):

        def cached_download(
            url: str,
            cache_dir: str | None = None,
            force_filename: str | None = None,
            force_download: bool = False,
            resume_download: bool = False,
            proxies=None,
            local_files_only: bool = False,
            use_auth_token=None,
            user_agent: str | None = None,
            **_,
        ):
            repo_id, revision, filename = _parse_hf_url(url)
            return hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                revision=revision,
                cache_dir=cache_dir,
                force_filename=force_filename,
                force_download=force_download,
                resume_download=resume_download,
                proxies=proxies,
                local_files_only=local_files_only,
                use_auth_token=use_auth_token,
                user_agent=user_agent,
            )

        huggingface_hub.cached_download = cached_download
except Exception:
    # Fallback silently; if huggingface_hub isn't available yet the concrete import
    # (e.g. sentence-transformers) will raise its own error later.
    pass

