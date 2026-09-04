"""Document processing: extract text from every page of each file in notes/.

Pipeline per PDF page:
  1. Try direct text extraction (PyMuPDF if installed, else pypdf).
  2. If a page yields < 50 chars, treat it as a scanned image and OCR it
     (pytesseract + Tesseract binary + Pillow preprocessing).
  3. Concatenate all pages in order, cache to data/extracted/<stem>.txt,
     and log any page that failed both paths.

All heavy imports are guarded so the web app boots even when the
optional OCR stack is not installed.
"""
import os
import io
import json
import logging

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import pytesseract
    from PIL import Image, ImageOps, ImageFilter
except ImportError:
    pytesseract = None
    Image = None

NOTES_DIR = os.path.join(os.getcwd(), 'notes')
CACHE_DIR = os.path.join(os.getcwd(), 'data', 'extracted')
MIN_TEXT_CHARS = 50


def ocr_available():
    if pytesseract is None or Image is None:
        return False
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def preprocess_for_ocr(img):
    """Grayscale + autocontrast + mild sharpening; retry path uses threshold."""
    g = img.convert('L')
    g = ImageOps.autocontrast(g)
    return g.filter(ImageFilter.SHARPEN)


def ocr_image(img):
    """OCR with retry: default pass, then binarized threshold pass."""
    try:
        text = pytesseract.image_to_string(preprocess_for_ocr(img)) or ''
        if len(text.strip()) >= MIN_TEXT_CHARS:
            return text
        # Retry with hard threshold for faint scans.
        g = img.convert('L')
        bw = g.point(lambda p: 255 if p > 150 else 0)
        text2 = pytesseract.image_to_string(bw) or ''
        return text2 if len(text2.strip()) > len(text.strip()) else text
    except Exception as e:
        logger.error(f'OCR failed: {e}')
        return ''


def page_images_fitz(page, dpi=200):
    pix = page.get_pixmap(dpi=dpi)
    img = Image.open(io.BytesIO(pix.tobytes('png')))
    return [img]


def extract_pdf_text(pdf_path):
    """Return (full_text, stats). stats has pages/chars/status/failed_pages."""
    pages_out = []
    failed = []
    if fitz is not None:
        try:
            doc = fitz.open(pdf_path)
            for i, page in enumerate(doc):
                text = (page.get_text() or '').strip()
                if len(text) >= MIN_TEXT_CHARS:
                    pages_out.append(text)
                elif ocr_available():
                    logger.info(f'{os.path.basename(pdf_path)} p{i+1}: image page, OCR…')
                    try:
                        combined = '\n'.join(ocr_image(im) for im in page_images_fitz(page))
                        if combined.strip():
                            pages_out.append(f'[OCR] {combined.strip()}')
                        else:
                            failed.append(i + 1)
                            logger.warning(f'{os.path.basename(pdf_path)} p{i+1}: OCR empty')
                    except Exception as e:
                        failed.append(i + 1)
                        logger.error(f'{os.path.basename(pdf_path)} p{i+1}: {e}')
                else:
                    failed.append(i + 1)
                    logger.warning(f'{os.path.basename(pdf_path)} p{i+1}: image page, '
                                   f'OCR unavailable (install tesseract + pytesseract)')
            doc.close()
        except Exception as e:
            logger.error(f'PyMuPDF failed on {pdf_path}: {e}; falling back to pypdf')
            return extract_pdf_text_pypdf(pdf_path)
    elif PdfReader is not None:
        return extract_pdf_text_pypdf(pdf_path)
    else:
        return '', {'pages': 0, 'chars': 0, 'status': 'no-pdf-backend', 'failed_pages': []}
    full = '\n'.join(f'--- PAGE {i+1} ---\n{t}' for i, t in enumerate(pages_out))
    status = 'ok' if not failed else ('partial' if pages_out else 'failed')
    if failed and not ocr_available():
        status += ' (ocr-missing)'
    return full, {'pages': len(pages_out), 'chars': len(full),
                  'status': status, 'failed_pages': failed}


def extract_pdf_text_pypdf(pdf_path):
    pages_out, failed = [], []
    try:
        reader = PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            try:
                text = (page.extract_text() or '').strip()
            except Exception:
                text = ''
            if len(text) >= MIN_TEXT_CHARS:
                pages_out.append(text)
            else:
                failed.append(i + 1)
        full = '\n'.join(f'--- PAGE {i+1} ---\n{t}' for i, t in enumerate(pages_out))
        status = 'ok' if not failed else ('partial' if pages_out else 'failed')
        status += ' (text-only; install PyMuPDF+tesseract for scanned pages)'
        return full, {'pages': len(pages_out), 'chars': len(full),
                      'status': status, 'failed_pages': failed}
    except Exception as e:
        logger.error(f'Cannot read {pdf_path}: {e}')
        return '', {'pages': 0, 'chars': 0, 'status': f'error: {e}', 'failed_pages': []}


def extract_text_from_file(path):
    low = path.lower()
    if low.endswith('.pdf'):
        text, _ = extract_pdf_text(path)
        return text
    if low.endswith(('.txt', '.md', '.markdown')):
        try:
            with open(path, encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f'Cannot read {path}: {e}')
            return ''
    if low.endswith('.docx'):
        try:
            import docx
            doc = docx.Document(path)
            return '\n'.join(p.text for p in doc.paragraphs)
        except ImportError:
            logger.error('python-docx not installed, skipping .docx')
            return ''
        except Exception as e:
            logger.error(f'DOCX error {path}: {e}')
            return ''
    return ''


def process_all_pdfs(notes_dir=None):
    """Process every supported file in notes/ (+ legacy PDFs in project root)."""
    notes_dir = notes_dir or NOTES_DIR
    os.makedirs(CACHE_DIR, exist_ok=True)
    candidates = []
    if os.path.isdir(notes_dir):
        for fname in sorted(os.listdir(notes_dir)):
            if fname.lower().endswith(('.pdf', '.txt', '.md', '.markdown', '.docx')):
                candidates.append(os.path.join(notes_dir, fname))
    # Legacy: PDFs sitting in the project root (current layout).
    for fname in sorted(os.listdir(os.getcwd())):
        if fname.lower().endswith('.pdf'):
            full = os.path.join(os.getcwd(), fname)
            if full not in candidates:
                candidates.append(full)
    results = {}
    for path in candidates:
        fname = os.path.basename(path)
        logger.info(f'Processing {fname}…')
        if fname.lower().endswith('.pdf'):
            text, stats = extract_pdf_text(path)
        else:
            text = extract_text_from_file(path)
            stats = {'pages': 1, 'chars': len(text),
                     'status': 'ok' if text.strip() else 'empty', 'failed_pages': []}
        stem = os.path.splitext(fname)[0]
        try:
            with open(os.path.join(CACHE_DIR, stem + '.txt'), 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            logger.error(f'Cache write failed for {fname}: {e}')
        results[fname] = stats
        logger.info(f'  -> {stats["chars"]} chars, status={stats["status"]}')
    try:
        with open(os.path.join(os.getcwd(), 'data', 'documents.json'), 'w') as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        logger.error(f'Manifest write failed: {e}')
    return results
