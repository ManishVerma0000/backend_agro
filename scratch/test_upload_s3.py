import asyncio
import os
import sys
import io
from dotenv import load_dotenv

# Add cwd to sys.path to resolve app modules
sys.path.append(os.getcwd())

from app.services.s3_service import upload_image_to_s3

class MockUploadFile:
    def __init__(self, file, filename, content_type):
        self.file = file
        self.filename = filename
        self.content_type = content_type

async def test_upload():
    load_dotenv()
    print("--- Loaded Environment Variables ---")
    print(f"AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID')}")
    print(f"AWS_REGION: {os.getenv('AWS_REGION')}")
    print(f"S3_BUCKET_NAME: {os.getenv('S3_BUCKET_NAME')}")
    print("------------------------------------")
    
    # 1x1 transparent PNG file bytes
    dummy_image_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc`0\x00"
        b"\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    file_like = io.BytesIO(dummy_image_bytes)
    
    mock_file = MockUploadFile(
        file=file_like,
        filename="test_verification_image.png",
        content_type="image/png"
    )
    
    print("Attempting to upload mock image to S3 (private)...")
    try:
        url = await upload_image_to_s3(mock_file)
        print("SUCCESS! Private image uploaded successfully.")
        print(f"Uploaded Image URL: {url}")
    except Exception as e:
        print("FAILED! Private S3 upload failed.")
        import traceback
        traceback.print_exc()

    # Now let's inspect the bucket configuration (Public Access Block, Policy, etc.)
    print("\nInspecting S3 Bucket Configuration...")
    try:
        import boto3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
        bucket_name = os.getenv("S3_BUCKET_NAME")
        
        # 1. Get Public Access Block
        try:
            pab = s3_client.get_public_access_block(Bucket=bucket_name)
            print("Public Access Block settings:")
            print(pab.get('PublicAccessBlockConfiguration'))
        except Exception as e:
            print(f"Could not get Public Access Block settings: {e}")
            
        # 2. Get Bucket Policy status
        try:
            policy_status = s3_client.get_bucket_policy_status(Bucket=bucket_name)
            print(f"Bucket Policy Public Status: {policy_status.get('PolicyStatus')}")
        except Exception as e:
            print(f"Could not get Bucket Policy status: {e}")

        # 3. Get Bucket Policy
        try:
            policy = s3_client.get_bucket_policy(Bucket=bucket_name)
            print("Bucket Policy:")
            print(policy.get('Policy'))
        except Exception as e:
            print(f"Could not get Bucket Policy: {e}")
            
    except Exception as e:
        print(f"Failed to inspect bucket: {e}")

if __name__ == "__main__":
    asyncio.run(test_upload())
