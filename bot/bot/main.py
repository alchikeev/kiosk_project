import logging
import os
import json
import requests
from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv
from .sessions import save_session, get_kiosk_by_session
from aiogram.types import InputFile

api_url = "http://127.0.0.1:5000/upload"  # локальный API киоска

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def handle_start(message: types.Message):
    if message.get_args():
        session_id = message.get_args()

        if session_id.startswith("print_") or session_id.startswith("kiosk"):
            # Режим печати
            kiosk_id = session_id.split("_")[1] if "_" in session_id else session_id
            save_session(message.from_user.id, kiosk_id)
            await message.answer(f"✅ Аппарат {kiosk_id} найден. Пожалуйста, отправьте PDF или DOCX файл для печати.")

        elif session_id.startswith("scan_"):
            try:
                scan_sessions_path = "/home/test/Документы/1/kiosk_core/scan_sessions.json"
                with open(scan_sessions_path, "r", encoding="utf-8") as f:
                    sessions = json.load(f)

                session = sessions.get(session_id)
                if not session:
                    await message.answer("⚠️ Сессия не найдена.")
                    return

                if session.get("used"):
                    await message.answer("⚠️ Этот QR-код уже был использован.")
                    return

                file_path = session.get("file_path")
                if not file_path or not os.path.exists(file_path):
                    await message.answer("❌ Файл не найден.")
                    return

                await message.answer_document(InputFile(file_path), caption="📎 Ваш сканированный документ")

                # Отметим как использованный
                session["used"] = True
                sessions[session_id] = session
                with open(scan_sessions_path, "w", encoding="utf-8") as f:
                    json.dump(sessions, f, indent=2, ensure_ascii=False)

            except Exception as e:
                await message.answer(f"❌ Ошибка: {e}")

        else:
            await message.answer("⚠️ Неизвестный формат QR-кода.")
    else:
        await message.answer("Привет! Пожалуйста, отсканируйте QR-код у аппарата.")


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_file(message: types.Message):
    user_id = message.from_user.id
    kiosk_id = get_kiosk_by_session(user_id)
    if not kiosk_id:
        await message.answer("⚠ Сессия не найдена или устарела. Пожалуйста, повторите через QR-код у аппарата.")
        return

    document = message.document
    file_path = f"data/files/{document.file_name}"
    await document.download(destination_file=file_path)
    await message.answer(f"✅ Файл получен и будет отправлен на печать в аппарат {kiosk_id}.")

    try:
        with open(file_path, "rb") as f:
            files = {"file": (document.file_name, f)}
            response = requests.post(api_url, files=files)

        if response.status_code == 200:
            await message.answer("✅ Файл отправлен на печать")
        else:
            await message.answer("❌ Ошибка при передаче файла")
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке: {e}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
