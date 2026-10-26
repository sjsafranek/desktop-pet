from PIL import Image

SCALING = 2

# Resampling.NEAREST is perfect for retro pixel art. 
# Use Image.Resampling.LANCZOS for smooth, high-res graphics.  
IMAGE_RESAMPLING_ALGORITHM = Image.Resampling.NEAREST
