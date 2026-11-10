import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from polypangf.outputs import export_result
from polypangf.privacy import PortableText


class PrivacyTests(unittest.TestCase):
    def test_portable_export_and_checksums(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "results"
            stage = root / "report"
            stage.mkdir(parents=True)
            original = json.dumps({"fingerprint": {"parameters": {"_base": temporary}, "inputs": {}}, "hostname": "private-host", "path": str(stage)})
            (stage / "state.json").write_text(original)
            (stage / "report.html").write_text('<h1>Report</h1><img src="../plot/a.png"> https://example.org/docs')
            (stage / "genes.tsv").write_text("gene\n/gene/one\n")
            archive = Path(temporary) / "export.zip"
            export_result(root, archive)
            self.assertEqual((stage / "state.json").read_text(), original)
            with zipfile.ZipFile(archive) as output:
                state = output.read("report/state.json").decode()
                self.assertNotIn(temporary, state)
                self.assertNotIn("private-host", state)
                html = output.read("report/report.html").decode()
                self.assertIn("</h1>", html)
                self.assertIn("../plot/a.png", html)
                self.assertIn("https://example.org/docs", html)
                self.assertEqual(output.read("report/genes.tsv"), b"gene\n/gene/one\n")
                for line in output.read("EXPORT_SHA256SUMS.txt").decode().splitlines():
                    expected, name = line.split("  ", 1)
                    self.assertEqual(hashlib.sha256(output.read(name)).hexdigest(), expected)

    def test_virtual_examples_and_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            portable = PortableText(temporary)
            data = portable.bytes(b'{"username":"private-user","input":"/fictional/private/data.fa","example":"/path/to/data.fa"}')
            self.assertNotIn(b"private", data)
            self.assertIn(b"/path/to/data.fa", data)


if __name__ == "__main__":
    unittest.main()

