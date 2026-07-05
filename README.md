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
**Última actualización:** 25 de junio de 2025  
**Licencia:** MIT — ver [LICENSE](./LICENSE)

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

## Stack

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.14 |
| Interfaz | Streamlit + Jupyter |
| Embeddings | Ollama — `embeddinggemma:300m` (dimensión 768) |
| Chat | Ollama — `llama3:latest` |
| Vector DB | ChromaDB (persistente local, similitud coseno) |
| Chunking | Por párrafos y por tamaño fijo (300 chars, solapamiento 50) |

## Requisitos

- [Ollama](https://ollama.com) instalado y corriendo
- Modelos descargados:
  ```bash
  ollama pull embeddinggemma:300m
  ollama pull llama3:latest
  ```
- Python 3.14+ con `pip`

## Instalación local

```bash
git clone <repo-url>
cd RAG

python -m venv venv
.\venv\Scripts\Activate   # Windows
# source venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
```

### Descargar modelos

```powershell
.\scripts\download_models.ps1   # Windows PowerShell
```

O manualmente:

```bash
ollama pull embeddinggemma:300m
ollama pull llama3:latest
```

## Uso

### Web App (Streamlit) — recomendado

```bash
streamlit run app.py
```

Abre `http://localhost:8501`. Interfaz de chat lista para hacer preguntas.

### Notebook

```bash
jupyter notebook notebooks\clase_rag.ipynb
```

Ejecuta las celdas en orden. El pipeline completo:
1. Verifica modelos instalados en Ollama
2. Prueba de chat básico
3. Exploración de embeddings (similitud coseno)
4. Carga los documentos `.txt` de `datos/`
5. Trocea en chunks (párrafos y tamaño fijo)
6. Indexa en ChromaDB
7. Recupera contexto (`recuperar`)
8. Responde preguntas usando RAG con citas de fuente

### Módulos Python (src/)

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

### Tests

```bash
python -m pytest tests/ -v
```

5 tests: carga, chunking por párrafos, chunking fijo, coseno, dimensión de embedding (768).

## Docker

```bash
docker compose up -d
```

Inicia dos contenedores:
- **ollama**: servidor de modelos (puerto `11434`)
- **streamlit**: app web RAG con el código montado (puerto `8501`)

La app descarga automáticamente los modelos de Ollama si no están presentes.

### Acceder a la app

Abrir `http://localhost:8501`.

---

## Deploy en Hugging Face Spaces

La app está preparada para desplegarse en **[Hugging Face Spaces](https://huggingface.co/spaces)** con Docker Compose.

### Pasos:

1. **Crea un Space** en https://huggingface.co/new-space
   - Name: `rag-lumetra` (o el que quieras)
   - License: `MIT`
   - Space SDK: **Docker**
   - Docker Template: **Blank**

2. **Sube el código** (el propio repo del proyecto):
   ```bash
   git remote add hf https://huggingface.co/spaces/TU_USUARIO/rag-lumetra
   git push hf main
   ```

3. **Configura el Space** (Settings > Space):
   - Hardware: al menos **2 vCPU · 16 GB RAM** (CPU basic es suficiente)
   - Container Age: `1 day` (para que no se duerma entre visitas)

4. **Primer arranque** (~10-15 min):
   La app descarga automáticamente los modelos de Ollama (`embeddinggemma:300m` + `llama3:latest`) y luego indexa los documentos. No requiere acción manual.

5. **¡Demo lista!** La app estará disponible en `https://TU_USUARIO-rag-lumetra.hf.space`

> **Nota**: La primera vez que alguien haga una pregunta, la app indexará los documentos automáticamente. Puede tardar ~1 minuto.

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
├── chroma_lumetra/              # ChromaDB persistente
├── notebooks/
│   └── clase_rag.ipynb          # Notebook principal del pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── LICENSE                      # MIT
└── README.md
```

## Notas

- El modelo `gemma4:e2b` fue reemplazado por `llama3:latest` por un error interno de carga de CLIP en Ollama para Windows.
- Todas las consultas sin respuesta en los documentos retornan: `"No encuentro esa información en la documentación"`.
- Los embeddings usan prefijos específicos (`title: none | text:` para documentos, `task: search result | query:` para consultas).

## Licencia

MIT — ver `LICENSE`.