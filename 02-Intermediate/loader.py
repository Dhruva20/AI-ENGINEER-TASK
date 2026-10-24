import io
import re

from pypdf import PdfReader

SUPPORTED_TYPES = (".txt", ".pdf")


class DocumentError(Exception):
    """Raised with a friendly message when a file can't be used."""


def _clean(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)       # collapse repeated spaces/tabs
    text = re.sub(r"\n{3,}", "\n\n", text)    # collapse many blank lines
    return text.strip()


def load_file(uploaded_file) -> str:
    """Return the text content of an uploaded .txt or .pdf file."""
    name = uploaded_file.name
    if not name.lower().endswith(SUPPORTED_TYPES):
        raise DocumentError(f"'{name}' is not supported. Upload a .txt or .pdf file.")

    data = uploaded_file.getvalue()
    if not data:
        raise DocumentError(f"'{name}' is empty.")

    try:
        if name.lower().endswith(".pdf"):
            reader = PdfReader(io.BytesIO(data))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        else:
            text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise DocumentError(f"'{name}' is not valid UTF-8 text.")
    except Exception as e:
        raise DocumentError(f"Could not read '{name}'. It may be corrupted or password-protected. ({e})")

    text = _clean(text)
    if not text:
        raise DocumentError(
            f"No readable text found in '{name}'. It may be a scanned PDF (images only)."
        )
    return text