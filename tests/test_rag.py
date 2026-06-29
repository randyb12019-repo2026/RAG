from pathlib import Path

import numpy as np

from src.chunking import cargar_documentos, chunk_fijo, chunk_parrafos
from src.rag import coseno, embed_consulta, embed_documentos


def test_cargar_documentos():
    docs = cargar_documentos()
    assert len(docs) >= 4
    assert all(n.endswith(".txt") for n in docs.keys())


def test_chunk_parrafos():
    docs = {"test.txt": "Párrafo uno.\n\nPárrafo dos.\n\nPárrafo tres."}
    chunks, metas = chunk_parrafos(docs, min_caracteres=1)
    assert len(chunks) == 3
    assert metas[0]["fuente"] == "test.txt"


def test_chunk_fijo():
    texto = "A" * 1000
    chunks = chunk_fijo(texto, tamano=300, solapamiento=50)
    assert len(chunks) >= 3
    assert all(len(c) <= 300 for c in chunks)


def test_coseno():
    a = [1, 0, 0]
    b = [1, 0, 0]
    assert coseno(a, b) == 1.0
    assert np.isclose(coseno([1, 0], [0, 1]), 0.0)


def test_embed_dimension():
    vector = embed_consulta("prueba")
    assert len(vector) == 768
