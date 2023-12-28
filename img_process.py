import datetime

import piexif
from PIL import Image
from PIL.ExifTags import TAGS


def get_image_timestamp(image_path):
    img = Image.open(image_path)
    exif_data = img._getexif()

    # Find the original date/time tag
    for tag, value in exif_data.items():
        decoded_tag = TAGS.get(tag, tag)
        if decoded_tag == "DateTimeOriginal":
            return datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")

    return None


def write_geolocation_to_image(image_path, location):
    lat, lon = location
    exif_dict = piexif.load(image_path)

    # Convert lat and lon to the EXIF format
    exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = "N" if lat >= 0 else "S"
    exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = decimal_to_dms(lat)
    exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = "E" if lon >= 0 else "W"
    exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = decimal_to_dms(lon)

    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, image_path)


def decimal_to_dms(deg):
    d = int(deg)
    m = int((deg - d) * 60)
    s = int((deg - d - m / 60) * 3600 * 100)
    return [(d, 1), (m, 1), (s, 100)]
