# MedQuery AI: Asistente Clínico de Consulta (RAG)

MedQuery AI es un asistente de búsqueda y consulta basado en la arquitectura RAG (Retrieval-Augmented Generation) diseñado para facilitar la gestión del conocimiento en clínicas e instituciones de salud. Permite al personal médico y administrativo consultar protocolos internos, normativas sanitarias y manuales de procedimientos mediante consultas en lenguaje natural.

El sistema procesa documentos en formato PDF, genera embeddings vectoriales mediante modelos de Hugging Face, almacena localmente la información en un índice FAISS y utiliza la API de Groq para la generación de respuestas precisas basadas estrictamente en la documentación provista.

## URL de la Aplicación (Despliegue Público)

La plataforma se encuentra disponible en el siguiente enlace:
**[Enlace de Streamlit Cloud](AQUÍ_VA_TU_ENLACE_DE_STREAMLIT_CLOUD)**

## Características Principales

*   **Búsqueda semántica:** Permite realizar consultas en lenguaje natural sin requerir coincidencias exactas de palabras clave.
*   **Baja latencia:** Respuestas rápidas gracias al motor de inferencia de Groq.
*   **Mitigación de alucinaciones:** Generación de respuestas basada exclusivamente en el contexto del documento consultado.
*   **Interfaz simplificada:** Diseñada con componentes nativos de Streamlit, priorizando la facilidad de uso clínico.
*   **Arquitectura modular:** La base documental puede actualizarse reemplazando o añadiendo archivos PDF en el directorio correspondiente.

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

## Tecnologías Utilizadas

*   **Lenguaje:** Python 3.11
*   **Orquestación:** LangChain
*   **Base de Datos Vectorial:** FAISS
*   **Embeddings:** Hugging Face (`all-MiniLM-L6-v2`)
*   **Modelo de Lenguaje (LLM):** Groq API (`llama3-8b-8192`)
*   **Interfaz Gráfica:** Streamlit
*   **Procesamiento de Archivos:** PyMuPDF (`fitz`)
*   **Despliegue:** Streamlit Community Cloud

## Estructura del Proyecto

```text
medquery-ai/
│
├── assets/             # Capturas de pantalla y evidencias visuales
├── db/                 # Índice y base de datos vectorial FAISS persistida
├── protocols_pdf/      # Repositorio local de PDFs médicos institucionales
├── src/
│   ├── loader.py       # Lector, procesador y fragmentador de PDFs
│   ├── embedder.py     # Generador de embeddings e indexador FAISS
│   └── llm_client.py   # Configuración del prompt y conexión con Groq
│
├── app.py              # Aplicación principal e interfaz de Streamlit
├── indexar_datos.py    # Script ejecutable para construir/actualizar la base vectorial
├── requirements.txt    # Dependencias del entorno de Python
├── README.md           # Documentación del repositorio
└── .env.example        # Plantilla para variables de entorno locales
```

## Instalación y Configuración Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/medquery-ai.git
cd medquery-ai
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
GROQ_API_KEY=TU_API_KEY_DE_GROQ_AQUÍ
```

### 5. Indexar la documentación

Coloque los archivos PDF con los protocolos o normativas dentro del directorio `protocols_pdf/` y ejecute el script de indexación para construir la base de conocimiento vectorial:

```bash
python indexar_datos.py
```

### 6. Ejecutar la aplicación

```bash
streamlit run app.py
```

## Ejemplos de Uso

**Consultas de ejemplo:**

*   *¿Cuál es el protocolo de triaje para pacientes con síntomas respiratorios agudos?*
*   *¿Qué pasos se deben seguir en caso de un pinchazo accidental con aguja?*
*   *¿Cuáles son los requisitos de ingreso para una cirugía programada?*

**Ejemplo de flujo de consulta:**

> **Usuario:** ¿Cómo se procede ante una sospecha de paro cardiorrespiratorio en sala de espera?
>
> **MedQuery AI:** De acuerdo con la Sección 2.1 del *Manual de Emergencias de la Clínica (2025)*, se debe activar inmediatamente el 'Código Azul'. El personal de enfermería más cercano debe iniciar compresiones torácicas y solicitar el desfibrilador externo automático (DEA) en un tiempo menor a 60 segundos mientras arriba el equipo de reanimación.

## Despliegue

La aplicación está preparada para ser desplegada en Streamlit Community Cloud. El procesamiento y fragmentación de los documentos se realiza de manera local para resguardar la privacidad de los datos institucionales, mientras que las consultas en producción se resuelven mediante llamadas a la API de Groq utilizando variables de entorno seguras configuradas en la plataforma de Streamlit.

## Autor

*   **[Tu Nombre Aquí]** - Desarrollador del proyecto.
*   [Perfil de GitHub](https://github.com/tu-usuario)

## Licencia

Este proyecto fue desarrollado con fines educativos y de validación técnica. Los documentos utilizados en la demostración son simulados y con fines ilustrativos.

