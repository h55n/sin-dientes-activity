"""Check the word-list import callback with and without a selected file."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk  # noqa: E402

from activity import Sindiente  # noqa: E402


class ImportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chooser = Gtk.FileChooserWidget()

    @classmethod
    def tearDownClass(cls):
        cls.chooser.destroy()

    def setUp(self):
        self.target = SimpleNamespace(archivo=self.chooser, combo=Mock(),
                                      nivel=4, sugar_data='/unused/')

    def test_no_selection_does_not_import_or_change_level(self):
        self.assertIsNone(self.chooser.get_uri())
        with patch('activity.utils.importar_lista_p') as importer:
            Sindiente._importar_archivo_cb(self.target, None)
        importer.assert_not_called()
        self.target.combo.get_active.assert_not_called()
        self.assertEqual(self.target.nivel, 4)

    def test_selected_file_and_category_are_passed_to_importer(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / 'words.palabra'
            filename.write_text('hola:saludo:pista\n')
            self.chooser.set_filename(str(filename))
            while Gtk.events_pending():
                Gtk.main_iteration()
            self.assertEqual(self.chooser.get_uri(), filename.as_uri())
            self.target.combo.get_active.return_value = 7
            with patch('activity.utils.importar_lista_p') as importer:
                Sindiente._importar_archivo_cb(self.target, None)
            importer.assert_called_once_with('/unused/', str(filename), 7)

    def test_selected_word_list_is_written_to_custom_category(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory) / 'words.palabra'
            content = 'Prueba\nsol:estrella:luz\n'
            filename.write_text(content)
            self.chooser.set_filename(str(filename))
            while Gtk.events_pending():
                Gtk.main_iteration()
            self.target.sugar_data = directory + '/'
            self.target.combo.get_active.return_value = 7
            Sindiente._importar_archivo_cb(self.target, None)
            self.assertEqual((Path(directory) / 'nivel8.palabra').read_text(),
                             content)


if __name__ == '__main__':
    unittest.main()
