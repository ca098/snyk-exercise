import os

SERVICE_HOST = os.environ.get("SERVICE_HOST", "127.0.0.1")
SERVICE_PORT = int(os.environ.get("SERVICE_PORT", "3000"))
SERVICE_LOG_LEVEL = os.environ.get("SERVICE_LOG_LEVEL", "info")

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
