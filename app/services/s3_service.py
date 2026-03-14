import boto3
import uuid
import os
from botocore.exceptions import NoCredentialsError, ClientError
from fastapi import UploadFile, HTTPException

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

async def upload_image_to_s3(file: UploadFile) -> str:
    """
    Uploads an image directly to the root of the configured S3 bucket.
    Returns the public URL of the uploaded image.
    """
    s3_client = get_s3_client()
    
    # Generate a unique file name to prevent collisions
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    try:
        bucket_name = os.getenv("S3_BUCKET_NAME")
        # Upload the file to S3
        s3_client.upload_fileobj(
            file.file,
            bucket_name,
            unique_filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not found.")
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")
        
    bucket_name = os.getenv("S3_BUCKET_NAME")
    # Construct the public URL for the uploaded S3 object
    bucket_location = s3_client.get_bucket_location(Bucket=bucket_name)
    region = bucket_location.get('LocationConstraint')
    if region is None:
        region = os.getenv("AWS_REGION", "us-east-1") # Default region if None
        
    image_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{unique_filename}"
    
    return image_url
