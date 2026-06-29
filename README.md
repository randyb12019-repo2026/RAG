# RAG — Asistente Virtual para Lumetra

Sistema de **Retrieval-Augmented Generation (RAG)** que permite a un modelo de lenguaje local responder preguntas sobre documentación interna de una empresa, usando **Ollama** para embeddings + chat y **ChromaDB** como base de datos vectorial.

## Arquitectura

```
Pregunta → Embeddings (embeddinggemma) → ChromaDB (búsqueda por similitud coseno)
                                              ↓
                                   Contexto recuperado (top-k chunks)
                                              ↓
                              Modelo de chat (gemma4) + prompt RAG
                                              ↓
                                         Respuesta
```

## Stack

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.14 |
| Notebook | Jupyter |
| Embeddings | Ollama — `embeddinggemma:300m` |
| Chat | Ollama — `gemma4:e2b` |
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

pip install -r requirements.txt
```

### Descargar modelos

```powershell
.\scripts\download_models.ps1   # Windows PowerShell
```

O manualmente:

```bash
ollama pull embeddinggemma:300m
ollama pull gemma4:e2b
```

## Uso

### Notebook (recomendado)

```bash
jupyter notebook notebooks\clase_rag.ipynb
```

Ejecuta las celdas en orden. El pipeline completo:
1. Carga los documentos `.txt` de `datos/`
2. Trocea en chunks (varias estrategias)
3. Indexa en ChromaDB
4. Responde preguntas usando RAG

### Módulos Python (src/)

Los módulos en `src/` pueden reutilizarse desde cualquier script:

```python
from src.chunking import cargar_documentos, chunk_parrafos, indexar
from src.rag import rag

docs = cargar_documentos()
chunks, metas = chunk_parrafos(docs)
coleccion = indexar(chunks, metas)
respuesta = rag("¿Qué días tengo que ir a la oficina?", coleccion)
print(respuesta)
```

### Tests

```bash
python -m pytest tests/ -v
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
├── src/                         # Módulos Python reutilizables
│   ├── __init__.py
│   ├── rag.py                   # Funciones core: preguntar, embed, coseno, RAG
│   └── chunking.py              # Estrategias de chunking (párrafos, tamaño fijo)
├── scripts/                     # Scripts auxiliares
│   └── download_models.ps1      # Descarga de modelos Ollama
├── tests/                       # Tests unitarios
│   ├── __init__.py
│   └── test_rag.py
├── datos/                       # Documentos de conocimiento
│   ├── faq_soporte.txt          # Preguntas frecuentes de soporte técnico
│   ├── manual_producto.txt      # Manual del producto Lumetra Insight
│   ├── onboarding.txt           # Guía de incorporación para nuevos empleados
│   ├── politica_formacion.txt   # Política de formación y presupuesto anual
│   └── politica_teletrabajo.txt # Política de teletrabajo y modelo híbrido
├── chroma_lumetra/              # Base de datos vectorial ChromaDB
│   ├── chroma.sqlite3
│   └── <uuid>/                  # Índice HNSW por colección
├── notebooks/                   # Notebooks de Jupyter
│   └── clase_rag.ipynb          # Notebook principal
├── Dockerfile                   # Imagen Docker para Jupyter
├── docker-compose.yml           # Orquestación Ollama + Jupyter
├── requirements.txt             # Dependencias del proyecto
├── .gitignore
├── LICENSE                      # Licencia MIT
└── README.md
```

## Licencia

Creado bajo licencia MIT. Ver `LICENSE`.