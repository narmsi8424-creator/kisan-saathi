from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str = "your_groq_api_key"
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    SUPABASE_URL: str = "your_supabase_url"
    SUPABASE_KEY: str = "your_supabase_key"
    SUPABASE_SERVICE_KEY: str = "your_service_key"
    WHATSAPP_TOKEN: str = "your_whatsapp_token"
    WHATSAPP_PHONE_ID: str = "your_phone_id"
    WHATSAPP_VERIFY_TOKEN: str = "kisan_saathi_verify_2024"
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"
    OPENAI_API_KEY: str = "your_openai_key"

    class Config:
        env_file = ".env"

settings = Settings()