from datetime import datetime

from database import LocationData, Session
from img_process import get_image_timestamp

image_path = "/Users/yuxianghe/Documents/AddLocationForPicFromCamWhtGPS/IMG_1204.JPG"
timestamp = get_image_timestamp(image_path)
target_timestamp = timestamp
target_timestamp = 1703590767
print(timestamp)
print(datetime.utcfromtimestamp(1703590767))
with Session() as session:
    before = (
        session.query(LocationData)
        .filter(LocationData.dateTime <= target_timestamp)
        .order_by(LocationData.dateTime.desc())
        .first()
    )
    print(before.dateTime)
