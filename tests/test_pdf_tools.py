import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import pymupdf

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/pdf_tools.py"


class PDFToolsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ai-study-pdf-")
        self.root = Path(self.temp.name)
        self.source = self.root / "source.pdf"
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((60, 80), "The object moves from x=1 to x=3.")
        page.insert_text((60, 110), "Repeat me.")
        page.insert_text((60, 140), "Repeat me.")
        page.insert_text((60, 180), "This quote spans")
        page.insert_text((60, 195), "two separate lines.")
        page = doc.new_page()
        page.insert_text((60, 80), "Second page with a distinct statement.")
        doc.save(self.source)
        doc.close()
        self.digest = hashlib.sha256(self.source.read_bytes()).hexdigest()

    def tearDown(self):
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), self.digest)
        self.temp.cleanup()

    def run_tool(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, encoding="utf-8")
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def notes(self, items):
        path = self.root / "notes.json"
        path.write_text(json.dumps({"annotations": items}, ensure_ascii=False), encoding="utf-8")
        return path

    def test_extract_selected_page_and_render(self):
        out = self.root / "extract"
        self.run_tool("extract", self.source, "--out", out, "--pages", "2", "--render", "--dpi", 72)
        data = json.loads((out / "source.json").read_text(encoding="utf-8"))
        self.assertEqual(data["selected_pages"], [2])
        self.assertEqual(data["sha256"], self.digest)
        self.assertIn("Second page", (out / "text.md").read_text())
        self.assertNotIn("The object moves", (out / "text.md").read_text())
        self.assertTrue((out / "assets/page-002.png").is_file())

    def test_annotations_unicode_multiline_and_visible_notes(self):
        comment = "这里的位移是物体的移动距离，不是关节角度。"
        notes = self.notes([{"page": 1, "quote": "The object moves from x=1 to x=3.", "comment": comment},
                            {"page": 1, "quote": "This quote spans two separate lines.", "comment": "跨行短句也应定位。", "kind": "notice"}])
        out = self.root / "annotated.pdf"
        self.run_tool("annotate", self.source, "--notes", notes, "--out", out)
        with pymupdf.open(out) as doc:
            self.assertEqual(len(doc), 3)
            page = doc[0]  # Keep the parent page alive while inspecting annotations.
            annots = list(page.annots())
            self.assertEqual(len(annots), 2)
            self.assertEqual(annots[0].info["content"], comment)
            self.assertIn("位移", doc[2].get_text())
        report = json.loads(out.with_suffix(".annotations.json").read_text(encoding="utf-8"))
        self.assertEqual(report["annotation_count"], 2)

    def test_unknown_quote_writes_no_output(self):
        notes = self.notes([{"page": 1, "quote": "Not present in the source", "comment": "不能错标"}])
        out = self.root / "bad.pdf"
        self.run_tool("annotate", self.source, "--notes", notes, "--out", out, ok=False)
        self.assertFalse(out.exists())
        self.assertFalse(out.with_suffix(".annotations.json").exists())

    def test_repeated_quote_requires_explicit_occurrence(self):
        item = {"page": 1, "quote": "Repeat me.", "comment": "选第二处"}
        out = self.root / "repeat.pdf"
        self.run_tool("annotate", self.source, "--notes", self.notes([item]), "--out", out, ok=False)
        self.assertFalse(out.exists())
        item["occurrence"] = 2
        self.run_tool("annotate", self.source, "--notes", self.notes([item]), "--out", out, "--no-notes-pages")
        with pymupdf.open(out) as doc:
            self.assertEqual(len(doc), 2)
            page = doc[0]
            annots = list(page.annots())
            self.assertEqual(len(annots), 1)
            self.assertGreater(annots[0].rect.y0, 120)

    def test_long_chinese_notes_paginate(self):
        comment = "长说明需要分页，不能裁掉内容。" * 220
        notes = self.notes([{"page": 1, "quote": "The object moves", "comment": comment}])
        out = self.root / "long.pdf"
        self.run_tool("annotate", self.source, "--notes", notes, "--out", out)
        with pymupdf.open(out) as doc:
            self.assertGreater(len(doc), 3)
            self.assertIn("裁掉内容", doc[-1].get_text())

    def test_crop_and_invalid_pages(self):
        out = self.root / "crop.png"
        self.run_tool("crop", self.source, "--page", 1, "--rect", 50, 50, 250, 150, "--dpi", 72, "--out", out)
        image = pymupdf.Pixmap(out)
        self.assertEqual((image.width, image.height), (200, 100))
        self.run_tool("extract", self.source, "--pages", "0", "--out", self.root / "invalid", ok=False)
        self.assertFalse((self.root / "invalid").exists())


if __name__ == "__main__":
    unittest.main()
