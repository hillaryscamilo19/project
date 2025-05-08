from motor.motor_asyncio import AsyncIOMotorClient # Mongo
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



#Conexion Con Sql Sever  
DATABASE_URL = (
    "mssql+pyodbc://TI-03\\MSSQLSERVERHILLA/ticked"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Crear el motor de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Establecer en False en producción
    pool_pre_ping=True
)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base para los modelos
Base = declarative_base()

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()