# import os
# from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
# from sqlalchemy.orm import declarative_base, sessionmaker
# from datetime import datetime, timezone

# Base = declarative_base()

# # Use absolute path to avoid relative path issues:
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DB_PATH = os.path.join(BASE_DIR, "results.db")

# engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)  # echo=True to see SQL logs
# Session = sessionmaker(bind=engine)

# class Result(Base):
#     __tablename__ = 'extractions'

#     id = Column(Integer, primary_key=True)
#     payee = Column(String)
#     amount = Column(Float)
#     amount_type = Column(String)
#     iban = Column(String)
#     created_at = Column(DateTime, default=datetime.now(timezone.utc))

# def save_to_db(data: dict):
#     session = Session()
#     try:
#         entry = Result(**data)
#         session.add(entry)
#         session.commit()
#     except Exception as e:
#         session.rollback()
#         print(f"💥 DB save error: {e}")
#         raise
#     finally:
#         session.close()

# # Create tables on import
# Base.metadata.create_all(engine)



import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
from sqlalchemy.orm import scoped_session

# Use absolute path to avoid relative path issues:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "results.db")

# 1. First create the engine
engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)  # echo=True to see SQL logs

# 2. Then create the Session factory
Session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()

class Result(Base):
    __tablename__ = 'extractions'

    id = Column(Integer, primary_key=True)
    payee = Column(String)
    amount = Column(Float)
    amount_type = Column(String)
    iban = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # Fixed: lambda for runtime evaluation

def save_to_db(data: dict):
    session = Session()
    try:
        entry = Result(**data)
        session.add(entry)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"💥 DB save error: {e}")
        raise
    finally:
        session.close()

# Create tables on import
Base.metadata.create_all(engine)