import os

MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "password")
MONGODB_USER = os.getenv("MONGODB_USER", "user")
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_CLUSTER = os.getenv("MONGODB_CLUSTER", "Cluster0")
MONGODB_URI = f"mongodb+srv://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}/?retryWrites=true&w=majority&appName={MONGODB_CLUSTER}"
DB_NAME = os.getenv("DB_NAME", "0")
