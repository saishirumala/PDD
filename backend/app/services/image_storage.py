import os
import uuid
from typing import Tuple, Optional
from app.config import settings

class ImageStorageProvider:
    async def save_image(self, file_data: bytes, filename: str, mime_type: str) -> str:
        raise NotImplementedError()

    async def delete_image(self, file_url: str) -> None:
        raise NotImplementedError()


class LocalStorageProvider(ImageStorageProvider):
    def __init__(self, upload_dir: str = settings.UPLOAD_DIR):
        self.upload_dir = upload_dir
        # Ensure uploads folder exists in parent or relative path
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_image(self, file_data: bytes, filename: str, mime_type: str) -> str:
        # Resolve file extension
        ext = os.path.splitext(filename)[1].lower()
        if not ext:
            if "png" in mime_type:
                ext = ".png"
            elif "webp" in mime_type:
                ext = ".webp"
            else:
                ext = ".jpg"
                
        # Create unique filename
        unique_name = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(self.upload_dir, unique_name)
        
        with open(file_path, "wb") as buffer:
            buffer.write(file_data)
            
        # Return URL relative path
        # In main.py we will mount static files directory under /uploads/
        return f"/uploads/{unique_name}"

    async def delete_image(self, file_url: str) -> None:
        if not file_url or not file_url.startswith("/uploads/"):
            return
            
        # Extract filename from URL path
        filename = file_url.split("/")[-1]
        file_path = os.path.join(self.upload_dir, filename)
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete local file {file_path}: {str(e)}")


class ImageStorageService:
    def __init__(self, provider: Optional[ImageStorageProvider] = None):
        self.provider = provider or LocalStorageProvider()

    def validate_image(self, filename: str, file_size: int, content_type: str) -> Tuple[bool, str]:
        # Size limit validation
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            return False, f"File size exceeds the limit of {settings.MAX_UPLOAD_SIZE_MB}MB."

        # MIME type validation
        allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
        if content_type.lower() not in allowed_types:
            return False, "Unsupported file format. Supported types: JPG, JPEG, PNG, WEBP."

        # File extension validation
        allowed_exts = [".jpg", ".jpeg", ".png", ".webp"]
        ext = os.path.splitext(filename)[1].lower()
        if ext not in allowed_exts:
            return False, "Unsupported file extension."

        return True, ""

    async def save(self, file_data: bytes, filename: str, mime_type: str) -> str:
        return await self.provider.save_image(file_data, filename, mime_type)

    async def delete(self, file_url: str) -> None:
        await self.provider.delete_image(file_url)

# Helper function to initialize storage service
def get_storage_service() -> ImageStorageService:
    return ImageStorageService()
