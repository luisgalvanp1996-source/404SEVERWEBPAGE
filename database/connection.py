from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Cargar variables desde .env
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_DRIVER = os.getenv("DB_DRIVER")

if not all([DB_USER, DB_PASSWORD, DB_SERVER, DB_NAME, DB_DRIVER]):
    raise RuntimeError("Faltan variables de entorno para la conexión a la base de datos")

# Escapar password y driver (IMPORTANTE)
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
