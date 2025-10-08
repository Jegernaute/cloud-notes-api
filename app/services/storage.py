from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Використовуємо service role key

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_file(bucket_name: str, file_name: str, data: bytes):
    """
    Завантажуємо файл у Supabase і повертаємо публічний URL.
    """
    supabase.storage.from_(bucket_name).upload(file_name, data)
    url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_name}"
    return url


def remove_file(bucket_name: str, file_path: str):
    """
    Видаляє файл із Supabase Storage.
    file_path - шлях всередині бакета, без назви bucket_name
    Наприклад: "2/uuid_filename.jpeg"
    """
    # Відправляємо як список
    response = supabase.storage.from_(bucket_name).remove([file_path])
    print("[DEBUG] Supabase remove response:", response)

