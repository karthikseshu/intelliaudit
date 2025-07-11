from PyPDF2 import PdfReader
from docx import Document
from fastapi import UploadFile
import io

def extract_text_from_file(file: UploadFile):
    filename = file.filename.lower()
    content = file.file.read()
    if filename.endswith('.pdf'):
        reader = PdfReader(io.BytesIO(content))
        text = ""
        pages = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            text += page_text + "\n"
            pages.append({"page": i+1, "text": page_text})
        return text, pages
    elif filename.endswith('.docx'):
        doc = Document(io.BytesIO(content))
        text = "\n".join([p.text for p in doc.paragraphs])
        # No page info for docx, treat as single page
        return text, [{"page": 1, "text": text}]
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are supported.") 