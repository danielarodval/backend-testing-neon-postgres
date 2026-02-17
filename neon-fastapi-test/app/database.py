import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
from urllib.parse import urlparse

# Create an asynchronous engine using the DATABASE_URL from settings
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Create the async engine with SSL context
parsed_url = urlparse(settings.DATABASE_URL)
db_user = parsed_url.username
db_password = parsed_url.password
db_host = parsed_url.hostname
db_port = parsed_url.port
db_name = parsed_url.path[1:]

# Build host (include port only when present) to avoid 'None' literal
host_part = f"{db_host}:{db_port}" if db_port else db_host

# Construct the async database URL (no query params — SSL passed via connect_args)
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{host_part}/{db_name}"

# Create the async engine with SSL context
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    connect_args={"ssl": ssl_context},
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=True
)

# Create a declarative base class for defining models
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create a declarative base class for defining models
Base = declarative_base()

# Define a dependency to get the database session
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()