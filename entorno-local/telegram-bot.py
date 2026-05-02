"""
Bot de Telegram que controla tu PC via Open Interpreter + Gemini 2.5 Pro.
Leer plan-entorno-local.html antes de correr este script.
"""

import asyncio
import io
import logging
import os
import threading
from pathlib import Path

from dotenv import load_dotenv
from PIL import ImageGrab
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))
GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Configurar Open Interpreter
# --------------------------------------------------------------------------- #
from interpreter import interpreter as oi

oi.llm.model       = "gemini/gemini-2.5-pro-preview-05-06"
oi.llm.api_key     = GEMINI_API_KEY
oi.os              = True     # OS Mode: ve la pantalla, controla mouse/teclado
oi.auto_run        = True     # No pide confirmación en cada paso
oi.llm.temperature = 0.1
oi.system_message += (
    "\nSiempre responde en español. "
    "Sé conciso en tus respuestas de texto al usuario. "
    "Cuando termines una tarea, confirmalo brevemente."
)

# Flag para cancelar tareas en curso
_cancel_flag = threading.Event()

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def is_authorized(update: Update) -> bool:
    return update.effective_user.id == AUTHORIZED_USER_ID


def take_screenshot() -> bytes:
    img = ImageGrab.grab()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def run_interpreter(prompt: str) -> str:
    _cancel_flag.clear()
    output_parts: list[str] = []

    for chunk in oi.chat(prompt, stream=True, display=False):
        if _cancel_flag.is_set():
            break
        if chunk.get("type") == "message" and chunk.get("content"):
            output_parts.append(chunk["content"])

    return "".join(output_parts).strip()


# --------------------------------------------------------------------------- #
# Handlers
# --------------------------------------------------------------------------- #

async def cmd_start(update: Update, _ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    await update.message.reply_text(
        "🤖 *Bot activo*\n\n"
        "Tu PC está lista para recibir órdenes.\n"
        "Escribime cualquier tarea y la ejecuto.\n\n"
        "Comandos disponibles:\n"
        "/status — estado del sistema\n"
        "/screenshot — foto de la pantalla\n"
        "/reset — limpiar conversación\n"
        "/stop — cancelar tarea en curso",
        parse_mode="Markdown",
    )


async def cmd_status(update: Update, _ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    await update.message.reply_text(
        "✅ Open Interpreter activo\n"
        "✅ Gemini 2.5 Pro conectado\n"
        "✅ OS Mode habilitado\n"
        f"✅ Bot autorizado para ID: {AUTHORIZED_USER_ID}"
    )


async def cmd_screenshot(update: Update, _ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    await update.message.reply_text("📸 Capturando pantalla...")
    try:
        img_bytes = await asyncio.get_event_loop().run_in_executor(
            None, take_screenshot
        )
        await update.message.reply_photo(
            photo=img_bytes,
            caption="📸 Pantalla actual de tu PC"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error al capturar: {e}")


async def cmd_reset(update: Update, _ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    oi.messages = []
    await update.message.reply_text("🔄 Conversación reiniciada.")


async def cmd_stop(update: Update, _ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        return
    _cancel_flag.set()
    await update.message.reply_text("⏹️ Tarea cancelada.")


async def handle_message(update: Update, _ctx: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update):
        await update.message.reply_text("⛔ No autorizado.")
        return

    prompt = update.message.text
    log.info("Tarea recibida: %s", prompt)

    await update.message.reply_text("⚙️ Ejecutando...")

    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None, run_interpreter, prompt
        )
        response = result if result else "✅ Tarea completada."
    except Exception as e:
        log.error("Error en interpreter: %s", e)
        response = f"❌ Error: {e}"

    # Telegram tiene límite de 4096 caracteres por mensaje
    if len(response) > 4000:
        for i in range(0, len(response), 4000):
            await update.message.reply_text(response[i:i+4000])
    else:
        await update.message.reply_text(response)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def validate_config() -> None:
    missing = []
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not AUTHORIZED_USER_ID:
        missing.append("TELEGRAM_USER_ID")
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if missing:
        raise ValueError(
            f"Faltan variables en el .env: {', '.join(missing)}\n"
            "Copiá .env.example a .env y completá los valores."
        )


def main() -> None:
    validate_config()

    print("🤖 Bot iniciado. Esperando mensajes de Telegram...")
    print("✅ Gemini 2.5 Pro conectado")
    print("✅ OS Mode habilitado")
    print(f"✅ Solo responde al usuario ID: {AUTHORIZED_USER_ID}")
    print("──── Ctrl+C para detener ────")

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start",      cmd_start))
    app.add_handler(CommandHandler("status",     cmd_status))
    app.add_handler(CommandHandler("screenshot", cmd_screenshot))
    app.add_handler(CommandHandler("reset",      cmd_reset))
    app.add_handler(CommandHandler("stop",       cmd_stop))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
