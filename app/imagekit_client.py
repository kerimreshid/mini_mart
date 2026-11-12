import os

from dotenv import load_dotenv
from imagekitio import ImageKit

load_dotenv()

IMAGEKIT_PRIVATE_KEY = os.getenv("IMAGEKIT_PRIVATE_KEY")

if not IMAGEKIT_PRIVATE_KEY:
    raise ValueError("IMAGEKIT_PRIVATE_KEY is missing from .env")

imagekit = ImageKit(
    private_key=IMAGEKIT_PRIVATE_KEY
)

