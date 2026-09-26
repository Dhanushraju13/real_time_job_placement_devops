import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://placement:placement@db:5432/placement"
)

# Ensure psycopg 3 driver is used when standard postgresql:// is provided
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "placement_super_secret_jwt_key_2026_devops_platform_secure_token"
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# Initial Admin user seeded if not existing
INITIAL_ADMIN_NAME = os.getenv("INITIAL_ADMIN_NAME", "System Admin")
INITIAL_ADMIN_EMAIL = os.getenv("INITIAL_ADMIN_EMAIL", "admin@placement.edu")
INITIAL_ADMIN_PASSWORD = os.getenv("INITIAL_ADMIN_PASSWORD", "Admin@123")
