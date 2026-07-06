import time
from pathlib import Path

import chromadb
import ollama

from src.rag import embed_consulta, MODELO_EMBED


def cargar_documentos(ruta="datos"):
    docs = {}
    for ruta_archivo in sorted(Path(ruta).glob("*.txt")):
        docs[ruta_archivo.name] = ruta_archivo.read_text(encoding="utf-8")
    return docs


def chunk_parrafos(docs, min_caracteres=40):
    chunks, metadatos = [], []
    for nombre, texto in docs.items():
        for parrafo in texto.split("\n\n"):
            parrafo = parrafo.strip()
            if len(parrafo) > min_caracteres:
                chunks.append(parrafo)
                metadatos.append({"fuente": nombre})
    return chunks, metadatos


def chunk_fijo(texto, tamano=300, solapamiento=50, min_caracteres=40):
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fin = min(inicio + tamano, len(texto))
        fragmento = texto[inicio:fin].strip()
        if len(fragmento) > min_caracteres:
            chunks.append(fragmento)
        inicio += tamano - solapamiento
    return chunks


def chunk_fijo_documentos(docs, tamano=300, solapamiento=50, min_caracteres=40):
    chunks, metadatos = [], []
    for nombre, texto in docs.items():
        for fragmento in chunk_fijo(texto, tamano, solapamiento, min_caracteres):
            chunks.append(fragmento)
            metadatos.append({"fuente": nombre})
    return chunks, metadatos


def _embed_uno(texto, cliente_ollama, reintentos=3):
    for intento in range(reintentos):
        try:
            entrada = f"title: none | text: {texto}"
            return cliente_ollama.embed(model=MODELO_EMBED, input=[entrada])["embeddings"][0]
        except Exception as e:
            if intento == reintentos - 1:
                raise
            time.sleep(2)


def indexar(chunks, metadatos, nombre_coleccion="lumetras", ruta_db="chroma_lumetra", progress_callback=None):
    cliente = chromadb.PersistentClient(path=ruta_db)
    coleccion = cliente.get_or_create_collection(
        nombre_coleccion, metadata={"hnsw:space": "cosine"}
    )

    cliente_ollama = ollama.Client(timeout=120)
    todos_embeddings = []
    total = len(chunks)
    for i, chunk in enumerate(chunks):
        embs = _embed_uno(chunk, cliente_ollama)
        todos_embeddings.append(embs)
        if progress_callback:
            progress_callback(i + 1, total)

    coleccion.upsert(
        ids=[f"chunk_{i}" for i in range(total)],
        documents=chunks,
        embeddings=todos_embeddings,
        metadatas=metadatos,
    )
    return coleccion


def recuperar(pregunta, coleccion, k=4):
    res = coleccion.query(query_embeddings=[embed_consulta(pregunta)], n_results=k)
    return list(zip(res["documents"][0], [m["fuente"] for m in res["metadatas"][0]]))
