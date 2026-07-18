"""
rag_chain.py — Cadena RAG | MedQuery AI
Paso 4: Retriever FAISS + LLM Groq integrados en cadena LangChain.

Flujo:
  Consulta del usuario
      |
  FAISS Retriever  (top-k chunks semanticamente similares)
      |
  Prompt clinico   (contexto recuperado + pregunta)
      |
  Groq LLM         (Llama 3 — alta velocidad, baja temperatura)
      |
  Respuesta + metadatos de fuente
"""

import os
import pickle
import warnings
from pathlib import Path

from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv()  # no-op en Streamlit Cloud, activo en desarrollo local


def _get_secret(key: str, default: str = "") -> str:
    """
    Lee una clave de configuracion en este orden de prioridad:
      1. st.secrets (Streamlit Community Cloud)
      2. os.getenv  (archivo .env local / variables del sistema)
    """
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings

warnings.filterwarnings("ignore")
load_dotenv()

# ─── Rutas ────────────────────────────────────────────────────────────────────
ROOT_DIR    = Path(__file__).resolve().parents[1]
DB_PATH     = ROOT_DIR / "db"

# ─── Configuración del modelo ─────────────────────────────────────────────────
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL  = os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant")
TOP_K       = 4   # chunks a recuperar por consulta
TEMPERATURE = 0.1 # baja temperatura: respuestas deterministas y precisas

# ─── Prompt del sistema clínico ───────────────────────────────────────────────
SYSTEM_PROMPT = """Eres MedQuery AI, un asistente clinico especializado en consulta \
de protocolos y manuales internos de una clinica privada.

Tu funcion es responder consultas del personal medico y administrativo \
ESTRICTAMENTE basandote en los fragmentos de documentacion clinica que se te \
proporcionan como contexto.

REGLAS OBLIGATORIAS:
1. Responde UNICAMENTE con informacion presente en el contexto proporcionado.
2. Si la informacion solicitada NO esta en el contexto, responde exactamente: \
"Esta informacion no se encuentra en los protocolos disponibles. \
Consulte con el area correspondiente."
3. No inventes, supongas ni extrapoles informacion medica.
4. Responde siempre en espanol, de forma clara y estructurada.
5. Se conciso y preciso: el personal clinico necesita respuestas directas.
6. Cuando sea relevante, indica el nombre del protocolo o seccion de origen.

CONTEXTO DOCUMENTADO:
{context}"""


# ═══════════════════════════════════════════════════════════════════════════════
# CARGA DE RECURSOS
# ═══════════════════════════════════════════════════════════════════════════════

def _load_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def _load_vectorstore(embeddings: HuggingFaceEmbeddings) -> FAISS:
    if not (DB_PATH / "index.faiss").exists():
        raise FileNotFoundError(
            f"Indice FAISS no encontrado en {DB_PATH}. "
            "Ejecuta 'python src/ingest.py' primero."
        )
    return FAISS.load_local(
        str(DB_PATH),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def _build_components(vectorstore: FAISS) -> tuple:
    """
    Construye y devuelve los tres componentes RAG por separado:
      - retriever : busca los k chunks mas relevantes en FAISS
      - llm       : ChatGroq con Llama 3
      - prompt    : template clinico con {context} e {input}

    Usamos componentes separados (en lugar de una cadena LangChain)
    para compatibilidad total con LangChain 1.x donde langchain.chains
    fue eliminado del paquete principal.
    """
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K},
    )

    llm = ChatGroq(
        model=_get_secret("GROQ_MODEL_NAME", GROQ_MODEL),
        temperature=TEMPERATURE,
        api_key=_get_secret("GROQ_API_KEY"),
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
    ])

    return retriever, llm, prompt


def _get_indexed_doc_names() -> list[str]:
    """
    Lee el docstore del index.pkl para extraer los nombres de archivos PDF
    indexados, sin cargar el modelo de embeddings.
    """
    pkl_path = DB_PATH / "index.pkl"
    if not pkl_path.exists():
        return []
    data     = pickle.load(open(pkl_path, "rb"))
    docstore = data[0]
    docs     = list(docstore._dict.values())
    return sorted(set(
        d.metadata.get("source_file", "")
        for d in docs
        if d.metadata.get("source_file")
    ))


# ═══════════════════════════════════════════════════════════════════════════════
# API PUBLICA — llamada desde app.py
# ═══════════════════════════════════════════════════════════════════════════════

class CustomRAGChain:
    """
    Envoltura personalizada para compatibilidad con la interfaz Runnable de LangChain.
    Permite llamar a .invoke() como se espera en app.py.
    """
    def __init__(self, retriever, llm, prompt):
        self.retriever = retriever
        self.llm       = llm
        self.prompt    = prompt

    def invoke(self, inputs: dict) -> dict:
        """
        Orquesta manualmente el pipeline RAG:
          1. Recuperar chunks relevantes con FAISS
          2. Formatear contexto como texto plano
          3. Inyectar en el prompt clinico
          4. Invocar Groq LLM
          5. Devolver respuesta + documentos fuente
        """
        query   = inputs["input"]
        docs    = self.retriever.invoke(query)
        context = "\n\n".join(doc.page_content for doc in docs)

        messages = self.prompt.format_messages(context=context, input=query)
        response = self.llm.invoke(messages)

        return {
            "answer":  response.content,
            "context": docs,
        }


def load_rag_resources() -> tuple:
    """
    Carga todos los recursos RAG y devuelve un CustomRAGChain listo para .invoke().
    Disenado para @st.cache_resource en app.py (se ejecuta una sola vez).
    """
    embeddings  = _load_embeddings()
    vectorstore = _load_vectorstore(embeddings)
    retriever, llm, prompt = _build_components(vectorstore)

    chain     = CustomRAGChain(retriever, llm, prompt)
    doc_names = _get_indexed_doc_names()
    return chain, doc_names


def get_source_label(context_docs: list) -> str:
    """
    Genera una etiqueta legible con la referencia del documento fuente mas relevante.
    Se muestra como el tag 'Ref:' en la burbuja de respuesta de la AI.

    Ejemplo: "MQ-CLI-101 — URG_manejo_infecciones_respiratorias_v1"
    """
    if not context_docs:
        return "Protocolo interno"

    meta   = context_docs[0].metadata
    fname  = meta.get("source_file", "Protocolo interno").replace(".pdf", "")
    doc_id = meta.get("doc_id", "")
    triage = meta.get("triage", "")

    parts = []
    if doc_id:
        parts.append(doc_id)
    parts.append(fname)
    if triage:
        parts.append(f"Triage: {triage}")

    return " | ".join(parts)
