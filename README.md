# 🏥 MedQuery AI: Asistente Clínico Inteligente (RAG)

**La información médica correcta, al alcance de una pregunta.**

MedQuery AI es un asistente inteligente basado en Inteligencia Artificial y arquitectura **RAG (Retrieval-Augmented Generation)** diseñado para la gestión eficiente del conocimiento en clínicas y centros de salud de alta complejidad. Permite al personal médico y administrativo consultar protocolos internos, normativas sanitarias y manuales de procedimientos de forma instantánea mediante lenguaje natural.

El sistema procesa archivos PDF institucionales, genera embeddings vectoriales precisos utilizando modelos de **Hugging Face**, almacena la información localmente en un índice **FAISS** y utiliza la API de **Groq** como modelo de lenguaje de alta velocidad para responder consultas críticas sin riesgo de alucinaciones.

---

## 🌐 URL de la Aplicación (Deploy Público)
La plataforma se encuentra desplegada y disponible para pruebas en producción aquí:
👉 **[AQUÍ_VA_TU_ENLACE_DE_STREAMLIT_CLOUD]**

---

## 🔥 Características principales

- 🩺 **Búsqueda Semántica Médica:** Consultas en lenguaje natural sin necesidad de coincidencia exacta de palabras clave.
- ⚡ **Respuestas en Tiempo Real:** Infraestructura ultra rápida gracias al motor de inferencia de Groq.
- 🔒 **Garantía Anti-Alucinaciones:** Respuestas basadas estricta y únicamente en el contexto documental proveído.
- 💻 **Interfaz Minimalista y Funcional:** Desarrollada con componentes nativos de Streamlit, priorizando la usabilidad médica sobre la estética pesada.
- 🔁 **Arquitectura Reutilizable:** Diseñado como un motor agnóstico; basta con cambiar los PDFs de la base documental para adaptarlo a cualquier otra especialidad médica o institución.

---

## 🏗️ Arquitectura de la Solución

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

## 🛠️ Tecnologías y Herramientas

* **Lenguaje:** Python 3.11
* **IDE de Desarrollo:** Antigravity IDE (Claude Sonnet)
* **Orquestación:** LangChain
* **Base de Datos Vectorial:** FAISS
* **Embeddings:** Hugging Face (`all-MiniLM-L6-v2`)
* **Modelo de Lenguaje (LLM):** Groq API (`llama3-8b-8192`)
* **Frontend:** Streamlit
* **Procesamiento de Archivos:** PyMuPDF (`fitz`)
* **Despliegue:** Streamlit Community Cloud

---

## 🗂️ Estructura del Proyecto

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

---

## ⚙️ Instrucciones de Instalación y Ejecución Local

### 1. Clonar el repositorio

```bash
git clone [https://github.com/tu-usuario/medquery-ai.git](https://github.com/tu-usuario/medquery-ai.git)
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

### 3. Instalar las dependencias del proyecto

```bash
pip install -r requirements.txt

```

### 4. Configurar variables de entorno

Crea un archivo llamado `.env` en la raíz del proyecto tomando como referencia `.env.example`:

```text
GROQ_API_KEY=TU_API_KEY_DE_GROQ_AQUÍ

```

### 5. Indexar la documentación institucional

Coloca los archivos PDF con los protocolos o normativas dentro de la carpeta `protocols_pdf/` y ejecuta el script para generar la base de conocimientos indexada:

```bash
python indexar_datos.py

```

### 6. Ejecutar la aplicación

```bash
streamlit run app.py

```

---

## 💡 Ejemplos de Interacción (Validación del Agente)

**Consultas frecuentes del personal de salud:**

* *"¿Cuál es el protocolo de triaje para pacientes con síntomas respiratorios agudos?"* 🚨
* *"¿Qué pasos se deben seguir en caso de un pinchazo accidental con aguja?"* 💉
* *"¿Cuáles son los requisitos de ingreso para una cirugía programada?"* 📝

**Ejemplo de flujo de respuesta real:**

> **Usuario:** ¿Cómo se procede ante una sospecha de paro cardiorrespiratorio en sala de espera?
> **MedQuery AI:** De acuerdo con la Sección 2.1 del *Manual de Emergencias de la Clínica (2025)*, se debe activar inmediatamente el 'Código Azul'. El personal de enfermería más cercano debe iniciar compunciones torácicas y solicitar el desfibrilador externo automático (DEA) en un tiempo menor a 60 segundos mientras arriba el equipo de reanimación. ⏱️

---

## 🚀 Despliegue

La aplicación se encuentra desplegada en **Streamlit Community Cloud**, conectada directamente a este repositorio de GitHub. El procesamiento y fragmentación de los documentos se realiza de manera local/estática para resguardar la privacidad de los manuales institucionales, mientras que la consulta se resuelve mediante llamadas seguras a la API de Groq utilizando variables de entorno protegidas (*Secrets*).

---

## 👤 Autor

**[Tu Nombre Aquí]**

*Desarrollador de Soluciones de IA | Proyecto de Startup Ficticia*

[🔗 Visita mi perfil en GitHub](https://www.google.com/search?q=https://github.com/tu-usuario)

---

## 📄 Licencia

Este proyecto fue desarrollado con fines educativos dentro del marco del Challenge Alura Agente. Los documentos utilizados en la demostración son de carácter ficticio/simulado para la validación de la tecnología RAG.
