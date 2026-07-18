# MedQuery AI: Asistente Clínico de Consulta (RAG)

MedQuery AI es un asistente de búsqueda y consulta basado en la arquitectura RAG (Retrieval-Augmented Generation) diseñado para facilitar la gestión del conocimiento en clínicas e instituciones de salud. Permite al personal médico y administrativo consultar protocolos internos, normativas sanitarias y manuales de procedimientos mediante consultas en lenguaje natural.

El sistema procesa documentos en formato PDF, genera embeddings vectoriales mediante modelos de Hugging Face, almacena localmente la información en un índice FAISS y utiliza la API de Groq para la generación de respuestas precisas basadas estrictamente en la documentación provista.

## 🌐 URL de la Aplicación (Despliegue Público)

La plataforma se encuentra disponible en el siguiente enlace:
👉 **[MedQuery AI - Demo en Streamlit Cloud](https://medqueryfast.streamlit.app/)**

---

## 🚀 Experiencia de Desarrollo Ágil
Este prototipo de nivel empresarial fue desarrollado de forma ágil bajo la filosofía **"Funcionalidad sobre Estética"**, utilizando el **IDE de Antigravity** asistido por Inteligencia Artificial. A través de un desarrollo incremental estructurado en 5 etapas interactivas, se consolidó un backend robusto capaz de parsear metadatos complejos (esquemas JSON estructurados embebidos en LaTeX) y orquestar una pipeline RAG personalizada en tiempo récord, libre de dependencias discontinuadas de LangChain.

---

## Características Principales

*   **Búsqueda semántica:** Permite realizar consultas en lenguaje natural sin requerir coincidencias exactas de palabras clave.
*   **Baja latencia:** Respuestas ultra-rápidas gracias al motor de inferencia de Groq.
*   **Mitigación de alucinaciones:** Generación de respuestas basada exclusivamente en el contexto del documento consultado.
*   **Interfaz simplificada:** Diseñada con componentes nativos de Streamlit, priorizando la facilidad de uso clínico y la claridad del diagnóstico.
*   **Gestión dinámica de referencias:** Las respuestas de la IA adjuntan una tarjeta de referencia dinámica (`Ref:`) con el ID del documento, triage clínico y nombre del protocolo.

---

## Arquitectura de la Solución

```text
               Personal Médico / Administrativo
                              │
                              ▼
                      Interfaz Streamlit
                              │
                              ▼
                     Consulta del Usuario
                              │
                              ▼
                    Retriever (FAISS + RAG)
                              │
                              ▼
                  Documentación PDF Indexada
                              │
                              ▼
                     Contexto Clínico Relevante
                              │
                              ▼
                         Groq (LLM)
                              │
                              ▼
                  Respuesta Validada al Usuario
```

---

## Tecnologías Utilizadas

- **Lenguaje:** Python 3.11
- **IDE de Desarrollo:** Antigravity IDE (Claude)
- **Orquestación:** LangChain Core (LCEL directo para LangChain 1.x)
- **Base de Datos Vectorial:** FAISS (Local)
- **Embeddings:** Hugging Face (`sentence-transformers/all-MiniLM-L6-v2`)
- **Modelo de Lenguaje (LLM):** Groq API (`llama-3.1-8b-instant` - Alta velocidad)
- **Interfaz Gráfica:** Streamlit (UI minimalista nativa)
- **Procesamiento de Archivos:** PyMuPDF (`fitz`)
- **Despliegue:** Streamlit Community Cloud

---

## Estructura del Proyecto

```text
MedQuery/
│
├── db/                 # Índice y base de datos vectorial FAISS persistida
├── protocols_pdf/      # Repositorio local de PDFs médicos institucionales
├── src/
│   ├── ingest.py       # Pipeline de ingesta: procesamiento, chunking e indexación
│   └── rag_chain.py    # Cadena RAG: orquestación de recuperación y llamada a Groq
│
├── app.py              # Aplicación principal e interfaz de Streamlit
├── requirements.txt    # Dependencias del entorno de Python
├── README.md           # Documentación del repositorio
├── .env.example        # Plantilla para variables de entorno locales
└── .gitignore          # Exclusiones de Git (protege .env y secrets)
```

---

## Instalación y Configuración Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/Ibarra1812/MedQuery.git
cd MedQuery
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En Mac/Linux:
source .venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Cree un archivo llamado `.env` en la raíz del proyecto basándose en `.env.example`:

```text
GROQ_API_KEY=tu_api_key_de_groq_aqui
GEMINI_API_KEY=tu_api_key_de_gemini_aqui
GROQ_MODEL_NAME=llama-3.1-8b-instant
```

### 5. Indexar la documentación clínica

Coloque los archivos PDF oficiales de protocolos en `protocols_pdf/` y ejecute la indexación:

```bash
python src/ingest.py
```

### 6. Ejecutar la aplicación

```bash
python -m streamlit run app.py
```

---

## Ejemplos de Uso

**Consultas de ejemplo:**

*   _"¿Cuál es el protocolo de triaje para pacientes con síntomas respiratorios agudos?"_ 🚨
*   _"¿Qué pasos se deben seguir en caso de un pinchazo accidental con aguja?"_ 💉
*   _"¿Cuáles son los requisitos de ingreso para una cirugía programada?"_ 📝

**Flujo de respuesta real:**

> **Usuario:** ¿Cómo se procede ante una sospecha de paro cardiorrespiratorio en sala de espera?
>
> **MedQuery AI:** De acuerdo con la Sección 2.1 del *Manual de Emergencias de la Clínica (2025)*, se debe activar inmediatamente el 'Código Azul'. El personal de enfermería más cercano debe iniciar compresiones torácicas y solicitar el desfibrilador externo automático (DEA) en un tiempo menor a 60 segundos mientras arriba el equipo de reanimación. ⏱️

---

## Despliegue

La aplicación se encuentra desplegada en **Streamlit Community Cloud**, conectada directamente a este repositorio de GitHub. El procesamiento y fragmentación de los documentos se realiza de manera local para resguardar la privacidad de los manuales institucionales, mientras que la consulta se resuelve mediante llamadas seguras a la API de Groq utilizando variables de entorno protegidas (*Secrets*).

---

## Autor

*   **Alvaro Ibarra**
    *   _Desarrollador de Soluciones de IA | Proyecto de Startup Ficticia_
    *   [🔗 Perfil de GitHub](https://github.com/Ibarra1812)

---

## Licencia

Este proyecto fue desarrollado con fines educativos y de validación técnica para el Challenge final de Alura.## Licencia

Este proyecto fue desarrollado con fines educativos y de validación técnica. Los documentos utilizados en la demostración son simulados y con fines ilustrativos.

