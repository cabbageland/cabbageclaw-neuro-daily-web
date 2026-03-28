#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_REPO = ROOT.parent / 'cabbageclaw-neuro-daily'
OUT_PATH = ROOT / 'data' / 'content.json'
REPO_NAME = 'cabbageland/cabbageclaw-neuro-daily'


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8').replace('\r\n', '\n')


def extract_section(text: str, heading: str) -> str:
    pattern = rf'^## {re.escape(heading)}\n+(.*?)(?=^## |\Z)'
    m = re.search(pattern, text, flags=re.M | re.S)
    return m.group(1).strip() if m else ''


def extract_subsection(text: str, heading: str) -> str:
    pattern = rf'^### {re.escape(heading)}\n+(.*?)(?=^### |^## |\Z)'
    m = re.search(pattern, text, flags=re.M | re.S)
    return m.group(1).strip() if m else ''


def first_paragraph(text: str) -> str:
    parts = [p.strip() for p in re.split(r'\n\s*\n', text.strip()) if p.strip()]
    return parts[0] if parts else ''


def clean_md(text: str) -> str:
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'^[-*]\s+', '', text, flags=re.M)
    return text.strip()


def normalize_verdict(text: str) -> str:
    return re.sub(r'^\*+\s*', '', clean_md(text)).strip()


def parse_daily(path: Path) -> dict:
    text = read_text(path)
    date = path.stem
    theme = clean_md(extract_section(text, 'Theme'))
    overview = clean_md(extract_section(text, 'Short overview'))
    takeaway = clean_md(extract_section(text, 'One-paragraph takeaway'))
    top = clean_md(extract_section(text, 'Most relevant paper'))
    ranked = extract_section(text, 'Ranked list')
    ranked_titles = re.findall(r'^\d+\. \*\*(.*?)\*\*', ranked, flags=re.M)
    return {
        'slug': date,
        'date': date,
        'title': f'Neuro Daily — {date}',
        'theme': theme,
        'overview': overview,
        'takeaway': takeaway,
        'mostRelevantPaper': top.split('\n\n', 1)[0].strip(),
        'rankedTitles': ranked_titles,
        'path': f'daily_papers/{path.name}',
    }


def parse_note(path: Path) -> dict:
    text = read_text(path)
    title = clean_md(re.sub(r'^#\s+', '', text.splitlines()[0]).strip())

    def bullet(label: str) -> str:
        m = re.search(rf'^\* {re.escape(label)}:\s*(.+)$', text, flags=re.M)
        return clean_md(m.group(1).strip()) if m else ''

    quick = extract_section(text, 'Quick verdict')
    verdict_lines = [ln.strip() for ln in quick.splitlines() if ln.strip()]
    verdict = normalize_verdict(verdict_lines[0]) if verdict_lines else ''
    verdict_text = clean_md('\n'.join(verdict_lines[1:]).strip())
    overview = clean_md(extract_section(text, 'One-paragraph overview'))
    why_it_matters = clean_md(extract_subsection(text, '12. Why does this matter for cabbageland?'))
    final_decision = clean_md(extract_subsection(text, '14. Final decision'))
    return {
        'slug': path.stem,
        'title': title,
        'dateSurfaced': bullet('Date surfaced'),
        'year': bullet('Year'),
        'link': bullet('Link'),
        'venue': bullet('Venue / source'),
        'whySelected': bullet('Why selected in one sentence'),
        'verdict': verdict,
        'verdictText': verdict_text,
        'overview': overview,
        'whyItMatters': why_it_matters,
        'finalDecision': final_decision,
        'path': f'paper_notes/{path.name}',
    }


def parse_related(path: Path) -> dict:
    text = read_text(path)
    title = clean_md(re.sub(r'^#\s+', '', text.splitlines()[0]).strip())
    synthesis = clean_md(extract_section(text, 'Current synthesis'))
    overview = first_paragraph(synthesis or clean_md('\n'.join(text.splitlines()[1:])))
    return {
        'slug': path.stem,
        'title': title,
        'overview': overview,
        'path': f'related_work/{path.name}',
    }


def collect_markdown() -> dict[str, str]:
    markdown: dict[str, str] = {}
    for subdir in ('daily_papers', 'paper_notes', 'related_work'):
        base = SOURCE_REPO / subdir
        if not base.exists():
            continue
        for path in base.glob('*.md'):
            if path.name == '.gitkeep':
                continue
            markdown[f'{subdir}/{path.name}'] = read_text(path)
    return markdown


def collect_audio() -> dict[str, dict[str, str]]:
    audio = {
        'daily_papers/2026-03-27.md': {
            'label': 'Listen to digest',
            'scriptPath': 'audio_scripts/2026-03-27_digest_audio_script.md',
            'audioPath': 'audio/generated/2026-03-27_digest.wav',
        },
        'paper_notes/deep_learning_assisted_v1_circuit_simulation.md': {
            'label': 'Listen to reading notes',
            'scriptPath': 'audio_scripts/2026-03-27_reading_notes_audio_script.md',
            'audioPath': 'audio/generated/2026-03-27_reading_notes.wav',
        },
        'paper_notes/modular_bidirectional_implantable_interface.md': {
            'label': 'Listen to reading notes',
            'scriptPath': 'audio_scripts/2026-03-27_reading_notes_audio_script.md',
            'audioPath': 'audio/generated/2026-03-27_reading_notes.wav',
        },
    }
    return audio


def main() -> None:
    daily_dir = SOURCE_REPO / 'daily_papers'
    notes_dir = SOURCE_REPO / 'paper_notes'
    related_dir = SOURCE_REPO / 'related_work'

    digests = sorted(
        (parse_daily(p) for p in daily_dir.glob('*.md') if p.name != '.gitkeep'),
        key=lambda x: x['date'],
        reverse=True,
    )
    notes = sorted(
        (parse_note(p) for p in notes_dir.glob('*.md') if p.name != '.gitkeep'),
        key=lambda x: (x['dateSurfaced'], x['title']),
        reverse=True,
    )
    related = sorted(
        (parse_related(p) for p in related_dir.glob('*.md') if p.name != '.gitkeep'),
        key=lambda x: x['title'].lower(),
    )

    payload = {
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'repo': REPO_NAME,
        'digests': digests,
        'notes': notes,
        'related': related,
        'markdown': collect_markdown(),
        'audio': collect_audio(),
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'wrote {OUT_PATH}')


if __name__ == '__main__':
    main()
