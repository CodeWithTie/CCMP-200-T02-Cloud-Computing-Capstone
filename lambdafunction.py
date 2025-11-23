import boto3
from PIL import Image
import io

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Example expects event keys: source_bucket, source_key, destination_bucket
    source_bucket = event.get("source_bucket")
    source_key = event.get("source_key")
    destination_bucket = event.get("destination_bucket")

    if not source_bucket or not source_key or not destination_bucket:
        return {"status": "error", "message": "Missing source_bucket, source_key, or destination_bucket in event."}

    destination_key = f"thumbnail-{source_key}"

    # 1. Download the original image
    original_image_obj = s3.get_object(Bucket=source_bucket, Key=source_key)
    original_image_data = original_image_obj["Body"].read()

    # 2. Resize the image
    image = Image.open(io.BytesIO(original_image_data))
    image.thumbnail((200, 200))  # create 200x200 thumbnail

    buffer = io.BytesIO()
    # Use PNG fallback if image.format is None
    img_format = image.format if image.format else "PNG"
    image.save(buffer, format=img_format)
    buffer.seek(0)

    # 3. Upload resized image (preserve content type)
    content_type = original_image_obj.get("ContentType", f"image/{img_format.lower()}")
    s3.put_object(
        Bucket=destination_bucket,
        Key=destination_key,
        Body=buffer,
        ContentType=content_type
    )

    return {
        "status": "success",
        "thumbnail_key": destination_key,
        "destination_bucket": destination_bucket
    }
