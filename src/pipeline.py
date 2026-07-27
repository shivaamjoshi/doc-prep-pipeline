# src/pipeline.py
import json
import os
from pathlib import Path

from src.parse import parse_pdf
from src.chunk import fixed_size_chunk


def is_low_signal_table(text: str, numeric_word_ratio_threshold: float = 0.2) -> bool:
    words = text.split()
    if not words:
        return True
    numeric_words = sum(w.isdigit() for w in words)
    ratio = numeric_words / len(words)
    return ratio > numeric_word_ratio_threshold


def process_document(pdf_path: str, chunk_size: int = 200, overlap: int = 40) -> list[dict]:
    """
    Full pipeline for one PDF: parse -> filter noisy tables -> chunk.
    Returns a flat list of chunk records ready to write out.
    """
    elements = parse_pdf(pdf_path)

    records = []
    for el in elements:
        # Drop noisy tables (e.g. mangled tables of contents)
        if el["category"] == "Table" and is_low_signal_table(el["text"]):
            continue

        # Skip near-empty elements (stray Titles, Images with no text, etc.)
        if len(el["text"].split()) < 3:
            continue

        chunks = fixed_size_chunk(el["text"], size=chunk_size, overlap=overlap)

        for i, chunk_text in enumerate(chunks):
            records.append({
                "text": chunk_text,
                "source": el["source"],
                "page": el["page"],
                "category": el["category"],
                "chunk_index": i,
            })

    return records


def run_pipeline(raw_dir: str = "data/raw", out_dir: str = "data/processed"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    pdf_files = [f for f in os.listdir(raw_dir) if f.endswith(".pdf")]
    print(f"Found {len(pdf_files)} PDF(s) in {raw_dir}")

    all_records = []
    for filename in pdf_files:
        pdf_path = os.path.join(raw_dir, filename)
        print(f"Processing {filename}...")
        records = process_document(pdf_path)
        print(f"  -> {len(records)} chunks")
        all_records.extend(records)

    out_path = os.path.join(out_dir, "chunks.json")
    with open(out_path, "w") as f:
        json.dump(all_records, f, indent=2)

    print(f"\nTotal chunks: {len(all_records)}")
    print(f"Written to: {out_path}")


if __name__ == "__main__":
    run_pipeline()