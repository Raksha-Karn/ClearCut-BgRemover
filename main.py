import os
import uuid
from fastapi import FastAPI, HTTPException, File, UploadFile, Header, status, Depends
from pydantic import BaseModel
from io import BytesIO
from rembg import remove
from supabase_client import supabase
from utils import create_bucket, upload_file
from PIL import Image
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from functools import lru_cache
from fastapi_limiter.depends import RateLimiter
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

app = FastAPI()

load_dotenv()

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", 6379)
redis_url = f"redis://{redis_host}:{redis_port}"

@app.on_event("startup")
async def startup():
    logger.info("Starting application...")
    redis_instance = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_instance)
    logger.info("Redis connection established.")

if supabase:
    try:
        already_exists = supabase.storage.get_bucket(os.getenv("BUCKET_NAME"))
        logger.info("Bucket already exists")
    except Exception as e:
        logger.warning(f"Bucket not found: {str(e)}. Creating a new bucket...")
        create_bucket(os.getenv("BUCKET_NAME"))
        logger.info("Bucket created successfully.")
else:
    raise Exception("Supabase client not initialized")


origins = [
    "http://localhost:5173",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ImageQuality(BaseModel):
    quality: str


def get_supabase():
    return supabase


@lru_cache()
def get_remover():
    from transparent_background import Remover
    return Remover(resize='dynamic')


async def process_image(image: UploadFile, quality: str, supabase_client) -> JSONResponse:
    try:
        logger.info("Processing image with quality: %s", quality)
        image_bytes = await image.read()
        pil_image = Image.open(BytesIO(image_bytes)).convert('RGB')

        if quality == "low":
            output_image = remove(
                pil_image,
                alpha_matting=quality=="high",
            )
        else:
            remover = get_remover()
            output_image = remover.process(pil_image)

        img_byte_arr = BytesIO()
        output_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        temp_dir = os.path.join(os.getcwd(), 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        file_path = os.path.join(temp_dir, f"{quality}_{uuid.uuid4()}.png")
        storage_path = f"{quality}/{uuid.uuid4()}.png"

        with open(file_path, "wb") as f:
            f.write(img_byte_arr.getvalue())

        await upload_file(file_path, os.getenv("BUCKET_NAME"), storage_path)

        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info("Deleted file from folder")

            public_url = supabase_client.storage.from_(os.getenv("BUCKET_NAME")).get_public_url(storage_path)
            print(public_url)

        logger.info("Image processed successfully, saving to storage.")
        return JSONResponse(
            content={
                "message": "success",
                "image_url": public_url,
                "expiry": "1 hour"
            }
        )

    except Exception as e:
        logger.error("Error processing image: %s", str(e), exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Error processing image: {str(e)}")


@app.post("/remove-bg/", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def remove_background(
        image: UploadFile = File(...),
        quality: str = Header(...),
        supabase_client=Depends(get_supabase)
):
    logger.info("Received request to remove background with quality: %s", quality)
    if quality not in ["low", "high"]:
        logger.warning("Invalid quality value: %s", quality)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid quality value. Must be 'low' or 'high'.")

    return await process_image(image, quality, supabase_client)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)