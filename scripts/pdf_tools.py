#!/usr/bin/env python3
"""Local PDF extraction, cropping and grounded Chinese annotations."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import textwrap

try:
    import pymupdf as pdf
except ImportError:
    raise SystemExit("Missing PyMuPDF. Run: python -m pip install -r requirements.txt")


def new_output(value, source=None):
    path = Path(value).expanduser().resolve()
    if source and path == Path(source).resolve():
        raise ValueError("Output must differ from the original PDF")
    if path.exists():
        raise ValueError(f"Output already exists: {path}. Choose a new path.")
    return path


def page_number(value, count):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= count:
        raise ValueError(f"Page must be an integer from 1 to {count}: {value}")
    return value - 1


def selected_pages(spec, count):
    if not spec:
        return list(range(count))
    result = set()
    for part in spec.split(","):
        bounds = part.strip().split("-")
        if len(bounds) > 2:
            raise ValueError(f"Invalid page range: {part}")
        start = int(bounds[0])
        end = int(bounds[-1])
        if start > end:
            raise ValueError(f"Reversed page range: {part}")
        page_number(start, count)
        page_number(end, count)
        result.update(range(start - 1, end))
    return sorted(result)


def rect_on_page(values, page):
    if not isinstance(values, (list, tuple)) or len(values) != 4:
        raise ValueError("rect must contain four PDF coordinates: x0,y0,x1,y1")
    rect = pdf.Rect(values)
    if rect.is_empty or rect.is_infinite or not page.rect.contains(rect):
        raise ValueError(f"Rectangle must be non-empty and inside page {page.number + 1}")
    return rect


def extract(args):
    source = Path(args.pdf).resolve()
    out = new_output(args.out)
    with pdf.open(source) as doc:
        pages = selected_pages(args.pages, len(doc))
        data = {"source_name": source.name, "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "page_count": len(doc), "selected_pages": [p + 1 for p in pages],
                "metadata": doc.metadata, "pages": [], "images": []}
        out.mkdir(parents=True)
        if args.render or args.images:
            (out / "assets").mkdir()
        markdown = [f"# {source.name}\n", "Extracted PDF text; check page images for layout and formulas.\n"]
        seen_images = set()
        for index in pages:
            page = doc[index]
            content = page.get_text("text")
            data["pages"].append({"page": index + 1, "width": page.rect.width,
                                  "height": page.rect.height, "rotation": page.rotation,
                                  "text": content, "text_layer_sparse": len(content.strip()) < 30,
                                  "blocks": [{"rect": list(b[:4]), "text": b[4]}
                                             for b in page.get_text("blocks") if b[6] == 0]})
            markdown.append(f"\n## PDF page {index + 1}\n\n{content}\n")
            if args.render:
                page.get_pixmap(dpi=args.dpi).save(out / "assets" / f"page-{index + 1:03}.png")
            if args.images:
                for entry in page.get_images(full=True):
                    xref = entry[0]
                    if xref in seen_images:
                        continue
                    seen_images.add(xref)
                    image = doc.extract_image(xref)
                    if not image:
                        continue
                    filename = f"page-{index + 1:03}-image-{xref}.{image['ext']}"
                    (out / "assets" / filename).write_bytes(image["image"])
                    data["images"].append({"page": index + 1, "xref": xref, "file": "assets/" + filename})
        (out / "text.md").write_text("\n".join(markdown), encoding="utf-8")
        (out / "source.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Extracted {len(pages)}/{data['page_count']} pages to {out}")
    sparse = [p["page"] for p in data["pages"] if p["text_layer_sparse"]]
    if sparse:
        print(f"Sparse text layer on pages {sparse}; use rendered pages or an OCR tool. This command does not run OCR.")


def crop(args):
    out = new_output(args.out, args.pdf)
    if out.suffix.lower() != ".png":
        raise ValueError("Crop output must end in .png")
    with pdf.open(args.pdf) as doc:
        page = doc[page_number(args.page, len(doc))]
        if page.rotation:
            raise ValueError("Crop currently requires a page with rotation 0")
        rect = rect_on_page(args.rect, page)
        out.parent.mkdir(parents=True, exist_ok=True)
        page.get_pixmap(dpi=args.dpi, clip=rect).save(out)
    print(f"Cropped PDF page {args.page} to {out}")


def locate(item, page):
    quote = item.get("quote")
    if quote and "rect" in item:
        raise ValueError("Use quote or rect, not both")
    if "rect" in item:
        if page.rotation:
            raise ValueError("Coordinate annotations currently require rotation 0; use quote instead")
        return [rect_on_page(item["rect"], page)]
    if not isinstance(quote, str) or not quote.strip():
        raise ValueError("Each annotation needs a non-empty quote or explicit rect")
    normalized = " ".join(quote.split())
    count = " ".join(page.get_text().split()).casefold().count(normalized.casefold())
    hits = page.search_for(quote, quads=True)
    if not count or not hits:
        raise ValueError(f"Quote not found on PDF page {page.number + 1}: {quote!r}")
    if count == 1:
        if "occurrence" in item and item["occurrence"] != 1:
            raise ValueError("Only one occurrence exists")
        return hits
    occurrence = item.get("occurrence")
    if isinstance(occurrence, bool) or not isinstance(occurrence, int) or not 1 <= occurrence <= count:
        raise ValueError(f"Quote appears {count} times on page {page.number + 1}; specify occurrence (1-based)")
    if len(hits) != count:
        raise ValueError("Repeated multiline quote: use a longer unique quote or explicit rect")
    return [hits[occurrence - 1]]


def notes_pages(doc, records):
    """Visible companion pages make Chinese comments readable without popup support."""
    first = len(doc)
    lines = []
    for i, item in enumerate(records, 1):
        lines.append(f"{i}. 原文第 {item['page']} 页 / {item['kind']}")
        if item.get("quote"):
            lines.extend(textwrap.wrap("原文：" + item["quote"], width=42))
        for paragraph in item["comment"].splitlines():
            lines.extend(textwrap.wrap(paragraph, width=42) or [""])
        lines.append("")
    for offset in range(0, len(lines), 44):
        page = doc.new_page(width=595, height=842)
        draw_mixed_line(page, 48, 45, "AI Paper Study / 中文阅读批注", 15)
        for n, line in enumerate(lines[offset:offset + 44]):
            draw_mixed_line(page, 48, 78 + n * 16, line, 11)
        page.insert_text((48, 815), f"Notes {len(doc) - first}", fontsize=9)
    return len(doc) - first


def draw_mixed_line(page, x, y, text, size):
    for run in re.findall(r"[\x20-\x7e]+|[^\x20-\x7e]+", text):
        font = "helv" if run.isascii() else "china-s"
        page.insert_text((x, y), run, fontname=font, fontsize=size)
        x += pdf.get_text_length(run, fontname=font, fontsize=size)


def annotate(args):
    source = Path(args.pdf).resolve()
    out = new_output(args.out, source)
    if out.suffix.lower() != ".pdf":
        raise ValueError("Annotated output must end in .pdf")
    report = new_output(out.with_suffix(".annotations.json"), source)
    payload = json.loads(Path(args.notes).read_text(encoding="utf-8-sig"))
    items = payload.get("annotations") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items:
        raise ValueError("Notes JSON must contain a non-empty annotations array")
    colors = {"explain": (1, .87, .2), "question": (1, .55, .55), "notice": (.4, .8, 1)}
    with pdf.open(source) as doc:
        original_count = len(doc)
        planned = []
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Annotation must be a JSON object")
            index = page_number(item.get("page"), original_count)
            comment = item.get("comment")
            if not isinstance(comment, str) or not comment.strip():
                raise ValueError("Annotation comment must be a non-empty string")
            kind = item.get("kind", "explain")
            if kind not in colors:
                raise ValueError("kind must be explain, question or notice")
            regions = locate(item, doc[index])
            planned.append((index, regions, {**item, "kind": kind}))
        # All anchors are validated before saving anything.
        for index, regions, item in planned:
            page = doc[index]
            annotation = page.add_highlight_annot(regions)
            annotation.set_info(title="AI Paper Study", subject=item["kind"], content=item["comment"])
            annotation.set_colors(stroke=colors[item["kind"]])
            annotation.update()
        extra = 0 if args.no_notes_pages else notes_pages(doc, [p[2] for p in planned])
        out.parent.mkdir(parents=True, exist_ok=True)
        doc.save(out, garbage=4, deflate=True)
    # Reopen to ensure comment content survived PDF serialization.
    with pdf.open(out) as check:
        contents = [a.info.get("content") for p in check for a in (p.annots() or [])]
        if any(item["comment"] not in contents for _, _, item in planned):
            raise RuntimeError("Annotation verification failed after saving")
    result = {"source_name": source.name, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "original_pages": original_count, "notes_pages_added": extra,
              "annotation_count": len(planned), "annotations": [p[2] for p in planned]}
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}: {len(planned)} annotations, {extra} visible notes pages")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    ex = sub.add_parser("extract", help="Extract paginated text, metadata and optional images")
    ex.add_argument("pdf")
    ex.add_argument("--out", required=True)
    ex.add_argument("--pages", help="1-based page selection, e.g. 1,3-5")
    ex.add_argument("--render", action="store_true", help="Render selected full pages as PNG")
    ex.add_argument("--images", action="store_true", help="Extract embedded images (not vector figures)")
    ex.add_argument("--dpi", type=int, default=140)
    ex.set_defaults(run=extract)
    cr = sub.add_parser("crop", help="Crop an original figure/table using page coordinates")
    cr.add_argument("pdf")
    cr.add_argument("--page", type=int, required=True)
    cr.add_argument("--rect", nargs=4, type=float, required=True)
    cr.add_argument("--out", required=True)
    cr.add_argument("--dpi", type=int, default=200)
    cr.set_defaults(run=crop)
    an = sub.add_parser("annotate", help="Highlight exact source quotes and attach Chinese comments")
    an.add_argument("pdf")
    an.add_argument("--notes", required=True, help="JSON annotation input")
    an.add_argument("--out", required=True)
    an.add_argument("--no-notes-pages", action="store_true", help="Keep only highlight popup comments")
    an.set_defaults(run=annotate)
    args = parser.parse_args()
    if hasattr(args, "dpi") and not 36 <= args.dpi <= 600:
        parser.error("dpi must be between 36 and 600")
    try:
        args.run(args)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
