# cabbageclaw-neuro-daily-web

GitHub Pages dashboard for `cabbageland/cabbageclaw-neuro-daily`.

## What it does

- shows the latest neuro digest
- browses recent daily digests
- browses paper notes
- filters note cards by verdict
- links back to the source markdown in the neuro-daily repo
- works as a simple static site suitable for GitHub Pages

## Structure

- `index.html` — site shell
- `styles.css` — UI styling
- `app.js` — client-side rendering
- `build_content.py` — generates `data/content.json` from the local `cabbageclaw-neuro-daily` repo
- `data/content.json` — generated content snapshot

## Audio assets

Generated audio files are committed to this repo because they are part of the published site output.

Piper voice model binaries are no longer intended to live in this repo long term. The audio pipeline in the sibling `cabbageclaw-neuro-daily` repo now resolves voices from a shared local cache at `~/.cache/piper-voices/` and auto-downloads them there if missing.

## Publishing on GitHub Pages

This repo is designed to work as a plain static site.

Typical setup:

1. Push to `main`
2. In GitHub repo settings, enable **Pages**
3. Set source to **Deploy from branch**
4. Branch: `main`, folder: `/ (root)`

## Refreshing content

Rebuild the JSON snapshot from the workspace copy of `cabbageclaw-neuro-daily`:

```bash
python3 build_content.py
```

A later improvement is to automate this refresh after each neuro-daily push.
