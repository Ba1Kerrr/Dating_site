import os
import magic
from fastapi import HTTPException, UploadFile
from pathlib import Path

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
UPLOAD_DIR = Path("templates/static")

def validate_image(file: UploadFile) -> str:
    """Валидация загружаемого файла"""
    # Проверка расширения
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Invalid file type")
    
    # Проверка размера
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 5MB)")
    
    # Проверка MIME-type (защита от переименованных exe)
    content = file.file.read(2048)
    file.file.seek(0)
    mime = magic.from_buffer(content, mime=True)
    if not mime.startswith('image/'):
        raise HTTPException(400, "File is not an image")
    
    # Генерация безопасного имени
    import uuid
    safe_name = f"{uuid.uuid4().hex}{ext}"
    return safe_name