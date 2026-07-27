# src/parse.py
from unstructured.partition.pdf import partition_pdf

def parse_pdf(path: str) -> list[dict]:
    """
    Extract elements from a PDF and normalize them into plain dicts.
    Returns one dict per element with: text, category, page, source.
    """
    elements = partition_pdf(filename=path, strategy="hi_res")

    parsed = []
    for el in elements:
        parsed.append({
            "text": el.text,
            "category": el.category,
            "page": el.metadata.page_number,
            "source": el.metadata.filename,
        })
    return parsed