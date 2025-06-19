from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

FILE_UPLOAD_SERVICE_URL = "http://file-upload-service:8000"
TYPING_INDICATOR_SERVICE_URL = "http://typing-indicator-service:8001"


@app.post("/upload/")
async def proxy_upload(request: Request):
    try:
        form = await request.form()
        files = [("files", (file.filename, await file.read(), file.content_type))
                 for file in form.getlist("files")]

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{FILE_UPLOAD_SERVICE_URL}/upload/", files=files)
            return JSONResponse(status_code=response.status_code, content=response.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files/{file_id}")
async def proxy_get_file(file_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FILE_UPLOAD_SERVICE_URL}/files/{file_id}")
        return JSONResponse(status_code=response.status_code, content=response.json())


@app.delete("/files/{file_id}")
async def proxy_delete_file(file_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{FILE_UPLOAD_SERVICE_URL}/files/{file_id}")
        return JSONResponse(status_code=response.status_code, content=response.json())


@app.get("/")
async def root():
    return {"message": "API Gateway is up"}



