from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pathlib import Path
from PIL import Image
from io import BytesIO
from models.user import User
from core.database import db
from bson import ObjectId
import os
from core.middleware import get_current_user
router = APIRouter()

# Image upload route
@router.post("/upload/{context_id}")
async def upload_image(context_id: str, file: UploadFile = File(...), user: User = Depends(get_current_user)):
    try:
        # Validate context ID with user ID
        context_collection = db.get_collection("contexts")
        context = await context_collection.find_one({
            "_id": ObjectId(context_id),
            "user_id": ObjectId(user.id)
        })

        if not context:
            raise HTTPException(status_code=403, detail="You do not have permission to upload to this context")

        # Define the base upload folder path
        base_upload_folder = Path("upload")
        user_folder = base_upload_folder / str(user.id)
        context_folder = user_folder / str(context_id)
        context_folder.mkdir(parents=True, exist_ok=True)  # Create directories if they don't exist

        existing_files = list(context_folder.glob("*"))
        next_index = len(existing_files) + 1

        # Define the image file path
        image_path = context_folder / f"{next_index}"

        # Process and save the image
        try:
            image = Image.open(BytesIO(await file.read()))
            image = image.convert("RGB")  # Convert image to RGB to avoid issues with transparency
            image.save(image_path, "PNG", quality=85)  # Save the image as PNG
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing the image: {str(e)}")

        # Generate the relative image URL
        image_url = f"/upload/{user.id}/{context_id}/{next_index}"

        await context_collection.update_one(
            {"_id": ObjectId(context_id)}, 
            {"$push": {"images": image_url}} 
        )

        return {
            "msg": "Image uploaded successfully",
            "file_path": str(image_path),
            "image_url": image_url
        }

    except HTTPException as e:
        # Re-raise any HTTPExceptions that were raised during the process
        raise e
    except Exception as e:
        # Catch any unexpected exceptions
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
