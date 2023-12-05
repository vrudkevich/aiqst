import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# import settings using explicit path to avoid relative import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa

connection_uri = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PWD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}"
if connection_uri.startswith("postgres://"):
    connection_uri = connection_uri.replace("postgres://", "postgresql://", 1)
if connection_uri.startswith("postgresql://"):
    connection_uri = connection_uri.replace(
        "postgresql://", "postgresql+psycopg2://", 1
    )

# print final connection string
print(f"Connecting to db... %s" % connection_uri)  # noqa

engine = create_engine(
    connection_uri,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)