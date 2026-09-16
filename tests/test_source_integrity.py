"""Ensure the standalone adaptation retains the authoritative implementation."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class SourceIntegrityTests(unittest.TestCase):
    def test_authoritative_implementation_is_preserved(self):
        manifest = json.loads((ROOT/'docs/source-provenance.json').read_text())
        for name, digest in manifest['preserved_sha256'].items():
            with self.subTest(file=name):
                self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), digest)

    def test_public_brand_and_compatible_identity(self):
        plugin = json.loads((ROOT/'package/metadata.json').read_text())['KPlugin']
        self.assertEqual(plugin['Name'], 'Plasma Flow')
        self.assertEqual(plugin['Id'], 'org.kde.plasma.virtualdesktopbar')
        self.assertEqual(plugin['Version'], '0.1.1')
        self.assertEqual([author['Name'] for author in plugin['Authors']], ['Lenon Kitchens','wsdfhjxc'])

    def test_dynamic_manager_is_not_bound_to_filtered_display_model(self):
        container = (ROOT/'package/contents/ui/Container.qml').read_text()
        self.assertIn('backend.configureDynamicDesktops', container)
        self.assertNotIn('function manageDynamicDesktops', container)
        script = (ROOT/'plugin/dynamic/reconcile.js').read_text()
        self.assertIn('workspace.windowList()', script)
        self.assertNotIn('FilterByScreen', script)

if __name__ == '__main__':
    unittest.main()
