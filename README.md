
# 🚀 Background Remover 

A high-performance image background remover API built with FastAPI, using `rembg` and `transparent_background` for background removal. The API supports Supabase storage integration, Redis rate limiting, and CORS for secure cross-origin access. 

[!First Screenshot](./screenshots/fir.png)
[!Second Screenshot](./screenshots/sec.png)


## 🌟 Features  

- 🖼️ **Background Removal** – Removes image backgrounds using `rembg` or `transparent_background`.  
- 📡 **FastAPI & Async Processing** – High-performance API with async operations.  
- 📂 **Cloud Storage** – Images are uploaded to Supabase storage for easy access.  
- 🚀 **Rate Limiting** – Prevents API abuse using Redis-based `fastapi-limiter`.  
- 🔧 **Quality Selection** – Choose between `"low"` and `"high"` processing quality.  
- 🔄 **Automatic Cleanup** – Deletes temporary files after upload.  
- 🌍 **CORS Support** – Allows secure cross-origin API requests.  
- 📜 **Logging & Monitoring** – Structured logging for debugging and tracking.  

## 🛠️ Tech Stack  

- **Frontend** - Vite
- **FastAPI** – Web framework for building high-performance APIs.  
- **Rembg** – ML-based background removal for images.  
- **PIL (Pillow)** – Image processing and manipulation.  
- **Supabase Storage** – Cloud storage for processed images.  
- **Redis** – Used for rate limiting and caching.  
- **FastAPI-Limiter** – Manages request rate limits.  
- **CORS Middleware** – Handles cross-origin requests.  
- **Uvicorn** – ASGI server for running FastAPI.  
