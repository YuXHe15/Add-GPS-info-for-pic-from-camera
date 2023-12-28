import csv
import datetime

from database import LocationData, Session, LATEST_PRIMARY_KEY

MAX_INTERVAL_SECONDS = 600
ACCURACY_THRESHOLD = 50  # Define the accuracy threshold


def parse_gpx_data(gpx_file_path):
    # Mocked data structure: list of tuples (timestamp, latitude, longitude)
    return [
        (datetime.datetime(2023, 12, 25, 10, 30, 0), 40.7128, -74.0060),
        (datetime.datetime(2023, 12, 25, 11, 0, 0), 40.7580, -73.9855),
        # ... more data points
    ]


def find_closest_points(timestamp, gpx_data):
    before, after = None, None
    for i in range(len(gpx_data) - 1):
        if gpx_data[i][0] <= timestamp <= gpx_data[i + 1][0]:
            before = gpx_data[i]
            after = gpx_data[i + 1]
            break
    return before, after


def linear_interpolation(before, after, target_time):
    total_time_diff = (after[0] - before[0]).total_seconds()
    time_diff = (target_time - before[0]).total_seconds()

    lat_diff = after[1] - before[1]
    lon_diff = after[2] - before[2]

    interpolated_lat = before[1] + (lat_diff * (time_diff / total_time_diff))
    interpolated_lon = before[2] + (lon_diff * (time_diff / total_time_diff))

    return interpolated_lat, interpolated_lon


def interpolate_location(session, target_timestamp):
    # Convert target timestamp to UNIX if it's a datetime object

    # Find the nearest locations before and after the target timestamp
    before = (
        session.query(LocationData)
        .filter(
            LocationData.dateTime <= target_timestamp,
            LocationData.accuracy <= ACCURACY_THRESHOLD,
        )
        .order_by(LocationData.dateTime.asc())
        .first()
    )

    after = (
        session.query(LocationData)
        .filter(
            LocationData.dateTime >= target_timestamp,
            LocationData.accuracy <= ACCURACY_THRESHOLD,
        )
        .order_by(LocationData.dateTime.asc())
        .first()
    )

    # If we found both neighbors, we can interpolate
    if before and after:
        # Perform linear interpolation
        if isinstance(target_timestamp, datetime.datetime):
            target_timestamp = int(target_timestamp.timestamp())
        before_time = int(
            datetime.datetime.strptime(before.dateTime, "%Y-%m-%d %H:%M:%S").timestamp()
        )
        after_time = int(
            datetime.datetime.strptime(after.dateTime, "%Y-%m-%d %H:%M:%S").timestamp()
        )
        if after_time - before_time > MAX_INTERVAL_SECONDS:
            diff_former = abs(target_timestamp - before_time)
            diff_latter = abs(after_time - target_timestamp)
            if diff_former < diff_latter:
                return before.latitude, before.longitude
            else:
                return after.latitude, after.longitude
        ratio = (target_timestamp - before_time) / (after_time - before_time)
        interpolated_latitude = (
            before.latitude + (after.latitude - before.latitude) * ratio
        )
        interpolated_longitude = (
            before.longitude + (after.longitude - before.longitude) * ratio
        )

        return interpolated_latitude, interpolated_longitude
    else:
        # Handling the case where there are no sufficient data points
        return None


import hashlib


def calculate_md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def has_csv_changed(csv_path, hash_store_path):
    current_hash = calculate_md5(csv_path)

    try:
        with open(hash_store_path, "r") as f:
            stored_hash = f.read()
    except FileNotFoundError:
        stored_hash = None

    if current_hash == stored_hash:
        print("CSV has not changed. No need to update the database.")
        return False  # CSV has not changed
    else:
        # CSV has changed, update the hash store
        print("CSV has changed. Updating the database...")
        update_latest_info(
            hash_store_path, current_hash, LATEST_PRIMARY_KEY
        )
        return True


def update_latest_info(hash_store_path, new_md5, new_latest_primary_key):
    with open(hash_store_path, "w") as f:
        f.write(f"{new_md5}\n{new_latest_primary_key}")


def get_latest_info(hash_store_path):
    try:
        with open(hash_store_path, "r") as f:
            md5, latest_primary_key = f.read().split("\n")
            return md5, int(latest_primary_key)
    except FileNotFoundError:
        return None, None


def get_latest_primary_key_from_csv(csv_path):
    try:
        with open(csv_path, "r") as csvfile:
            last_line = None
            for last_line in csvfile:
                pass  # Iterate to the end of the file

            if last_line:
                # Assuming dataTime is the first column in the CSV
                return int(last_line.split(",")[0])
            else:
                print("CSV file is empty.")
                return 0
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        return 0
