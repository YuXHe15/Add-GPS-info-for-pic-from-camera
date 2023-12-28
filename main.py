import os
from datetime import datetime

from database import LATEST_PRIMARY_KEY, Session, import_csv_to_db
from gpx_process import has_csv_changed, interpolate_location
from img_process import get_image_timestamp, write_geolocation_to_image

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(ROOT_DIR, "backUpData.csv")
HASH_FILE = os.path.join(ROOT_DIR, "last_hash.txt")

with Session() as session:
    # Import data from CSV
    if has_csv_changed(
        CSV_FILE,
        HASH_FILE,
    ):
        import_csv_to_db(
            session,
            CSV_FILE,
        )

    # For each image
    photo_directory = "imgs"
    full_photo_directory = os.path.join(ROOT_DIR, photo_directory)
    photo_list = [
        os.path.join(full_photo_directory, file)
        for file in os.listdir(full_photo_directory)
        if file.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    for image_path in photo_list:
        timestamp = get_image_timestamp(image_path)
        location = interpolate_location(session, timestamp)

        if location:
            write_geolocation_to_image(image_path, location)
            print(f"Geolocation added to {image_path}")
        else:
            print(f"No geolocation data available for {image_path}")
