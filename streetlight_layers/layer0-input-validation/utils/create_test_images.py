"""
Test Image Generator for Layer 0 Input Validation
Creates synthetic test images with various quality issues for testing validation logic.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2
from pathlib import Path
import random


class TestImageGenerator:
    """Generate test images with controlled quality characteristics."""
    
    def __init__(self, output_dir: str = "test_images"):
        """
        Initialize the test image generator.
        
        Args:
            output_dir: Base directory for saving test images
        """
        self.output_dir = Path(output_dir)
        self.create_directories()
    
    def create_directories(self):
        """Create output directory structure."""
        subdirs = ['good', 'blurry', 'dark', 'bright', 'low_res']
        
        for subdir in subdirs:
            dir_path = self.output_dir / subdir
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {dir_path}")
    
    def create_textured_pattern(self, width: int, height: int) -> np.ndarray:
        """
        Create a textured pattern with edges for blur detection.
        
        Args:
            width: Image width
            height: Image height
            
        Returns:
            Numpy array with RGB image
        """
        # Create base image with gradient
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add color gradient background
        for y in range(height):
            r = int(100 + (y / height) * 100)
            g = int(150 - (y / height) * 50)
            b = int(200 - (y / height) * 100)
            image[y, :] = [b, g, r]  # BGR format
        
        # Add geometric patterns for edge detection
        # Vertical lines
        for x in range(0, width, 40):
            cv2.line(image, (x, 0), (x, height), (255, 255, 255), 2)
        
        # Horizontal lines
        for y in range(0, height, 40):
            cv2.line(image, (0, y), (width, y), (255, 255, 255), 2)
        
        # Add circles
        num_circles = 5
        for i in range(num_circles):
            x = random.randint(50, width - 50)
            y = random.randint(50, height - 50)
            radius = random.randint(20, 50)
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            cv2.circle(image, (x, y), radius, color, 3)
        
        # Add rectangles
        num_rects = 3
        for i in range(num_rects):
            x1 = random.randint(0, width - 100)
            y1 = random.randint(0, height - 100)
            x2 = x1 + random.randint(50, 100)
            y2 = y1 + random.randint(50, 100)
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        
        return image
    
    def add_text_overlay(self, image: np.ndarray, text: str):
        """
        Add text overlay to image.
        
        Args:
            image: Input image as numpy array
            text: Text to overlay
        """
        # Convert to PIL for text rendering
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        
        # Use default font
        width, height = pil_image.size
        text_bbox = draw.textbbox((0, 0), text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (width - text_width) // 2
        y = height - text_height - 20
        
        # Draw text with shadow
        draw.text((x + 2, y + 2), text, fill=(0, 0, 0))
        draw.text((x, y), text, fill=(255, 255, 255))
        
        # Convert back to numpy array
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    def generate_good_image(self):
        """Generate a good quality image that should pass all checks."""
        print("\n📸 Generating GOOD quality image...")
        
        width, height = 800, 600
        image = self.create_textured_pattern(width, height)
        
        # Ensure good brightness
        mean_brightness = np.mean(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
        if mean_brightness < 80 or mean_brightness > 180:
            # Adjust brightness to middle range
            adjustment = 128 - mean_brightness
            image = np.clip(image.astype(np.int16) + adjustment, 0, 255).astype(np.uint8)
        
        image = self.add_text_overlay(image, "GOOD QUALITY")
        
        # Save as JPEG
        output_path = self.output_dir / "good" / "good_image.jpg"
        cv2.imwrite(str(output_path), image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        # Calculate and display stats
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        
        print(f"  ✓ Saved: {output_path}")
        print(f"  ✓ Resolution: {width}x{height}")
        print(f"  ✓ Blur score: {blur_score:.2f} (should be > 100)")
        print(f"  ✓ Brightness: {brightness:.2f} (should be 30-230)")
        
        return output_path
    
    def generate_blurry_image(self):
        """Generate a blurry image that should fail blur check."""
        print("\n📸 Generating BLURRY image...")
        
        width, height = 800, 600
        image = self.create_textured_pattern(width, height)
        
        # Apply heavy Gaussian blur
        image = cv2.GaussianBlur(image, (51, 51), 20)
        
        image = self.add_text_overlay(image, "BLURRY")
        
        # Save as JPEG
        output_path = self.output_dir / "blurry" / "blurry_image.jpg"
        cv2.imwrite(str(output_path), image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        # Calculate and display stats
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        
        print(f"  ✓ Saved: {output_path}")
        print(f"  ✓ Resolution: {width}x{height}")
        print(f"  ✗ Blur score: {blur_score:.2f} (should be < 100)")
        print(f"  ✓ Brightness: {brightness:.2f}")
        
        return output_path
    
    def generate_dark_image(self):
        """Generate a dark image that should fail brightness check."""
        print("\n📸 Generating DARK image...")
        
        width, height = 800, 600
        image = self.create_textured_pattern(width, height)
        
        # Make it very dark
        image = (image * 0.1).astype(np.uint8)
        
        image = self.add_text_overlay(image, "DARK")
        
        # Save as JPEG
        output_path = self.output_dir / "dark" / "dark_image.jpg"
        cv2.imwrite(str(output_path), image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        # Calculate and display stats
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        
        print(f"  ✓ Saved: {output_path}")
        print(f"  ✓ Resolution: {width}x{height}")
        print(f"  ✓ Blur score: {blur_score:.2f}")
        print(f"  ✗ Brightness: {brightness:.2f} (should be < 30)")
        
        return output_path
    
    def generate_bright_image(self):
        """Generate a very bright image that should fail brightness check."""
        print("\n📸 Generating BRIGHT image...")
        
        width, height = 800, 600
        # Create a bright base image
        image = np.full((height, width, 3), 240, dtype=np.uint8)
        
        # Add some darker patterns for contrast
        for x in range(0, width, 40):
            cv2.line(image, (x, 0), (x, height), (220, 220, 220), 2)
        
        for y in range(0, height, 40):
            cv2.line(image, (0, y), (width, y), (220, 220, 220), 2)
        
        # Add text
        image = self.add_text_overlay(image, "BRIGHT")
        
        # Save as JPEG
        output_path = self.output_dir / "bright" / "bright_image.jpg"
        cv2.imwrite(str(output_path), image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        # Calculate and display stats
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        
        print(f"  ✓ Saved: {output_path}")
        print(f"  ✓ Resolution: {width}x{height}")
        print(f"  ✓ Blur score: {blur_score:.2f}")
        print(f"  ✗ Brightness: {brightness:.2f} (should be > 230)")
        
        return output_path
    
    def generate_low_res_image(self):
        """Generate a low resolution image that should fail resolution check."""
        print("\n📸 Generating LOW RESOLUTION image...")
        
        width, height = 200, 200
        image = self.create_textured_pattern(width, height)
        
        image = self.add_text_overlay(image, "LOW RES")
        
        # Save as JPEG
        output_path = self.output_dir / "low_res" / "low_res_image.jpg"
        cv2.imwrite(str(output_path), image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        # Calculate and display stats
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        
        print(f"  ✓ Saved: {output_path}")
        print(f"  ✗ Resolution: {width}x{height} (should be < 300x300)")
        print(f"  ✓ Blur score: {blur_score:.2f}")
        print(f"  ✓ Brightness: {brightness:.2f}")
        
        return output_path
    
    def generate_all(self):
        """Generate all test images."""
        print("=" * 60)
        print("GENERATING TEST IMAGES FOR LAYER 0 VALIDATION")
        print("=" * 60)
        
        images = []
        images.append(self.generate_good_image())
        images.append(self.generate_blurry_image())
        images.append(self.generate_dark_image())
        images.append(self.generate_bright_image())
        images.append(self.generate_low_res_image())
        
        print("\n" + "=" * 60)
        print("✅ ALL TEST IMAGES GENERATED SUCCESSFULLY")
        print("=" * 60)
        print(f"\nTotal images created: {len(images)}")
        print(f"Output directory: {self.output_dir.absolute()}")
        print("\nTest images:")
        for img_path in images:
            print(f"  • {img_path}")
        print("\nYou can now use these images to test the validation API!")
        
        return images


def main():
    """Main entry point."""
    # Create generator
    generator = TestImageGenerator(output_dir="../test_images")
    
    # Generate all test images
    generator.generate_all()


if __name__ == "__main__":
    main()

