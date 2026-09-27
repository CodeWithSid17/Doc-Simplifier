class DocumentExtractionError(Exception):
    pass


def extract_text(document):
    file_type = document.file_type

    if file_type == "txt":
        return extract_txt(document)
    if file_type == "pdf":
        return extract_pdf(document)
    if file_type == "docx":
        return extract_docx(document)
    if file_type == "xlsx":
        return extract_xlsx(document)
    if file_type in {"jpg", "jpeg", "png"}:
        return extract_image(document)

    raise DocumentExtractionError(f"Unsupported file type: {file_type}")


def extract_txt(document):
    document.file.seek(0)
    content = document.file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    result = str(content).strip()
    if not result:
        raise DocumentExtractionError("The text file is empty.")
    return result


def extract_pdf(document):
    try:
        import pypdf
    except ImportError as exc:
        raise DocumentExtractionError("pypdf is not installed.") from exc

    document.file.seek(0)
    reader = pypdf.PdfReader(document.file)
    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())

    result = "\n\n".join(pages).strip()
    if not result:
        raise DocumentExtractionError(
            "No readable text was found in this PDF. A scanned PDF needs OCR support."
        )
    return result


def extract_docx(document):
    try:
        from docx import Document as WordDocument
    except ImportError as exc:
        raise DocumentExtractionError("python-docx is not installed.") from exc

    document.file.seek(0)
    word_document = WordDocument(document.file)
    paragraphs = []

    for paragraph in word_document.paragraphs:
        text = paragraph.text.strip()
        if text:
            paragraphs.append(text)

    for table in word_document.tables:
        for row in table.rows:
            values = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if values:
                paragraphs.append(" | ".join(values))

    result = "\n\n".join(paragraphs).strip()
    if not result:
        raise DocumentExtractionError("No readable text was found in this DOCX.")
    return result


def extract_xlsx(document):
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise DocumentExtractionError("openpyxl is not installed.") from exc

    document.file.seek(0)
    workbook = load_workbook(document.file, read_only=True, data_only=True)
    sheets = []

    for worksheet in workbook.worksheets:
        rows = []
        for row in worksheet.iter_rows(values_only=True):
            values = [str(value).strip() for value in row if value is not None]
            if values:
                rows.append(" | ".join(values))
        if rows:
            sheets.append(f"Sheet: {worksheet.title}\n" + "\n".join(rows))

    workbook.close()
    result = "\n\n".join(sheets).strip()

    if not result:
        raise DocumentExtractionError("No readable data was found in this Excel file.")
    return result


def extract_image(document):
    try:
        from PIL import Image
        import pytesseract
    except ImportError as exc:
        raise DocumentExtractionError(
            "Image OCR dependencies are not installed on the server."
        ) from exc

    document.file.seek(0)

    try:
        image = Image.open(document.file)
        image = image.convert("RGB")
        text = pytesseract.image_to_string(image)
    except Exception as exc:
        raise DocumentExtractionError(
            "Could not read this image. Make sure the image contains clear text."
        ) from exc

    result = text.strip()
    if not result:
        raise DocumentExtractionError(
            "No readable text was found in this image."
        )
    return result
