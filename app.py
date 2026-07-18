"""
MedQuery AI — Asistente Clínico RAG
app.py | Frontend principal (Streamlit)
"""

import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MedQuery AI – Clinical Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# CSS MÍNIMO — sólo para respetar la paleta y tipografía del prototipo
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Fuente base ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── Colores del prototipo ── */
    :root {
        --primary:       #004e9f;
        --primary-light: #0066cc;
        --surface:       #fcf9f8;
        --surface-low:   #f6f3f2;
        --outline:       #727784;
        --outline-var:   #c1c6d5;
        --on-surface:    #1c1b1b;
        --on-surf-var:   #414753;
        --success:       #2ECC71;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: var(--surface-low);
        border-right: 1px solid var(--outline-var);
        padding: 0;
    }
    [data-testid="stSidebar"] > div:first-child { padding: 0; }

    /* ── Fondo principal ── */
    [data-testid="stAppViewContainer"] { background-color: var(--surface); }

    /* ── Burbuja usuario ── */
    .msg-user {
        background: #F1F3F5;
        border: 1px solid #E9ECEF;
        border-radius: 4px;
        padding: 12px 16px;
        max-width: 78%;
        margin-left: auto;
        margin-bottom: 8px;
        font-size: 14px;
        line-height: 20px;
        color: var(--on-surface);
    }
    .msg-user .msg-label {
        font-size: 11px;
        font-weight: 600;
        color: var(--on-surf-var);
        letter-spacing: 0.02em;
        margin-bottom: 6px;
    }

    /* ── Burbuja AI ── */
    .msg-ai {
        background: #ffffff;
        border: 1px solid #E9ECEF;
        border-left: 4px solid var(--primary);
        border-radius: 4px;
        padding: 12px 16px;
        max-width: 78%;
        margin-right: auto;
        margin-bottom: 8px;
        font-size: 14px;
        line-height: 20px;
        color: var(--on-surface);
        box-shadow: 0 1px 2px rgba(0,0,0,.06);
    }
    .msg-ai .msg-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
    }
    .msg-ai .msg-label {
        font-size: 11px;
        font-weight: 600;
        color: var(--primary);
        letter-spacing: 0.02em;
    }
    .msg-ai .msg-ref {
        margin-left: auto;
        font-size: 10px;
        font-weight: 600;
        color: var(--outline);
        background: #F1F3F5;
        padding: 2px 8px;
        border-radius: 2px;
        letter-spacing: 0.02em;
    }

    /* ── Status pills (sidebar) ── */
    .status-card {
        display: flex;
        align-items: center;
        gap: 8px;
        background: var(--surface);
        border: 1px solid var(--outline-var);
        border-radius: 2px;
        padding: 8px 10px;
        margin-bottom: 8px;
    }
    .dot-green { width:8px; height:8px; border-radius:50%; background:var(--success); flex-shrink:0; }
    .status-title { font-size:11px; font-weight:600; color:var(--on-surf-var); letter-spacing:.02em; }
    .status-value { font-size:14px; font-weight:500; color:var(--on-surface); }

    /* ── Aviso legal inferior ── */
    .legal-note {
        text-align: center;
        font-size: 11px;
        color: var(--outline);
        letter-spacing: .02em;
        margin-top: 6px;
    }

    /* ── Ocultar hamburger y footer de Streamlit ── */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# ESTADO DE SESIÓN — historial de chat
# ──────────────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []          # lista de dicts {role, content, ref}

if "rag_ready" not in st.session_state:
    st.session_state.rag_ready = False      # se pondrá True cuando el backend esté cargado

