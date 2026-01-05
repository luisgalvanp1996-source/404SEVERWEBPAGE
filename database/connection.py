from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# ======================================================
# CARGAR VARIABLES DE ENTORNO
# ======================================================
load_dotenv()

# ----------------------
# SQL SERVER
# ----------------------
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_DRIVER = os.getenv("DB_DRIVER")

# ----------------------
# MONGODB
# ----------------------
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "404webpagedb")

# ======================================================
# VALIDACIONES
# ======================================================
if not all([DB_USER, DB_PASSWORD, DB_SERVER, DB_NAME, DB_DRIVER]):
    raise RuntimeError("❌ Faltan variables de entorno para SQL Server")

# ======================================================
# SQL SERVER - SQLALCHEMY
# ======================================================
password = quote_plus(DB_PASSWORD)
driver = quote_plus(DB_DRIVER)

DATABASE_URL = (
    f"mssql+pyodbc://{DB_USER}:{password}@{DB_SERVER}/{DB_NAME}"
    f"?driver={driver}"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()

# ======================================================
# MONGODB - PYMONGO
# ======================================================
mongo_client = MongoClient(
    host=MONGO_HOST,
    port=MONGO_PORT
)

mongo_db = mongo_client[MONGO_DB]

# ======================================================
# HELPERS (RECOMENDADO)
# ======================================================
def get_db():
    """Session SQL Server"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mongo_db():
    """MongoDB database"""
    return mongo_db
