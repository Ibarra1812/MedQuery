"""
ingest.py — Pipeline de Ingesta RAG | MedQuery AI
Paso 3: Extracción, chunking y vectorización de protocolos clínicos.

Estrategia:
  - Fuente  : protocols_pdf/  (PDFs con texto LaTeX + bloque JSON de metadatos al final)
  - Índice  : db/             (FAISS persistido en disco)
  - Prefijo : primer segmento del nombre de archivo antes del guion bajo
               determina el área de negocio (URG, ADM, BIO, FAR)
"""

import json
import logging
import re
from pathlib import Path

import fitz  # PyMuPDF
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─── Rutas ────────────────────────────────────────────────────────────────────
ROOT_DIR    = Path(__file__).resolve().parents[1]   # raíz del proyecto
PDF_DIR     = ROOT_DIR / "protocols_pdf"
DB_DIR      = ROOT_DIR / "db"

# ─── Modelo de embeddings ─────────────────────────────────────────────────────
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ─── Mapeo prefijo → área de negocio ─────────────────────────────────────────
AREA_MAP: dict[str, str] = {
    "URG": "Urgencias y Emergencias",
    "ADM": "Administración y Epidemiología",
    "BIO": "Biología y Laboratorio",
    "FAR": "Farmacia Clínica",
}

# ─── Parámetros de chunking ───────────────────────────────────────────────────
CHUNK_SIZE    = 600   # caracteres; apropiado para texto clínico denso
CHUNK_OVERLAP = 80    # solapamiento para preservar contexto entre fragmentos


# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACCIÓN DE METADATOS
# ═══════════════════════════════════════════════════════════════════════════════

def extract_area(filename: str) -> tuple[str, str]:
    """
    Lee el prefijo antes del primer guion bajo del nombre de archivo.
    Devuelve (prefix, area_label).

    Ejemplos:
        "URG_manejo_infecciones.pdf" -> ("URG", "Urgencias y Emergencias")
        "ADM_notificacion.pdf"       -> ("ADM", "Administracion y Epidemiologia")
    """
    prefix = filename.split("_")[0].upper()
    area   = AREA_MAP.get(prefix, f"Area no mapeada ({prefix})")
    return prefix, area


def extract_json_metadata(raw_text: str) -> tuple[str, dict]:
    """
    Busca y extrae el bloque JSON de metadatos institucionales embebido
    al final del texto del PDF.

    Estrategia de deteccion (en orden de prioridad):
      1. Busca un objeto JSON que contenga la clave "doc_id" (esquema conocido).
      2. Fallback: busca cualquier objeto JSON valido en los ultimos 3.000 chars.
      3. Sin bloque JSON: devuelve el texto completo y un dict vacio.

    Devuelve (texto_sin_bloque_json, metadata_dict).
    """
    # Estrategia 1: clave "doc_id" canonica
    pattern = re.compile(r'(\{[^{}]*?"doc_id"[^{}]*?\})', re.DOTALL)
    matches = list(pattern.finditer(raw_text))

    if matches:
        last_match = matches[-1]
        try:
            metadata   = json.loads(last_match.group(1))
            clean_text = raw_text[: last_match.start()].strip()
            return clean_text, metadata
        except json.JSONDecodeError:
            log.warning("   JSON con 'doc_id' encontrado pero no parseable; intentando fallback.")

    # Estrategia 2: cualquier JSON al final del documento
    tail = raw_text[-3000:]
    last_open  = tail.rfind("{")
    last_close = tail.rfind("}")

    if last_open != -1 and last_close > last_open:
        candidate = tail[last_open : last_close + 1]
        try:
            metadata   = json.loads(candidate)
            cut_at     = len(raw_text) - len(tail) + last_open
            clean_text = raw_text[:cut_at].strip()
            log.info("   Metadatos extraidos por fallback (JSON generico al final).")
            return clean_text, metadata
        except json.JSONDecodeError:
            pass

    # Estrategia 3: sin bloque JSON
    log.warning("   No se detecto bloque de metadatos JSON en el documento.")
    return raw_text.strip(), {}


# ═══════════════════════════════════════════════════════════════════════════════
# CARGA DE PDFs
# ═══════════════════════════════════════════════════════════════════════════════

