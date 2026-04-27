from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    LLM_MODEL_NAME: str
    LLM_MODEL_PROVIDER: str
    LLM_API_KEY: str
    SPIFF_BASE_URL: str
    SPIFF_CLIENT_ID: str
    SPIFF_OPENID_SECRET_KEY: str
    KEYCLOAK_BASE_URL: str
    KEYCLOAK_REALM: str
    ORCH_S_CLIENT_ID: str
    ORCH_S_OPENID_SECRET: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()