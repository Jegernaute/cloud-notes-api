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


