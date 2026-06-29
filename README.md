# RAG — Asistente Virtual para Lumetra

Sistema de **Retrieval-Augmented Generation (RAG)** que permite a un modelo de lenguaje local responder preguntas sobre documentación interna de una empresa, usando **Ollama** para embeddings + chat y **ChromaDB** como base de datos vectorial.

**Autor:** Randy Bonucci  
**BootCamp:** Data Analytics & IA — UpgradeHub  
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
| Notebook | Jupyter |
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

### Notebook (recomendado)

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
- **jupyter**: Jupyter Notebook con el código montado (puerto `8888`)

### Descargar modelos dentro del contenedor

```bash
docker exec -it ollama ollama pull embeddinggemma:300m
docker exec -it ollama ollama pull llama3:latest
```

### Acceder al notebook

Abrir `http://localhost:8888`.

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