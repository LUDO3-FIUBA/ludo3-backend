from datetime import date, timezone, datetime
from unittest import mock

from django.test import SimpleTestCase, TestCase

from backend.services.catedra_calendar_sync_service import (
    _normalize_entry,
    _sheets_to_csv_url,
    sync_catedra_calendar,
)
from tests.factories import SemesterFactory


class SheetsToCSVUrlTests(SimpleTestCase):
    def test_basic_url_without_gid(self):
        url = 'https://docs.google.com/spreadsheets/d/ABC123/edit'
        result = _sheets_to_csv_url(url)
        self.assertEqual(result, 'https://docs.google.com/spreadsheets/d/ABC123/export?format=csv&gid=0')

    def test_url_with_gid_in_fragment(self):
        url = 'https://docs.google.com/spreadsheets/d/ABC123/edit#gid=456789'
        result = _sheets_to_csv_url(url)
        self.assertEqual(result, 'https://docs.google.com/spreadsheets/d/ABC123/export?format=csv&gid=456789')

    def test_url_with_gid_in_query(self):
        url = 'https://docs.google.com/spreadsheets/d/ABC123/edit?gid=999'
        result = _sheets_to_csv_url(url)
        self.assertEqual(result, 'https://docs.google.com/spreadsheets/d/ABC123/export?format=csv&gid=999')

    def test_invalid_url_raises(self):
        with self.assertRaises(ValueError):
            _sheets_to_csv_url('https://example.com/not-a-sheet')


class NormalizeEntryTests(TestCase):
    def setUp(self):
        self.semester = SemesterFactory()

    def test_valid_class_entry(self):
        raw = {
            'date': '2025-04-07',
            'class_number': 3,
            'topic': 'Introducción a RPC',
            'entry_type': 'class',
            'links': [{'label': 'Paper', 'url': 'https://example.com'}],
            'notes': 'Lectura obligatoria',
        }
        entry = _normalize_entry(raw, self.semester)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.date, date(2025, 4, 7))
        self.assertEqual(entry.class_number, 3)
        self.assertEqual(entry.topic, 'Introducción a RPC')
        self.assertEqual(entry.entry_type, 'class')
        self.assertEqual(entry.notes, 'Lectura obligatoria')

    def test_missing_date_returns_none(self):
        raw = {'date': '', 'topic': 'Sin fecha', 'entry_type': 'class', 'links': [], 'notes': ''}
        self.assertIsNone(_normalize_entry(raw, self.semester))

    def test_invalid_date_returns_none(self):
        raw = {'date': 'no-es-fecha', 'topic': 'Algo', 'entry_type': 'class', 'links': [], 'notes': ''}
        self.assertIsNone(_normalize_entry(raw, self.semester))

    def test_unknown_entry_type_defaults_to_other(self):
        raw = {'date': '2025-05-01', 'topic': 'Raro', 'entry_type': 'desconocido', 'links': [], 'notes': ''}
        entry = _normalize_entry(raw, self.semester)
        self.assertEqual(entry.entry_type, 'other')

    def test_links_not_a_list_defaults_to_empty(self):
        raw = {'date': '2025-05-01', 'topic': 'Algo', 'entry_type': 'class', 'links': 'no-es-lista', 'notes': ''}
        entry = _normalize_entry(raw, self.semester)
        self.assertEqual(entry.links, [])

    def test_topic_truncated_to_500_chars(self):
        raw = {'date': '2025-05-01', 'topic': 'x' * 600, 'entry_type': 'class', 'links': [], 'notes': ''}
        entry = _normalize_entry(raw, self.semester)
        self.assertEqual(len(entry.topic), 500)


class SyncCatedraCalendarTests(TestCase):
    def test_raises_if_no_calendar_url(self):
        semester = SemesterFactory(calendar_source_url=None)
        with self.assertRaises(ValueError):
            sync_catedra_calendar(semester)

    @mock.patch.dict('os.environ', {}, clear=True)
    def test_uses_mock_entries_without_groq_key(self):
        semester = SemesterFactory(
            calendar_source_url='https://docs.google.com/spreadsheets/d/ABC/edit',
            start_date=datetime(2025, 4, 1, tzinfo=timezone.utc),
        )
        count = sync_catedra_calendar(semester)
        self.assertGreater(count, 0)
        from backend.models.catedra_calendar_entry import CatedraCalendarEntry
        self.assertEqual(CatedraCalendarEntry.objects.filter(semester=semester).count(), count)

    @mock.patch.dict('os.environ', {}, clear=True)
    def test_sync_replaces_existing_entries(self):
        from backend.models.catedra_calendar_entry import CatedraCalendarEntry
        semester = SemesterFactory(
            calendar_source_url='https://docs.google.com/spreadsheets/d/ABC/edit',
            start_date=datetime(2025, 4, 1, tzinfo=timezone.utc),
        )
        sync_catedra_calendar(semester)
        first_count = CatedraCalendarEntry.objects.filter(semester=semester).count()
        sync_catedra_calendar(semester)
        second_count = CatedraCalendarEntry.objects.filter(semester=semester).count()
        self.assertEqual(first_count, second_count)
