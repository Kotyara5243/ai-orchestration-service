import time
import httpx
from app.configs.config import settings


class KeycloakTokenClient:
    """
    Fetches and caches a Keycloak access token using the OAuth2
    client credentials grant (service-to-service, no user interaction).

    Usage:
        token_client = KeycloakTokenClient()
        token = await token_client.get_token()
        headers = {"Authorization": f"Bearer {token}"}

    The token is cached in memory and refreshed automatically when it
    is within TOKEN_EXPIRY_BUFFER_SECONDS of expiring.
    """

    TOKEN_EXPIRY_BUFFER_SECONDS = 30

    def __init__(self):
        self._token: str | None = None
        self._expires_at: float = 0.0

    @property
    def _token_url(self) -> str:
        return (
            f"{settings.KEYCLOAK_BASE_URL.rstrip('/')}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token"
        )

    def _is_token_valid(self) -> bool:
        return (
            self._token is not None
            and time.monotonic() < self._expires_at - self.TOKEN_EXPIRY_BUFFER_SECONDS
        )

    async def get_token(self) -> str:
        """
        Returns a valid access token, fetching a new one from Keycloak
        if the cached token is missing or about to expire.
        """
        if self._is_token_valid():
            return self._token

        payload = {
            "grant_type": "password",
            "client_id": settings.SPIFF_CLIENT_ID,
            "client_secret": settings.SPIFF_OPENID_SECRET_KEY,
            "username": "agent_test",
            "password": "test",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._token_url,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            data = response.json()

        self._token = data["access_token"]
        self._expires_at = time.monotonic() + data.get("expires_in", 300)
        return self._token

    async def get_auth_headers(self) -> dict[str, str]:
        """ Returns Authorization headers."""
        token = await self.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }