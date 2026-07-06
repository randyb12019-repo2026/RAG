import subprocess
import time
import sys
import socket
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent
TEMP_DIR = BASE / "_gif_frames"
OUTPUT_DIR = BASE / "_demo"
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ── Helper: kill leftover process on port ──────────────
def liberar_puerto(puerto):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ocupado = s.connect_ex(("127.0.0.1", puerto)) == 0
    s.close()
    if ocupado:
        import psutil
        for conn in psutil.net_connections():
            if conn.laddr.port == puerto and conn.pid:
                p = psutil.Process(conn.pid)
                p.terminate()
                p.wait(timeout=5)
                time.sleep(2)
                break

# ── 1. Start Streamlit ─────────────────────────────────
print("Starting Streamlit (dark theme)...")
liberar_puerto(8513)

proc = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "app.py",
     "--server.port=8513", "--server.headless=true", "--theme.base=dark"],
    cwd=str(BASE), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
time.sleep(10)

frames = []

def shot(nombre, espera=1.5):
    time.sleep(espera)
    ruta = TEMP_DIR / f"{nombre}.png"
    page.screenshot(path=str(ruta))
    frames.append(ruta)
    print(f"  [{len(frames)}] {nombre}")

def click_ejemplo(texto_parcial):
    for btn in page.query_selector_all("button"):
        try:
            if texto_parcial.lower() in btn.inner_text().lower():
                btn.click()
                print(f"  -> Click: {btn.inner_text()[:50]}")
                return True
        except:
            continue
    return False

print("Opening browser...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 900})

    page.goto("http://localhost:8513", wait_until="networkidle", timeout=60000)
    shot("01_cargando", 2)

    try:
        page.wait_for_selector("div[data-testid='stChatInput']", timeout=120000)
        print("  App ready")
    except Exception as e:
        print(f"  Warning: {e}")
    shot("02_listo", 2)

    # ── All 5 example questions ─────────────────────────
    preguntas = [
        ("presenciales", "03a"),
        ("formación", "04a"),
        ("soporte", "05a"),
        ("restablecimiento", "06a"),
        ("presupuesto", "07a"),
    ]

    for i, (palabra, prefijo) in enumerate(preguntas):
        click_ejemplo(palabra)
        # Clear any previous chat input text
        try:
            page.locator("div[data-testid='stChatInput'] textarea").fill("")
        except:
            pass
        shot(f"{prefijo}_click", 2)
        time.sleep(12)
        shot(f"{prefijo}_respondiendo")
        time.sleep(10)
        shot(f"{prefijo}_respuesta")

    # ── Typed question in chat input ────────────────────
    print("  Typing custom question...")
    pregunta_manual = "¿Qué hago si no recuerdo mi contraseña?"
    try:
        input_area = page.locator("div[data-testid='stChatInput'] textarea")
        input_area.click()
        input_area.fill(pregunta_manual)
        shot("08_escrito", 1)
        input_area.press("Enter")
        print("  Question submitted")
    except Exception as e:
        print(f"  Error typing: {e}")
        shot("08_error", 1)

    shot("09_enviado", 2)
    time.sleep(15)
    shot("10_respondiendo_manual")
    time.sleep(15)
    shot("11_respuesta_manual")

    browser.close()

print(f"\nTotal frames: {len(frames)}")

# ── 2. Create GIF ──────────────────────────────────────
images = []
for f in sorted(frames, key=lambda x: x.stem):
    img = Image.open(f).convert("RGB")
    images.append(img)

gif_path = OUTPUT_DIR / "demo_rag.gif"
# durations for each frame (ms): loading, ready, then 3 shots per question x 5 + 3 for typed
durations = [3000, 2000] + [1500, 2500, 3000] * 5 + [2000, 1500, 2500, 3000]
images[0].save(
    gif_path,
    save_all=True,
    append_images=images[1:],
    duration=durations[:len(images)],
    loop=0,
)
print(f"GIF creado: {gif_path}")

# ── 3. Cleanup ─────────────────────────────────────────
proc.terminate()
import shutil
shutil.rmtree(TEMP_DIR, ignore_errors=True)
