from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.responses import FileResponse
import os
import shutil
from typing import List
import uuid

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_file(files: List[UploadFile] = File(...)):
    uploaded_files = []
    for file in files:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        try:
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            uploaded_files.append({"filename": file.filename, "id": file_id})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading file: {e}")
        finally:
            file.file.close()
    return {"message": "Files uploaded successfully", "files": uploaded_files}


@app.get("/files/{file_id}")
async def download_file(file_id: str):
    for filename in os.listdir(UPLOAD_DIR):
        if filename.startswith(file_id + "_"):
            file_path = os.path.join(UPLOAD_DIR, filename)
            return FileResponse(file_path, filename=filename.split("_", 1)[1])
    raise HTTPException(status_code=404, detail="File not found")

@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    for filename in os.listdir(UPLOAD_DIR):
        if filename.startswith(file_id + "_"):
            file_path = os.path.join(UPLOAD_DIR, filename)
            try:
                os.remove(file_path)
                return {"message": "File deleted successfully"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error deleting file: {e}")
    raise HTTPException(status_code=404, detail="File not found")
