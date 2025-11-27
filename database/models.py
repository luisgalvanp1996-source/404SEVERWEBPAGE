from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class DeviceClientInfo(Base):
    __tablename__ = "DeviceClientInfo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_agent = Column(String(500))
    platform = Column(String(200))
    language = Column(String(50))
    timezone = Column(String(100))
    screen_width = Column(Integer)
    screen_height = Column(Integer)
    available_width = Column(Integer)
    available_height = Column(Integer)
    color_depth = Column(Integer)
    pixel_ratio = Column(Float)
    touch_points = Column(Integer)
    orientation = Column(String(50))
    vendor = Column(String(200))
    hardware_concurrency = Column(Integer)
    memory_gb = Column(Float)
    connection_effective_type = Column(String(50))
    connection_rtt = Column(Integer)
    connection_downlink = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
