# RAG — Asistente Virtual para Lumetra

Sistema de **Retrieval-Augmented Generation (RAG)** que permite a un modelo de lenguaje local responder preguntas sobre documentación interna de una empresa, usando **Ollama** para embeddings + chat y **ChromaDB** como base de datos vectorial.

## Arquitectura

```
Pregunta → Embeddings (embeddinggemma) → ChromaDB (búsqueda por similitud coseno)
                                              ↓
                                   Contexto recuperado (top-k chunks)
                                              ↓
                              Modelo de chat (gemma4 / llama3) + prompt RAG
                                              ↓
                                         Respuesta
```

## Stack

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.14 |
| Notebook | Jupyter |
| Embeddings | Ollama — `embeddinggemma:300m` |
| Chat | Ollama — `gemma4:e2b` / `llama3:latest` |
| Vector DB | ChromaDB (persistente local) |
| Chunking | Por párrafos y por tamaño fijo (300 chars) |

## Requisitos

- [Ollama](https://ollama.com) instalado
- Modelos descargados:
  ```bash
  ollama pull embeddinggemma:300m
  ollama pull gemma4:e2b
  ```
- Python 3.14+ con `pip`

## Instalación local

```bash
git clone https://github.com/tuusuario/RAG.git
cd RAG

python -m venv venv
.\venv\Scripts\Activate   # Windows
# source venv/bin/activate  # Linux/macOS

pip install jupyter ollama chromadb numpy
```

## Uso

```bash
jupyter notebook clase_rag.ipynb
```

Ejecuta las celdas en orden. El pipeline completo:
1. Carga los documentos `.txt` de `datos/`
2. Trocea en chunks (varias estrategias)
3. Indexa en ChromaDB
4. Responde preguntas usando RAG

### Probar el asistente

```python
rag("¿Qué días tengo que ir a la oficina obligatoriamente?")
# → Los días presenciales obligatorios son martes y jueves [politica_teletrabajo.txt]
```

## Docker

### Requisitos

- Docker y Docker Compose instalados

### Levantar el entorno

```bash
docker compose up -d
```

Esto inicia dos contenedores:
- **ollama**: servidor de modelos (puerto `11434`)
- **jupyter**: Jupyter Notebook con el código (puerto `8888`)

### Descargar modelos dentro del contenedor

```bash
docker exec -it ollama ollama pull embeddinggemma:300m
docker exec -it ollama ollama pull gemma4:e2b
```

### Acceder al notebook

Abrir `http://localhost:8888` en el navegador.

## Estructura del proyecto

```
RAG/
├── datos/                    # Documentos de conocimiento
│   ├── faq_soporte.txt
│   ├── manual_producto.txt
│   ├── onboarding.txt
│   ├── politica_formacion.txt
│   └── politica_teletrabajo.txt
├── chroma_lumetra/           # Base de datos vectorial (ChromaDB)
├── clase_rag.ipynb           # Notebook principal
├── venv/                     # Entorno virtual (ignorado por git)
├── Dockerfile
├── docker-compose.yml
├── LICENSE
└── README.md
```

## Licencia

Distribuido bajo licencia MIT. Ver `LICENSE`.
