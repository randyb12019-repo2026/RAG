import streamlit as st
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

st.set_page_config(page_title="RAG - Asistente Lumetra", page_icon="🤖", layout="centered")

from src.rag import rag_stream, MODELO_EMBED, MODELO_CHAT
from src.chunking import cargar_documentos, chunk_fijo_documentos, indexar
import chromadb
import ollama

TITLE = "🤖 Asistente Virtual Lumetra"
DESCRIPTION = "Sistema RAG que responde preguntas sobre la documentación interna de Lumetra usando IA generativa local."

EJEMPLOS = [
    "¿Qué días son presenciales obligatorios?",
    "¿Cómo solicito una formación?",
    "¿Cuál es el horario de soporte?",
    "¿Qué hago si no me llega el correo de restablecimiento?",
    "¿Cuánto presupuesto de formación tengo al año?",
]

if "ready" not in st.session_state:
    st.session_state.ready = False
    st.session_state.collection = None
if "messages" not in st.session_state:
    st.session_state.messages = []


def esperar_ollama(max_intentos=20, espera=3):
    for intento in range(max_intentos):
        try:
            ollama.list()
            return True
        except Exception:
            if intento == 0:
                st.info("⏳ Esperando a que Ollama esté listo...")
            time.sleep(espera)
    return False


def descargar_si_falta(modelo):
    try:
        local = [m["name"] for m in ollama.list()["models"]]
        if any(modelo in n for n in local):
            return True
    except Exception:
        pass
    with st.spinner(f"⬇️ Descargando {modelo}..."):
        try:
            ollama.pull(modelo)
            return True
        except Exception as e:
            st.error(f"Error descargando {modelo}: {e}")
            return False


def init():
    if not esperar_ollama():
        st.error("No se pudo conectar con Ollama.")
        st.stop()

    ok = all(descargar_si_falta(m) for m in [MODELO_EMBED, MODELO_CHAT])
    if not ok:
        st.error("No se pudieron descargar los modelos necesarios.")
        st.stop()

    db_path = "/data/chroma_lumetra"
    cliente = chromadb.PersistentClient(path=db_path)

    try:
        coleccion = cliente.get_collection("lumetras")
        if coleccion.count() == 0:
            raise ValueError("empty")
    except Exception:
        docs = cargar_documentos(str(BASE_DIR / "datos"))
        chunks, metas = chunk_fijo_documentos(docs)
        barra = st.progress(0, text="📚 Indexando documentos...")
        coleccion = indexar(
            chunks, metas, ruta_db=db_path,
            progress_callback=lambda a, t: barra.progress(a / t, text=f"📚 Indexando {a}/{t} chunks...")
        )
        barra.empty()
        st.success(f"✅ {len(chunks)} chunks indexados")

    st.session_state.collection = coleccion
    st.session_state.ready = True


def check_models():
    try:
        models = ollama.list()
        names = [m["name"] for m in models["models"]]
        has_embed = any(MODELO_EMBED in n for n in names)
        has_chat = any(MODELO_CHAT in n for n in names)
        return has_embed, has_chat
    except Exception:
        return False, False


def responder(prompt):
    return rag_stream(prompt, st.session_state.collection)


with st.sidebar:
    st.markdown("### ⚙️ Modelos")
    st.code(f"Embeddings: {MODELO_EMBED}")
    st.code(f"Chat: {MODELO_CHAT}")
    st.divider()
    st.markdown("### 💡 Preguntas de ejemplo")
    for q in EJEMPLOS:
        if st.button(q, use_container_width=True, type="tertiary"):
            st.session_state.clicked = q
    st.divider()
    st.markdown("### 📁 Documentos")
    st.caption("FAQ • Manual de producto • Onboarding • Política formación • Política teletrabajo")

st.title(TITLE)
st.markdown(DESCRIPTION)
st.divider()

if not st.session_state.ready:
    init()
    st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if "clicked" in st.session_state:
    prompt = st.session_state.pop("clicked")
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        respuesta = ""
        for token in responder(prompt):
            respuesta += token
            placeholder.markdown(respuesta + "▌")
        placeholder.markdown(respuesta)
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    st.rerun()

if prompt := st.chat_input("Escribe tu pregunta sobre Lumetra..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        respuesta = ""
        for token in responder(prompt):
            respuesta += token
            placeholder.markdown(respuesta + "▌")
        placeholder.markdown(respuesta)
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    st.rerun()
