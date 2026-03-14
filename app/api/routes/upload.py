from fastapi import APIRouter, File, UploadFile
from app.services.s3_service import upload_image_to_s3

router = APIRouter()

@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    """
    Test API endpoint to upload an image to AWS S3.
    """
    if not file.content_type.startswith("image/"):
        return {"error": "File provided is not an image."}
        
    image_url = await upload_image_to_s3(file)
    
    return {
        "message": "Image uploaded successfully",
        "image_url": image_url
    }
