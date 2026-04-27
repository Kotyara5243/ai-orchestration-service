import asyncio
import json
import sys
from pathlib import Path

# Allow running from the project root without installing the package
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from app.configs.config import settings
from app.core.clients.keycloak.keycloak_client import KeycloakTokenClient
from app.core.clients.spiff.spiff_client import SpiffClient


async def main(process_model_id: str) -> None:
    print(f"Spiff base URL : {settings.SPIFF_BASE_URL}")
    print(f"Keycloak URL : {settings.KEYCLOAK_BASE_URL}")
    print(f"Realm : {settings.KEYCLOAK_REALM}")
    print(f"Client ID : {settings.SPIFF_CLIENT_ID}")
    print(f"Process model : {process_model_id}")
    print("-" * 50)
 
    token_client = KeycloakTokenClient()
 
    print("Fetching Keycloak token...")
    token = await token_client.get_token()
    print(f"Token obtained : {token}")
    print("-" * 50)
 
    spiff = SpiffClient(token_client=token_client)
 
    print(f"Fetching process model '{process_model_id}'...")
    result = await spiff.get_process_model(process_model_id)
 
    print("Response:\n")
    print(json.dumps(result, indent=2))

    primary_file = result["primary_file_name"]

    print(f"Fetching process model xml file '{process_model_id}', '{primary_file}'...")
    file_xml = await spiff.get_process_model_file(process_model_id, primary_file)

    print("Response: \n"+ file_xml['file_contents'])


if __name__ == "__main__":
    asyncio.run(main("aa:test"))