from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Leer la cadena de conexión desde variables de entorno o desde config/settings.ini
# Ejemplo de env var: DATABASE_URL = "mssql+pyodbc://user:pass@SERVER/DB?driver=ODBC+Driver+17+for+SQL+Server"
DATABASE_URL = (
    "mssql+pyodbc://sa:Luis1996%40%40@SERVER404\\SERVERHOME/404webpagedb"
    "?driver=ODBC+Driver+17+for+SQL+Server"
)
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
