from PIL import Image
import io

async def sticker_to_image(file: bytes) -> bytes:
    """Converts a sticker file (likely webp) to a PNG image."""
    try:
        with Image.open(io.BytesIO(file)) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            output_buffer = io.BytesIO()
            img.save(output_buffer, format='PNG')
            return output_buffer.getvalue()
    except Exception as e:
        print(f"Error converting sticker to image: {e}")
        return None