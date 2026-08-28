import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

class UploadService:
    """
    Serviço centralizado para validação, armazenamento e exclusão segura de arquivos.
    """
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
    ALLOWED_DOC_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.webp'}

    @classmethod
    def save_image(cls, file: FileStorage, subfolder: str = "") -> str | None:
        """
        Salva uma imagem com validação de extensão e geração de nome seguro (UUID).
        Retorna o caminho relativo (ex: 'uploads/abc123.jpg') ou None se inválido.
        """
        if not file or not isinstance(file, FileStorage) or not file.filename:
            return None

        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in cls.ALLOWED_IMAGE_EXTENSIONS:
            return None

        filename = f"{uuid.uuid4().hex}{ext}"
        base_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join(current_app.root_path, 'static', 'uploads'))
        target_folder = os.path.join(base_folder, subfolder) if subfolder else base_folder
        os.makedirs(target_folder, exist_ok=True)

        full_path = os.path.join(target_folder, filename)
        file.save(full_path)

        if subfolder:
            return f"uploads/{subfolder}/{filename}"
        return f"uploads/{filename}"

    @classmethod
    def delete_file(cls, relative_path: str) -> bool:
        """
        Remove um arquivo do disco de forma segura.
        """
        if not relative_path:
            return False

        clean_path = relative_path.lstrip("/").replace("static/", "")
        static_root = os.path.join(current_app.root_path, "static")
        full_path = os.path.join(static_root, clean_path)

        try:
            if os.path.exists(full_path) and os.path.isfile(full_path):
                os.remove(full_path)
                return True
        except Exception as e:
            current_app.logger.error(f"Erro ao excluir arquivo {full_path}: {e}")
        return False
