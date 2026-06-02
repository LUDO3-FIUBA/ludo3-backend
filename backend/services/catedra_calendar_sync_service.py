import json
import logging
import os
import re
from datetime import date
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests

from backend.models.catedra_calendar_entry import CatedraCalendarEntry
from backend.models.semester import Semester

logger = logging.getLogger(__name__)

_SHEETS_EXPORT_RE = re.compile(
    r'https://docs\.google\.com/spreadsheets/d/([^/]+)'
)

GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_MODEL = 'llama-3.3-70b-versatile'

PARSE_PROMPT = """
Tenés una tabla CSV que representa el calendario de una cátedra universitaria.
Tu tarea es convertir cada fila en un objeto JSON con este esquema:

{
  "date": "YYYY-MM-DD",          // fecha de la clase o evento; si no tiene fecha ignorá la fila
  "class_number": 1,             // número de clase si está explícito, sino null
  "topic": "Nombre del tema",    // tema principal de la clase o evento
  "entry_type": "class",         // uno de: class, tp_delivery, exam, holiday, other
  "links": [                     // lista de links encontrados en la fila, puede estar vacía
    {"label": "Paper X", "url": "https://..."}
  ],
  "notes": ""                    // texto adicional (lecturas, autores, etc.) sin los links
}

Reglas:
- Si una fila es un feriado o día sin clase, usá entry_type "holiday" y topic descriptivo.
- Si es entrega de TP, usá entry_type "tp_delivery".
- Si es parcial o examen, usá entry_type "exam".
- Ignorá filas de encabezado o sin fecha.
- Devolvé SOLO un array JSON válido, sin texto adicional, sin markdown.

CSV:
"""


def _sheets_to_csv_url(url: str) -> str:
    """Convierte una URL de Google Sheets (cualquier formato) a URL de export CSV."""
    m = _SHEETS_EXPORT_RE.match(url)
    if not m:
        raise ValueError(f"La URL no parece ser de Google Sheets: {url}")
    sheet_id = m.group(1)
    parsed = urlparse(url)
    fragment = parsed.fragment
    gid_match = re.search(r'gid=(\d+)', url + '#' + fragment)
    gid = gid_match.group(1) if gid_match else '0'
    return f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'


def _fetch_csv(url: str) -> str:
    csv_url = _sheets_to_csv_url(url)
    resp = requests.get(csv_url, timeout=15)
    resp.raise_for_status()
    try:
        return resp.content.decode('utf-8-sig')
    except UnicodeDecodeError:
        return resp.content.decode('latin-1')


_MOCK_ENTRIES = [
    {"date": str(date.today().replace(day=1)), "class_number": 1, "topic": "Introducción y RPC", "entry_type": "class", "links": [{"label": "Saltzer y Kaashoek (2009)", "url": "https://example.com/paper1"}], "notes": "Lecturas: 2.1, 4.1 y 4.2"},
    {"date": str(date.today().replace(day=8)), "class_number": 2, "topic": "MapReduce", "entry_type": "class", "links": [{"label": "MapReduce - Dean", "url": "https://example.com/paper2"}], "notes": ""},
    {"date": str(date.today().replace(day=15)), "class_number": 3, "topic": "TP1 MapReduce — enunciado", "entry_type": "tp_delivery", "links": [], "notes": "Entrega y presentación"},
    {"date": str(date.today().replace(day=22)), "class_number": 4, "topic": "Replicación y Sharding", "entry_type": "class", "links": [{"label": "The Log - Kreps", "url": "https://example.com/paper3"}], "notes": "Capítulo 5, pp. 152–161"},
]


def _parse_with_groq(csv_text: str, api_key: str, year: int) -> List[Dict]:
    import time

    lines = csv_text.splitlines()
    truncated = '\n'.join(lines[:300])

    year_hint = f'IMPORTANTE: Las fechas sin año explícito corresponden al año {year}.\n\n'
    payload = {
        'model': GROQ_MODEL,
        'messages': [
            {'role': 'user', 'content': PARSE_PROMPT + year_hint + truncated}
        ],
        'temperature': 0,
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    for attempt in range(3):
        resp = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=60)
        if resp.status_code == 429:
            wait = 10 * (attempt + 1)
            logger.warning(f'Groq rate limit, reintentando en {wait}s (intento {attempt + 1}/3)')
            time.sleep(wait)
            continue
        resp.raise_for_status()
        break
    else:
        resp.raise_for_status()

    content = resp.json()['choices'][0]['message']['content'].strip()

    if content.startswith('```'):
        content = re.sub(r'^```[a-z]*\n?', '', content)
        content = re.sub(r'\n?```$', '', content)

    return json.loads(content)


def _normalize_entry(raw: Dict, semester: Semester) -> Optional[CatedraCalendarEntry]:
    date_str = raw.get('date', '').strip()
    if not date_str:
        return None
    try:
        entry_date = date.fromisoformat(date_str)
    except ValueError:
        return None

    entry_type = raw.get('entry_type', 'class')
    if entry_type not in CatedraCalendarEntry.EntryType.values:
        entry_type = CatedraCalendarEntry.EntryType.OTHER

    links = raw.get('links', [])
    if not isinstance(links, list):
        links = []

    return CatedraCalendarEntry(
        semester=semester,
        date=entry_date,
        class_number=raw.get('class_number'),
        topic=(raw.get('topic') or '').strip()[:500],
        entry_type=entry_type,
        links=links,
        notes=(raw.get('notes') or '').strip(),
    )


def sync_catedra_calendar(semester: Semester) -> int:
    """
    Fetchea el Google Sheets del semestre, parsea con Groq (Llama) y actualiza
    los CatedraCalendarEntry. Devuelve la cantidad de entradas creadas.
    Sin GROQ_API_KEY usa datos de prueba y omite el fetch.
    """
    if not semester.calendar_source_url:
        raise ValueError('El semestre no tiene una URL de calendario configurada')

    api_key = os.environ.get('GROQ_API_KEY', '')
    if not api_key:
        logger.warning('GROQ_API_KEY no configurada — usando datos de prueba (sin fetch)')
        raw_entries = _MOCK_ENTRIES
    else:
        csv_text = _fetch_csv(semester.calendar_source_url)
        year = semester.start_date.year if semester.start_date else date.today().year
        raw_entries = _parse_with_groq(csv_text, api_key, year)

    entries = [_normalize_entry(r, semester) for r in raw_entries]
    entries = [e for e in entries if e is not None]

    from django.db import transaction

    with transaction.atomic():
        CatedraCalendarEntry.objects.filter(semester=semester).delete()
        CatedraCalendarEntry.objects.bulk_create(entries)

    return len(entries)
