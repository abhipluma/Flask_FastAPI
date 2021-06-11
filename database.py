import os, sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PROJECT_DIR = os.path.join(BASE_DIR,'enterprise')
# load_dotenv(os.path.join(PROJECT_DIR, '.env'))
# sys.path.append(BASE_DIR)

host_server = os.environ.get('host_server', 'localhost')
db_server_port = os.environ.get('db_server_port', '5432')
database_name = os.environ.get('database_name', 'new_db')
db_username = os.environ.get('db_username', 'pluma_dev')
db_password = os.environ.get('db_password', 'pluma_dev')
ssl_mode = os.environ.get('ssl_mode','prefer')
DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(db_username, db_password, host_server, db_server_port, database_name, ssl_mode)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()