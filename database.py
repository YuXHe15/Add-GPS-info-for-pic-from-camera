import csv
from datetime import datetime

from sqlalchemy import BigInteger, Column, Float, Integer, String, create_engine, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class LocationData(Base):
    __tablename__ = "location_data"
    dataTime = Column(BigInteger, primary_key=True)  # UNIX timestamp as primary key
    dateTime = Column(String)  # Human-readable timestamp
    locType = Column(Integer)
    longitude = Column(Float)
    latitude = Column(Float)
    heading = Column(Integer)
    accuracy = Column(Integer)
    speed = Column(Float)
    distance = Column(Float)
    isBackForeground = Column(Integer)
    stepType = Column(Integer)
    altitude = Column(Float)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def get_latest_primary_key(session):
    latest_entry = session.query(func.max(LocationData.dataTime)).scalar()
    return int(latest_entry) if latest_entry is not None else 0


def import_csv_to_db(session, csv_path):
    with open(csv_path, "r") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            current_key = int(row["dataTime"])
            if current_key > LATEST_PRIMARY_KEY:
                location_entry = LocationData(**row)
                row["dateTime"] = datetime.fromtimestamp(int(row["dataTime"]))
                row["dataTime"] = int(row["dataTime"])
                location_entry = LocationData(**row)
                session.add(location_entry)
        session.commit()


# Adjust the database URI according to your environment
engine = create_engine("sqlite:///location_data.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
LATEST_PRIMARY_KEY = get_latest_primary_key(Session())
