import asyncio
import os
import logging
from aiogram import Bot
from aiogram.types import FSInputFile
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Проверка наличия OpenCV для получения информации о видео
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning(
        "OpenCV не установлен. Для получения размеров видео "
        "установите: pip install opencv-python"
    )


def get_video_info(video_path: str):
    """
    Получает информацию о видео: ширину, высоту, длительность.
    """
    if not CV2_AVAILABLE:
        msg = "OpenCV не установлен. Установите: pip install opencv-python"
        logger.warning(msg)
        return None, None, None

    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error("Не удалось открыть видео файл")
            return None, None, None

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = int(frame_count / fps) if fps > 0 else None

        cap.release()
        return width, height, duration
    except Exception as e:
        logger.error(f"Ошибка при получении информации о видео: {e}")
        return None, None, None


async def upload_video(chat_id: str, video_path: str, bot_token: str):
    """
    Отправляет видео в указанный чат и возвращает его file_id.
    Сохраняет оригинальный размер и качество видео.
    """
    bot = None
    try:
        # Проверка существования файла
        if not os.path.exists(video_path):
            logger.error(f"Файл {video_path} не найден!")
            return None

        # Получаем информацию о размере файла
        file_size = os.path.getsize(video_path)
        size_mb_orig = file_size / (1024 * 1024)
        logger.info(f"Оригинальный размер файла: {size_mb_orig:.2f} MB")

        # Получаем информацию о видео (размеры, длительность)
        width, height, duration = get_video_info(video_path)
        if width and height:
            logger.info(f"📐 Оригинальные размеры видео: {width}x{height}")
        if duration:
            logger.info(f"⏱ Длительность видео: {duration} сек")

        # Инициализация бота
        bot = Bot(token=bot_token)

        logger.info(f"Отправка видео {video_path} в чат {chat_id}...")
        msg = "💡 Используем send_video с явными размерами для качества!"
        logger.info(msg)
        video_file = FSInputFile(video_path)

        # Отправка видео с явными параметрами для сохранения качества
        # Явно указываем размеры видео, если они известны
        if width and height:
            logger.info(f"✅ Указываем размеры: {width}x{height}")
            if duration:
                message = await bot.send_video(
                    chat_id=chat_id,
                    video=video_file,
                    width=width,
                    height=height,
                    duration=duration,
                    supports_streaming=True
                )
            else:
                message = await bot.send_video(
                    chat_id=chat_id,
                    video=video_file,
                    width=width,
                    height=height,
                    supports_streaming=True
                )
        elif duration:
            message = await bot.send_video(
                chat_id=chat_id,
                video=video_file,
                duration=duration,
                supports_streaming=True
            )
        else:
            message = await bot.send_video(
                chat_id=chat_id,
                video=video_file,
                supports_streaming=True
            )

        if message.video:
            logger.info("✅ Видео успешно отправлено!")
            logger.info(f"📋 File ID: {message.video.file_id}")
            sent_width = message.video.width
            sent_height = message.video.height
            logger.info(
                f"📐 Размеры отправленного видео: {sent_width}x{sent_height}"
            )

            # Проверяем, сохранились ли размеры
            if width and height:
                if sent_width == width and sent_height == height:
                    logger.info("✅ Размеры сохранены без изменений!")
                else:
                    logger.warning(
                        f"⚠️ Размеры изменились: было {width}x{height}, "
                        f"стало {sent_width}x{sent_height}"
                    )

            if message.video.file_size:
                size_mb = message.video.file_size / (1024 * 1024)
                logger.info(f"📦 Размер файла: {size_mb:.2f} MB")
            else:
                logger.info("📦 Размер файла: не указан")

            if message.video.duration:
                logger.info(f"⏱ Длительность: {message.video.duration} сек")

            # Выводим file_id и параметры для копирования
            print("\n" + "="*50)
            print(f"VIDEO_FILE_ID={message.video.file_id}")
            if width and height:
                print(f"VIDEO_WIDTH={width}")
                print(f"VIDEO_HEIGHT={height}")
            if duration:
                print(f"VIDEO_DURATION={duration}")
            print("="*50 + "\n")
            logger.info("💡 Добавьте эти значения в .env файл")

            return message.video.file_id
        else:
            logger.error("❌ Не удалось получить file_id видео.")
            return None

    except Exception as e:
        logger.error(f"❌ Ошибка при отправке видео: {e}", exc_info=True)
        return None
    finally:
        # Правильное закрытие сессии бота
        if bot:
            await bot.session.close()


async def main():
    """Главная функция для запуска скрипта."""
    # Получение токена бота
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        msg = "❌ BOT_TOKEN не найден! Создайте файл .env с токеном бота."
        logger.error(msg)
        return

    # Получение ID чата
    CHAT_ID = os.getenv('MY_CHAT_ID')
    if not CHAT_ID:
        logger.error("❌ MY_CHAT_ID не найден! Добавьте его в .env файл.")
        logger.info("💡 Вы можете получить свой chat_id у бота @userinfobot")
        return

    # Путь к видео
    VIDEO_PATH = "files/video1.mp4"

    # Отправка видео
    file_id = await upload_video(CHAT_ID, VIDEO_PATH, BOT_TOKEN)

    if file_id:
        logger.info(f"✅ Успешно! File ID сохранен: {file_id}")
    else:
        logger.error("❌ Не удалось получить file_id")

if __name__ == "__main__":
    asyncio.run(main())
