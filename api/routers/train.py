from fastapi import APIRouter, UploadFile, HTTPException, Form
from pathlib import Path
from typing import Optional
import os
import time

router = APIRouter()

UPLOAD_FOLDER = Path("uploads")
TEMP_FOLDER = Path("temp")
UPLOAD_FOLDER.mkdir(exist_ok=True)
TEMP_FOLDER.mkdir(exist_ok=True)
@router.post("/upload")
async def upload_chunk(
    file: UploadFile, 
    chunk_number: int = Form(...), 
    total_chunks: int = Form(...), 
    file_name: str = Form(...), 
    file_type: Optional[str] = Form("zip")
):
    try:
        temp_folder = TEMP_FOLDER /file_name
        temp_folder.mkdir(exist_ok=True)

        chunk_path = temp_folder /f"chunk_{chunk_number}"
        with open(chunk_path, "wb") as buffer:
            buffer.write(await file.read())

        if chunk_number == total_chunks:
            final_file_path = UPLOAD_FOLDER / file_name

            if final_file_path.exists():
                final_file_path.unlink()

            with open(final_file_path, "wb") as final_file:
                print('11')
                for i in range(1, total_chunks + 1):
                    chunk_file_path = temp_folder / f"chunk_{i}"
                    with open(chunk_file_path, "rb") as chunk_file:
                        print(f"Combining chunk {i}")
                        final_file.write(chunk_file.read())

            time.sleep(1) 
            for chunk_file in temp_folder.iterdir():
                chunk_file.unlink()
            temp_folder.rmdir()

            if file_type == "json":
                print(f"Processing JSON file: {final_file_path}")
            elif file_type == "zip":
                print(f"Processing ZIP file: {final_file_path}")

            return {"msg": "File uploaded and combined successfully", "file_path": str(final_file_path)}

        return {"msg": "Chunk uploaded successfully"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error processing chunk: {str(e)}")
