import numpy as np
import ollama

MODELO_EMBED = "embeddinggemma:300m"
MODELO_CHAT = "llama3:latest"
SYSTEM_RAG = """Eres el asistente interno de Lumetra.
Responde SOLO con la información del CONTEXTO.
Si la respuesta no está en el contexto, di exactamente: "No encuentro esa información en la documentación".
Cita siempre el documento del que sacas cada dato, entre corchetes:  [nombre_del_archivo]"""


def preguntar(prompt, system=None):
    mensajes = []
    if system:
        mensajes.append({"role": "system", "content": system})
    mensajes.append({"role": "user", "content": prompt})
    opciones = {"temperature": 0}
    if "qwen" in MODELO_CHAT:
        opciones["think"] = False
    r = ollama.chat(model=MODELO_CHAT, messages=mensajes, options=opciones)
    return r["message"]["content"].strip()


def embed_documentos(textos):
    entrada = [f"title: none | text: {t}" for t in textos]
    return ollama.embed(model=MODELO_EMBED, input=entrada)["embeddings"]


def embed_consulta(texto):
    entrada = f"task: search result | query: {texto}"
    return ollama.embed(model=MODELO_EMBED, input=entrada)["embeddings"][0]


def coseno(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))


def rag(pregunta, coleccion, k=4, ver_contexto=False):
    from src.chunking import recuperar
    trozos = recuperar(pregunta, coleccion, k)
    contexto = "\n\n".join([f"[{fuente}]: {texto}" for texto, fuente in trozos])
    if ver_contexto:
        print("-" * 60, f"\n CONTEXTO RECUPERADO: \n\n{contexto}\n", "-" * 60)
    prompt = f"CONTEXTO:\n{contexto}\n\nPREGUNTA: {pregunta}"
    return preguntar(prompt, system=SYSTEM_RAG)
