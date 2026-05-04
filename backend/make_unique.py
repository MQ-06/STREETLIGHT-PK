from PIL import Image, ImageDraw
import random
import os

def create_unique_image(source_path, target_path):
    img = Image.open(source_path)
    # Add a tiny 1x1 random color pixel to change the hash
    draw = ImageDraw.Draw(img)
    x = random.randint(0, img.width - 1)
    y = random.randint(0, img.height - 1)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    draw.point((x, y), fill=color)
    img.save(target_path)
    print(f"Created unique image at {target_path}")

if __name__ == "__main__":
    create_unique_image(
        r"C:\Users\HP\Documents\fyp\STREETLIGHT-PK\backend\pothole_test.png",
        r"C:\Users\HP\Documents\fyp\STREETLIGHT-PK\backend\pothole_test_unique.png"
    )
