from __future__ import annotations

from email import policy
from email.parser import BytesParser
from io import BytesIO

import fitz
import pdfplumber


class DocumentParseError(Exception):
    pass


def extract_text(filename: str, content_type: str | None, payload: bytes) -> str:
    lower = filename.lower()

    if lower.endswith(".pdf") or content_type == "application/pdf":
        return _extract_pdf_text(payload)

    if lower.endswith(".eml") or content_type == "message/rfc822":
        return _extract_email_text(payload)

    try:
        return payload.decode("utf-8", errors="ignore")
    except Exception as exc:
        raise DocumentParseError("Unable to decode text payload") from exc


def _extract_pdf_text(payload: bytes) -> str:
    text_parts: list[str] = []

    with fitz.open(stream=payload, filetype="pdf") as doc:
        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                text_parts.append(page_text)

    if not "".join(text_parts).strip():
        with pdfplumber.open(BytesIO(payload)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)

    combined = "\n".join(part.strip() for part in text_parts if part and part.strip())
    if not combined:
        raise DocumentParseError("No extractable text found in PDF")
    return combined


def _extract_email_text(payload: bytes) -> str:
    message = BytesParser(policy=policy.default).parsebytes(payload)

    subject = message.get("subject", "")
    sender = message.get("from", "")
    to = message.get("to", "")

    body_parts: list[str] = []
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body_parts.append(part.get_content())
    else:
        body_parts.append(message.get_content())

    body = "\n".join(part.strip() for part in body_parts if part and part.strip())
    return f"Subject: {subject}\nFrom: {sender}\nTo: {to}\n\n{body}".strip()
