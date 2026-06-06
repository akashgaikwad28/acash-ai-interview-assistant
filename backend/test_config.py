import os
os.environ["ENVIRONMENT"] = "production"
os.environ["SECRET_KEY"] = "dev-secret-key-123"
os.environ["ADMIN_TOKEN"] = "dev-admin-token-123"
os.environ["GEMINI_API_KEY"] = "gemini-key-123"
os.environ["GOOGLE_CALENDAR_ID"] = "akash.gaikwad9945@gmail.com"
os.environ["GOOGLE_CALENDAR_CLIENT_ID"] = "client-id-123"
os.environ["GOOGLE_CALENDAR_CLIENT_SECRET"] = "client-secret-123"
os.environ["GOOGLE_CALENDAR_REFRESH_TOKEN"] = "refresh-token-123"
os.environ["CORS_ORIGINS"] = "https://acash-ai-interview-assistant.vercel.app"

from app.core.config import get_settings

try:
    settings = get_settings()
    print("Success! CORS origins parsed as:", settings.cors_origins)
except Exception as e:
    import traceback
    traceback.print_exc()