if "docs_loaded" not in st.session_state:
    st.session_state.docs_loaded = []       # nombres de PDFs indexados

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Estado del sistema
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── Header ──
    st.markdown(
        """
        <div style="padding:20px 20px 16px 20px;
                    border-bottom:1px solid #c1c6d5;
                    display:flex; align-items:center; gap:10px;">
            <span style="font-size:28px;">🏥</span>
            <div>
                <div style="font-size:18px; font-weight:700;
                            color:#004e9f; line-height:1.2;">MedQuery AI</div>
                <div style="font-size:11px; font-weight:600;
                            color:#414753; letter-spacing:.04em;">Clinical Decision Support</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Sección: Estado del sistema ──
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#727784;'
        'letter-spacing:.08em;text-transform:uppercase;'
        'padding:0 4px;margin-bottom:10px;">Estado del Sistema</p>',
        unsafe_allow_html=True,
    )

    # Vectorial DB
    db_color  = "#2ECC71" if st.session_state.rag_ready else "#E74C3C"
    db_status = "Cargada (FAISS)" if st.session_state.rag_ready else "No inicializada"
    st.markdown(
        f"""
        <div class="status-card">
            <div class="dot-green" style="background:{db_color};"></div>
            <div>
                <div class="status-title">Vectorial DB</div>
                <div class="status-value">{db_status}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # LLM Model
    st.markdown(
        """
        <div class="status-card">
            <div class="dot-green"></div>
            <div>
                <div class="status-title">LLM Model</div>
                <div class="status-value">Online (Llama-3 via Groq)</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Documentación cargada
    if st.session_state.docs_loaded:
        for doc_name in st.session_state.docs_loaded:
            short = doc_name if len(doc_name) <= 28 else doc_name[:25] + "…"
            st.markdown(
                f"""
                <div class="status-card">
                    <span style="font-size:18px;">📄</span>
                    <div>
                        <div class="status-title">Documentation</div>
                        <div class="status-value" title="{doc_name}">{short}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            """
            <div class="status-card">
                <span style="font-size:18px;">📄</span>
                <div>
                    <div class="status-title">Documentation</div>
                    <div class="status-value" style="color:#727784;">Sin documentos cargados</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Footer sidebar ──
    st.markdown("<br>" * 4, unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:11px;font-weight:600;color:#727784;'
        'letter-spacing:.02em;text-align:center;'
        'border-top:1px solid #c1c6d5;padding-top:14px;">'
        'Uso exclusivo para personal autorizado</p>',
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────────────────────
# MAIN — Header
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="border-bottom:1px solid #c1c6d5; padding-bottom:12px; margin-bottom:20px;">
        <h1 style="font-size:20px; font-weight:600; color:#004e9f; margin:0; line-height:1.4;">
            Asistente Clínico RAG
        </h1>
        <p style="font-size:11px; font-weight:600; color:#414753;
                  letter-spacing:.02em; margin:2px 0 0 0;">
            Consulta de protocolos internos en tiempo real
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN — Área de chat (historial)
# ──────────────────────────────────────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        # Estado vacío — mensaje de bienvenida
        st.markdown(
            """
            <div style="text-align:center; padding:60px 20px; color:#727784;">
                <div style="font-size:48px; margin-bottom:12px;">🏥</div>
                <p style="font-size:16px; font-weight:600; color:#414753; margin-bottom:6px;">
                    Bienvenido a MedQuery AI
                </p>
                <p style="font-size:14px; line-height:20px;">
                    Formula tu consulta sobre protocolos clínicos, manuales de urgencias<br>
                    o normativas institucionales en el campo de texto de abajo.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f"""
                    <div class="msg-user">
                        <div class="msg-label">👤 &nbsp;Usuario</div>
                        {msg["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                ref_html = (
                    f'<span class="msg-ref">Ref: {msg["ref"]}</span>'
                    if msg.get("ref")
                    else ""
                )
                st.markdown(
                    f"""
                    <div class="msg-ai">
                        <div class="msg-header">
                            <span>🤖</span>
                            <span class="msg-label">MedQuery AI</span>
                            {ref_html}
                        </div>
                        {msg["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# ──────────────────────────────────────────────────────────────────────────────
# MAIN — Input de consulta
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

with st.form(key="query_form", clear_on_submit=True):
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_query = st.text_input(
            label="query",
            placeholder="Escribe tu consulta sobre protocolos aquí...",
            label_visibility="collapsed",
        )
    with col_btn:
        submitted = st.form_submit_button("Enviar ▶", use_container_width=True)

st.markdown(
    '<p class="legal-note">Las respuestas de IA deben ser verificadas clínicamente.</p>',
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# LÓGICA PROVISIONAL — se reemplazará en el Paso 4 con el RAG real
# ──────────────────────────────────────────────────────────────────────────────
if submitted and user_query.strip():
    # Guardar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Placeholder: respuesta stub hasta que el backend RAG esté conectado
    stub_response = (
        "⚙️ <em>Backend RAG aún no conectado.</em> "
        "Esta respuesta es un marcador provisional. "
        "El agente responderá aquí una vez integrado el Retriever y la API de Groq (Paso 4)."
    )
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": stub_response,
            "ref": "Pendiente — Paso 4",
        }
    )
    st.rerun()
