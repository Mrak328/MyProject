import os
from PIL import Image
from typing import Tuple, Optional
from app.core.config import settings


class ImageService:
    """Сервис для обработки изображений"""

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    MAX_SIZE = (1920, 1080)  # Максимальный размер
    THUMBNAIL_SIZE = (300, 200)  # Размер превью

    @staticmethod
    def is_allowed_extension(filename: str) -> bool:
        """Проверка разрешенного расширения"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in ImageService.ALLOWED_EXTENSIONS

    @staticmethod
    def get_image_info(filepath: str) -> dict:
        """Получить информацию об изображении"""
        with Image.open(filepath) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "size": os.path.getsize(filepath),
                "mode": img.mode
            }

    @staticmethod
    def resize_image(
            input_path: str,
            output_path: str,
            max_size: Tuple[int, int] = MAX_SIZE
    ) -> bool:
        """Изменение размера изображения"""
        try:
            with Image.open(input_path) as img:
                # Сохраняем пропорции
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(output_path, quality=85, optimize=True)
            return True
        except Exception as e:
            print(f"Error resizing image: {e}")
            return False

    @staticmethod
    def create_thumbnail(
            input_path: str,
            output_path: str,
            size: Tuple[int, int] = THUMBNAIL_SIZE
    ) -> bool:
        """Создание миниатюры"""
        try:
            with Image.open(input_path) as img:
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(output_path, quality=70, optimize=True)
            return True
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return False

    @staticmethod
    def get_optimized_filename(filename: str, prefix: str = "") -> str:
        """Создание оптимизированного имени файла"""
        name, ext = os.path.splitext(filename)
        if prefix:
            return f"{prefix}_{name}{ext}"
        return f"{name}_optimized{ext}"


image_service = ImageService()