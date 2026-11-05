"""Create a tiny fictional paper fragment and annotate it with Chinese teaching notes."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
import pymupdf
from pdf_tools import annotate, extract

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--out", required=True)
args = parser.parse_args()
out = Path(args.out).resolve()
out.mkdir(parents=True, exist_ok=True)
source = out / "teaching-source.pdf"
if source.exists():
    parser.error("Demo source exists; choose a fresh output directory")
with pymupdf.open() as doc:
    page = doc.new_page(width=595, height=842)
    page.insert_text((48, 60), "AI Paper Study - Teaching Fixture", fontsize=18)
    page.insert_text((48, 100), "This is a fictional teaching example, not a research paper.", fontsize=11)
    page.insert_text((48, 145), "The object moves from x=1 to x=3.", fontsize=12)
    page.insert_text((48, 180), "The action also depends on current robot state.", fontsize=12)
    doc.save(source)
notes = {"annotations": [
    {"page": 1, "quote": "The object moves from x=1 to x=3.", "kind": "explain", "comment": "这里描述的是物体位置从1到3，位移为2。它提供动作生成的运动参照，并不等于某个机器人关节应转动2度。"},
    {"page": 1, "quote": "The action also depends on current robot state.", "kind": "notice", "comment": "同样的物体移动目标，在不同机械臂姿态下可能需要不同的关节动作。所以动作分支还需要当前自身状态。"}
]}
notes_file = out / "notes.json"
notes_file.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
annotate(SimpleNamespace(pdf=str(source), notes=str(notes_file), out=str(out / "teaching-annotated.pdf"), no_notes_pages=False))
extract(SimpleNamespace(pdf=str(out / "teaching-annotated.pdf"), out=str(out / "preview"), pages=None, render=True, images=False, dpi=120))
