from supabase_client import supabase


def create_bucket(name: str):
    res = supabase.storage.create_bucket(name)
    print("Created bucket: ", res)


async def upload_file(file_path: str, bucket_name: str, storage_path: str):
    with open(file_path, "rb") as f:
        res = supabase.storage.from_(bucket_name).upload(file=f, path=storage_path, file_options={"content-type": "image/png"})
        print("Uploaded file: ", res)

        return res