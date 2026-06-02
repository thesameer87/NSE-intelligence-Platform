import os
import pytest

# Inject required environment variables globally BEFORE any app code imports
os.environ["ANGEL_ONE_API_KEY"] = "test"
os.environ["ANGEL_ONE_CLIENT_ID"] = "test"
os.environ["ANGEL_ONE_PASSWORD"] = "test"
os.environ["SUPABASE_URL"] = "http://localhost"
os.environ["SUPABASE_KEY"] = "test"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/testdb"
os.environ["JWT_SECRET"] = "test"
os.environ["INTERNAL_API_TOKEN"] = "test"
os.environ["ENVIRONMENT"] = "development"
os.environ["SCHEDULER_INTERVAL_SECONDS"] = "5"