def load_pdf(pdf_path: Path) -> tuple[str, dict]:
    """
    Extrae el texto completo de un PDF y separa el bloque de metadatos.
    Enriquece el dict de metadatos con informacion derivada del nombre de archivo.

    Devuelve (texto_limpio, metadatos_enriquecidos).
    """
    with fitz.open(str(pdf_path)) as doc:
        full_text = "\n".join(page.get_text("text") for page in doc)

    clean_text, meta = extract_json_metadata(full_text)

    prefix, area = extract_area(pdf_path.name)
    meta.update({
        "area_prefix": prefix,
        "area_label":  area,
        "source_file": pdf_path.name,
    })

    return clean_text, meta


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTRUCCION DEL INDICE FAISS
# ═══════════════════════════════════════════════════════════════════════════════

def build_faiss_index(lc_documents: list, embeddings: HuggingFaceEmbeddings) -> None:
    """
    Vectoriza la lista de LangChain Documents y persiste el indice FAISS en DB_DIR.
    Re-ingesta limpia: sobreescribe cualquier indice previo.
    """
    DB_DIR.mkdir(parents=True, exist_ok=True)

    log.info(f"Vectorizando {len(lc_documents)} chunks...")
    vectorstore = FAISS.from_documents(lc_documents, embeddings)
    vectorstore.save_local(str(DB_DIR))
    log.info(f"Indice FAISS guardado en: {DB_DIR}")


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def run_ingestion() -> None:
    """
    Orquesta el pipeline completo:
      1. Descubre PDFs en protocols_pdf/
      2. Extrae texto y metadatos de cada PDF
      3. Divide en chunks (RecursiveCharacterTextSplitter)
      4. Carga modelo de embeddings HuggingFace (all-MiniLM-L6-v2, CPU)
      5. Construye y persiste el indice FAISS en db/
    """
    # 1. Descubrimiento de PDFs
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        log.error(f"No se encontraron archivos PDF en: {PDF_DIR}")
        log.error("Coloca los documentos clinicos en la carpeta 'protocols_pdf/' y vuelve a ejecutar.")
        return

    log.info(f"Documentos detectados ({len(pdf_files)}):")
    for f in pdf_files:
        log.info(f"  * {f.name}")

    # 2. Carga y chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    lc_documents: list[Document] = []
    total_pdfs_ok = 0

    for pdf_path in pdf_files:
        log.info(f"Procesando: {pdf_path.name}")

        try:
            clean_text, doc_meta = load_pdf(pdf_path)
        except Exception as exc:
            log.error(f"Error al leer {pdf_path.name}: {exc}")
            continue

        raw_chunks = splitter.split_text(clean_text)
        log.info(f"  Chunks generados: {len(raw_chunks)}")

        for idx, chunk in enumerate(raw_chunks):
            chunk_meta = {
                **doc_meta,
                "chunk_index":  idx,
                "total_chunks": len(raw_chunks),
            }
            lc_documents.append(Document(page_content=chunk, metadata=chunk_meta))

        log.info(f"  Area       : {doc_meta.get('area_label', 'N/A')}")
        log.info(f"  Doc ID     : {doc_meta.get('doc_id', 'N/A')}")
        log.info(f"  Triage     : {doc_meta.get('triage', 'N/A')}")
        log.info(f"  Especialidad: {doc_meta.get('speciality', doc_meta.get('specialty', 'N/A'))}")
        total_pdfs_ok += 1

    if not lc_documents:
        log.error("No se generaron chunks. Verifica el contenido de los PDFs.")
        return

    log.info(f"Resumen: {total_pdfs_ok}/{len(pdf_files)} PDFs procesados | {len(lc_documents)} chunks totales")

    # 3. Modelo de embeddings
    log.info(f"Cargando modelo de embeddings: {EMBED_MODEL}")
    log.info("(Primera ejecucion: descarga ~90 MB desde HuggingFace Hub)")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    # 4 + 5. Construccion y persistencia del indice
    build_faiss_index(lc_documents, embeddings)

    log.info("=" * 52)
    log.info("Ingesta completada: indice FAISS listo en db/")
    log.info("=" * 52)


if __name__ == "__main__":
    run_ingestion()
