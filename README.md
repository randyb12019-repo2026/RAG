---
title: RAG Lumetra
emoji: 👁
colorFrom: red
colorTo: pink
sdk: docker
sdk_version: "1"
app_file: app.py
pinned: false
license: mit
short_description: Asistente RAG con Ollama + ChromaDB
---

# RAG — Asistente Virtual para Lumetra

Sistema de **Retrieval-Augmented Generation (RAG)** que permite a un modelo de lenguaje local responder preguntas sobre documentación interna de una empresa, usando **Ollama** para embeddings + chat y **ChromaDB** como base de datos vectorial.

**Autor:** Randy Bonucci  
**BootCamp:** Data Analytics & IA — UpgradeHub  
**Licencia:** MIT — ver [LICENSE](./LICENSE)

---

## Stack

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.14 |
| Interfaz | Streamlit + Jupyter |
| Embeddings | Ollama — `embeddinggemma:300m` (dimensión 768) |
| Chat | Ollama — `llama3:latest` |
| Vector DB | ChromaDB (persistente local, similitud coseno) |
| Chunking | Por párrafos y por tamaño fijo (300 chars, solapamiento 50) |

## Arquitectura

```
Pregunta → Embeddings (embeddinggemma:300m) → ChromaDB (búsqueda coseno)
                                                    ↓
                                          Contexto recuperado (top-k chunks)
                                                    ↓
                                        Modelo de chat (llama3) + prompt RAG
                                                    ↓
                                                Respuesta
```

## Instalación

### Requisitos

- Python 3.14+
- [Ollama](https://ollama.com) instalado y corriendo
- Modelos descargados:

```bash
ollama pull embeddinggemma:300m
ollama pull llama3:latest
```

### Setup

```bash
git clone https://github.com/randyb12019-repo2026/RAG.git
cd RAG

python -m venv venv
.\venv\Scripts\Activate   # Windows
# source venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
```

## Uso

### Web App (Streamlit)

```bash
streamlit run app.py
```

Abre `http://localhost:8501`. La app descarga automáticamente los modelos de Ollama si no están presentes e indexa los documentos en el primer arranque.

### Notebook

```bash
jupyter notebook notebooks\clase_rag.ipynb
```

Ejecuta las celdas en orden para ver el pipeline completo:
1. Verifica modelos instalados en Ollama
2. Prueba de chat básico
3. Exploración de embeddings (similitud coseno)
4. Carga los documentos `.txt` de `datos/`
5. Trocea en chunks (párrafos y tamaño fijo)
6. Indexa en ChromaDB
7. Recupera contexto
8. Responde preguntas usando RAG con citas de fuente

### Módulos Python

```python
from src.chunking import cargar_documentos, chunk_parrafos, indexar
from src.rag import rag

docs = cargar_documentos()
chunks, metas = chunk_parrafos(docs)
coleccion = indexar(chunks, metas)
respuesta = rag("¿Qué días tengo que ir a la oficina?", coleccion)
print(respuesta)
# → "Los días presenciales obligatorios son martes y jueves [politica_teletrabajo.txt]"
```

## Tests

```bash
python -m pytest tests/ -v
```

5 tests: carga de documentos, chunking por párrafos, chunking por tamaño fijo, similitud coseno, dimensión de embedding (768).

## Despliegue

### Docker (local)

```bash
docker compose up -d
```

### Hugging Face Spaces

El proyecto está preparado para desplegarse en [Hugging Face Spaces](https://huggingface.co/spaces) con Docker Compose.

**Hardware recomendado:**

| Recurso | Mínimo | Recomendado |
|---|---|---|
| vCPU | 2 | 4+ |
| RAM | 8 GB | 16 GB |
| Disco | 10 GB | 20 GB |

> El primer arranque descarga los modelos de Ollama (`embeddinggemma:300m` + `llama3:latest`) e indexa los documentos automáticamente. Puede tardar ~10-15 min.

## Demo GIF

Genera una animación que recorre la app mostrando las 5 preguntas de ejemplo y una consulta escrita manualmente:

```powershell
pip install -r requirements-demo.txt
playwright install chromium
python capturar_gif.py
```

El GIF se genera en `_demo/demo_rag.gif`. Requiere **Ollama corriendo** con los modelos descargados.

## Estructura del proyecto

```
RAG/
├── src/                         # Módulos Python reutilizables
│   ├── __init__.py
│   ├── rag.py                   # Funciones core: preguntar, embed, coseno, RAG
│   └── chunking.py              # Estrategias de chunking + indexación ChromaDB
├── scripts/
│   └── download_models.ps1      # Descarga de modelos Ollama
├── tests/
│   ├── __init__.py
│   └── test_rag.py              # 5 tests unitarios
├── datos/                       # Documentos de conocimiento (5 .txt)
│   ├── faq_soporte.txt
│   ├── manual_producto.txt
│   ├── onboarding.txt
│   ├── politica_formacion.txt
│   └── politica_teletrabajo.txt
├── notebooks/
│   └── clase_rag.ipynb          # Notebook principal del pipeline
├── _demo/                       # GIF demo generado
│   └── demo_rag.gif
├── capturar_gif.py              # Script para generar GIF demo
├── requirements-demo.txt        # Dependencias para generar el GIF demo
├── chroma_lumetra/              # ChromaDB persistente
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Notas

- El modelo `gemma4:e2b` fue reemplazado por `llama3:latest` por un error interno de carga de CLIP en Ollama para Windows.
- Consultas sin respuesta en los documentos retornan: `"No encuentro esa información en la documentación"`.
- Los embeddings usan prefijos específicos (`title: none | text:` para documentos, `task: search result | query:` para consultas).

## Licencia

MIT — ver `LICENSE`.
