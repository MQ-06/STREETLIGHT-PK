import piexif
from PIL import Image
import os

def inject_exif(image_path, lat=31.5204, lon=74.3587):
    print(f"Injecting EXIF + GPS ({lat}, {lon}) into {image_path}...")
    img = Image.open(image_path)
    
    # Helper to convert decimal to rational
    def to_rational(num):
        abs_num = abs(num)
        d = int(abs_num)
        m = int((abs_num - d) * 60)
        s = int((abs_num - d - m/60) * 3600 * 100)
        return ((d, 1), (m, 1), (s, 100))

    # Create dummy EXIF data with GPS
    exif_dict = {
        "0th": {
            piexif.ImageIFD.Make: u"Samsung",
            piexif.ImageIFD.Model: u"SM-G991B",
            piexif.ImageIFD.Software: u"G991BXXU5CVA9",
            piexif.ImageIFD.DateTime: u"2026:05:04 03:45:00",
        },
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: u"2026:05:04 03:45:00",
            piexif.ExifIFD.LensModel: u"Samsung S21 Main Camera",
        },
        "GPS": {
            piexif.GPSIFD.GPSLatitudeRef: 'N' if lat >= 0 else 'S',
            piexif.GPSIFD.GPSLatitude: to_rational(lat),
            piexif.GPSIFD.GPSLongitudeRef: 'E' if lon >= 0 else 'W',
            piexif.GPSIFD.GPSLongitude: to_rational(lon),
        }
    }
    
    exif_bytes = piexif.dump(exif_dict)
    img.save(image_path, exif=exif_bytes)
    print("Done!")

# Inject into both test images
inject_exif(r"C:\Users\HP\Documents\fyp\STREETLIGHT-PK\backend\pothole_test.png")
inject_exif(r"C:\Users\HP\Documents\fyp\STREETLIGHT-PK\backend\trash_test.png")
