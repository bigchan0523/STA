from PIL import Image, ImageOps, ImageChops
import os

input_path = r'c:\ai리터러시\Gemini_Generated_Image_cpzxkfcpzxkfcpzx.png'
output_path = r'c:\ai리터러시\STA-3.0.0\assets\sta_icon.ico'

if not os.path.exists(input_path):
    print(f"Error: {input_path} not found.")
    exit(1)

img = Image.open(input_path).convert('RGBA')

# 여백 제거 (Trim white space)
# 배경색이 거의 흰색이므로 (255, 255, 255)와의 차이를 이용
bg = Image.new(img.mode, img.size, (255, 255, 255, 255))
diff = ImageChops.difference(img, bg)
bbox = diff.getbbox()

if bbox:
    # 약간의 여유(padding)를 주기 위해 bbox를 약간 확장 (선택 사항)
    # 여기서는 꽉 채우기 위해 그대로 사용하거나 아주 약간만 패딩 추가
    cropped = img.crop(bbox)
else:
    cropped = img

# 정삼각형/정사각형 비율 맞추기
width, height = cropped.size
new_size = max(width, height)
final_img = Image.new("RGBA", (new_size, new_size), (255, 255, 255, 0)) # 투명 배경

# 중앙 배치
paste_x = (new_size - width) // 2
paste_y = (new_size - height) // 2
final_img.paste(cropped, (paste_x, paste_y), cropped)

# 아이콘 사이즈 설정
icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
final_img.save(output_path, format='ICO', sizes=icon_sizes)

# 검증용 PNG 저장
verify_path = r'c:\ai리터러시\STA-3.0.0\assets\verify_icon.png'
final_img.save(verify_path)

print(f'New ICO generated successfully at {output_path} with trimmed margins!')
print(f'Verification image saved at {verify_path}')