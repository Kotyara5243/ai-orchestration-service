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

PROCESS_MODEL_ID = "agentic-orchestration:test-model"


async def fetch_process_model_and_file(spiff: SpiffClient, process_model_id: str) :
    
    print(f"Fetching process model '{process_model_id}'...")
    result = await spiff.get_process_model(process_model_id)
 
    print("Response:\n")
    print(json.dumps(result, indent=2))

    primary_file = result["primary_file_name"]

    print(f"Fetching process model xml file '{process_model_id}', '{primary_file}'...")
    file_xml = await spiff.get_process_model_file(process_model_id, primary_file)

    print("Response: \n"+ file_xml['file_contents'])


async def fetch_process_instances(spiff: SpiffClient) :
    
    # columns = {"Header": "", "accessor": "", "filterable": False}

    payload = {"report_metadata" : {
        "columns" : [
            {"Header":"Id","accessor":"id","filterable":False},
            {"Header":"Process","accessor":"process_model_display_name","filterable":False},
            {"Header":"Status","accessor":"status","filterable":False}
        ],
        "filter_by": [{"field_name": "with_oldest_open_task", "field_value": True}],
        "order_by": []
    } }

    print(f"Fetching instances...")
    result = await spiff.get_process_instances(payload=payload)
    instances = result["results"]

    print("Response:\n")
    print(json.dumps(instances, indent=2))

    return instances


async def send_message(spiff: SpiffClient) :
    
    print(f"Fetching message models...")
    message_models = await spiff.get_message_models()
 
    print("Response:\n")
    print(json.dumps(message_models, indent=2))
    
    instances = await fetch_process_instances(spiff)
    
    waiting_instances = [instance for instance in instances if instance.get("status") == "waiting"]
    
    print("Response:\n")
    print(json.dumps(waiting_instances, indent=2))
    
    if len(waiting_instances) is not 0 :
        process_instance_waiting_id = waiting_instances[0]["id"]

        print(f"Fetching message instances...")
        message_instances = await spiff.get_messages(process_instance_waiting_id)
 
        print("Response:\n")
        print(json.dumps(message_instances, indent=2))
        
        print(f"Trigerring message event...")
        result = await spiff.trigger_message_event(message_instances["results"][0]["name"], {})
    
        print("Response:\n")
        print(json.dumps(result, indent=2))




async def main() -> None:
    print(f"Spiff base URL : {settings.SPIFF_BASE_URL}")
    print(f"Keycloak URL : {settings.KEYCLOAK_BASE_URL}")
    print(f"Realm : {settings.KEYCLOAK_REALM}")
    print(f"Client ID : {settings.SPIFF_CLIENT_ID}")
    print("-" * 50)
 
    token_client = KeycloakTokenClient()
 
    print("Fetching Keycloak token...")
    token = await token_client.get_token()
    print(f"Token obtained : {token}")
    print("-" * 50)
 
    spiff = SpiffClient(token_client=token_client)

    await fetch_process_model_and_file(spiff, PROCESS_MODEL_ID)
    await fetch_process_instances(spiff)
    await send_message(spiff)


if __name__ == "__main__":
    asyncio.run(main())