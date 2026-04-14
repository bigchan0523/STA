import sys
import subprocess
import os

def install_pillow():
    print("Pillow not found. Attempting to install...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        return True
    except Exception as e:
        print(f"Failed to install Pillow: {e}")
        return False

try:
    from PIL import Image, ImageDraw, ImageOps
except ImportError:
    if install_pillow():
        from PIL import Image, ImageDraw, ImageOps
    else:
        print("Could not load Pillow. Exiting.")
        sys.exit(1)

input_image_path = r"c:\ai리터러시\sta.png"
output_icon_path = r"c:\ai리터러시\SAT-3.0.0\assets\sta_icon.ico"

def create_rounded_icon(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Input image not found: {input_path}")
        return

    img = Image.open(input_path).convert("RGBA")
    
    # 1. Create a square background (size = max dimension)
    width, height = img.size
    size = max(width, height)
    
    # Use a bit higher resolution for processing then downscale
    canvas_size = 1024 
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 0))
    
    # 2. Resize original image to fit within canvas_size (maintaining aspect ratio)
    # Give some padding (e.g. 10% from edges)
    padding = int(canvas_size * 0.1)
    inner_size = canvas_size - (padding * 2)
    
    img.thumbnail((inner_size, inner_size), Image.Resampling.LANCZOS)
    
    # Center the logo on the white square background
    # (Actually Novela look often has a solid white rounded background)
    bg = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 255))
    
    paste_x = (canvas_size - img.width) // 2
    paste_y = (canvas_size - img.height) // 2
    bg.paste(img, (paste_x, paste_y), img if img.mode == 'RGBA' else None)
    
    # 3. Apply Rounded Corners Mask (Squircle/Rounded Rect style)
    mask = Image.new("L", (canvas_size, canvas_size), 0)
    draw = ImageDraw.Draw(mask)
    
    # Radius (Novela style is roughly 1/5th to 1/6th of the size)
    radius = canvas_size // 6
    draw.rounded_rectangle((0, 0, canvas_size, canvas_size), radius=radius, fill=255)
    
    final_img = ImageOps.fit(bg, (canvas_size, canvas_size))
    final_img.putalpha(mask)
    
    # 4. Save as ICO with multiple sizes
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    final_img.save(output_path, format='ICO', sizes=icon_sizes)
    print(f"Improved icon saved at {output_path}")

create_rounded_icon(input_image_path, output_icon_path)
