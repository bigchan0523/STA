import math
import os
from PIL import Image, ImageDraw

def get_star_points(center, outer_radius, inner_radius):
    points = []
    # 5 pointed star has 10 points (outer and inner)
    for i in range(10):
        radius = outer_radius if i % 2 == 0 else inner_radius
        angle = math.radians(i * 36 - 90)  # Start at the top point (-90 degrees)
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        points.append((x, y))
    return points

def create_perfect_icon():
    canvas_size = 1024
    # Create transparent background
    image = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # 1. Draw Rounded Rectangle (White Background)
    # Give a tiny margin (e.g. 5 pixels) to prevent anti-aliasing clipping
    margin = 5
    rect_shape = [margin, margin, canvas_size - margin, canvas_size - margin]
    radius = canvas_size // 6  # Novela style curvature
    draw.rounded_rectangle(rect_shape, radius=radius, fill=(255, 255, 255, 255))

    # 2. Draw Blue Star
    star_center = (canvas_size // 2, canvas_size // 2)
    # Outer radius proportional to canvas to look large but balanced
    outer_radius = 320 
    inner_radius = 140
    star_color = (0, 120, 215, 255) # Bright Blue similar to the user photo
    
    star_points = get_star_points(star_center, outer_radius, inner_radius)
    draw.polygon(star_points, fill=star_color)

    # 3. Save as ICO
    output_path = r'c:\ai리터러시\STA-3.0.0\assets\sta_icon.ico'
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    image.save(output_path, format='ICO', sizes=icon_sizes)

    # 4. Save verification PNG
    verify_path = r'c:\ai리터러시\STA-3.0.0\assets\verify_icon.png'
    image.save(verify_path)
    
    print(f"Perfect icon created at {output_path}")
    print(f"Verification image saved at {verify_path}")

if __name__ == "__main__":
    create_perfect_icon()
