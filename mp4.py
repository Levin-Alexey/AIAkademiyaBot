import asyncio
import os
from aiogram import Bot
from aiogram.types import FSInputFile

# --- НАСТРОЙКИ ---
BOT_TOKEN = "" # Твой токен
MY_CHAT_ID = 525944420  # Твой цифровой ID (можно узнать у @userinfobot)
VIDEO_FILENAME = "video.mp4" # Имя твоего файла (должен лежать рядом)
# -----------------

async def upload_video_note():
    # Проверяем, есть ли файл
    if not os.path.exists(VIDEO_FILENAME):
        print(f"❌ Ошибка: Файл {VIDEO_FILENAME} не найден!")
        return

    print("⏳ Начинаю загрузку видео-кружочка...")
    
    bot = Bot(token=BOT_TOKEN)

    try:
        # Самый важный момент: мы отправляем файл именно методом send_video_note
        video_file = FSInputFile(VIDEO_FILENAME)
        
        # Отправляем
        sent_message = await bot.send_video_note(chat_id=MY_CHAT_ID, video_note=video_file)
        
        # Получаем ID
        file_id = sent_message.video_note.file_id
        
        print("\n" + "="*50)
        print("✅ УСПЕХ! Видео отправлено.")
        print("Вот твой ID для вставки в код Cloudflare:")
        print("-" * 20)
        print(file_id)
        print("-" * 20)
        print("="*50 + "\n")

    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        print("Совет: Убедитесь, что видео квадратное (1:1) и меньше 1 минуты.")
    
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(upload_video_note())