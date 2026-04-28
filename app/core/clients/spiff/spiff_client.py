import httpx
from typing import Any
from app.configs.config import settings
from app.core.clients.keycloak.keycloak_client import KeycloakTokenClient


class SpiffClient:
    """
    Async httpx client for SpiffWorkflow API communication.

    Authentication is handled via a Keycloak bearer token obtained
    using the OAuth2 client credentials grant. The token is fetched
    and cached by KeycloakTokenClient, which refreshes it automatically.
    """

    def __init__(self, token_client: KeycloakTokenClient):
        self.base_url = settings.SPIFF_BASE_URL.rstrip("/")
        self._token_client = token_client

    async def _get(self, path: str, params: dict | None = None) -> dict[str, Any]:
        headers = await self._token_client.get_auth_headers()
        url = f"{self.base_url}{path}"

        # for debug
        # print("URL: "+ url)

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()

            # For debug
            # print(f"Status : {response.status_code}")
            # print(f"Headers : {dict(response.headers)}")
            # print(f"Raw body : {response.text!r}")
            
            return response.json()

    async def _post(self, path: str, payload: dict[str, Any], params: dict | None = None) -> dict[str, Any]:
        headers = await self._token_client.get_auth_headers()
        url = f"{self.base_url}{path}"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, params=params)
            response.raise_for_status()
            
            # For debug
            # print(f"Status : {response.status_code}")
            # print(f"Headers : {dict(response.headers)}")
            # print(f"Raw body : {response.text!r}")

            return response.json()

    # -------------------------
    # Message events
    # -------------------------

    async def trigger_message_event(
        self,
        message_name: str,
        payload: dict[str, Any],
        execution_mode: str = "synchronous",
    ) -> dict[str, Any]:
        """
        POST /messages/{modified_message_name}

        Triggers a SpiffWorkflow message event, starting or resuming a process instance.

        Params:
            message_name: The message_name, modified to replace slashes (/) with colons
            execution_mode: synchronous (default) or asynchronous.
            payload: JSON body sent as the message payload.

        Returns:
            Parsed JSON response from SpiffWorkflow.
        """
        return await self._post(
            f"/messages/{message_name}",
            payload=payload,
            params={"execution_mode": execution_mode},
        )
    
    async def get_message_models(self) -> dict[str, Any]:
        """
        GET /message-models

        Get a list of message models.
        """
        return await self._get(f"/message-models")
    
    async def get_messages(self, process_instance_id: str | None) -> dict[str, Any]:
        """
        GET /messages

        Get a list of message instances.
        """
        return await self._get(f"/messages", params={"process_instance_id": process_instance_id})

    # -----------------------------
    # Process instances
    # -----------------------------

    async def get_process_instance(self, modified_process_model_identifier: str, process_instance_id: str) -> dict[str, Any]:
        """
        GET /process-instances/{modified_process_model_identifier}/{process_instance_id}

        Fetches the current state of a process instance including its
        process variables.
        """
        return await self._get(f"/process-instances/{modified_process_model_identifier}/{process_instance_id}")
    
    async def get_process_instances(
        self,
        payload: dict[str, Any],
        page: int = 1,
        per_page: int = 100,
    ) -> dict[str, Any]:
        """
        POST /process-instances

        Returns a list of process instances
        """
        return await self._post(
            f"/process-instances",
            payload=payload,
            params={"page": page, "per_page": per_page},
        )
    
    async def get_process_instance_logs(self, modified_process_model_identifier: str, process_instance_id: str) -> dict[str, Any]:
        """
        GET /logs/{modified_process_model_identifier}/{process_instance_id}

        Returns a list of process instances
        """
        return await self._get(f"/logs/{modified_process_model_identifier}/{process_instance_id}")

    # -----------------------------
    # Process models
    # -----------------------------

    async def get_process_model(self, process_model_id: str) -> dict[str, Any]:
        """
        GET /process-models/{modified_process_model_id}

        Fetches the process model definition including BPMN metadata.
        """
        return await self._get(f"/process-models/{process_model_id}")

    async def get_process_models(self, process_group_identifier: str) -> dict[str, Any]:
        """
        GET /process-models

        Fetches the process models in a group.

        Params:
            process_group_identifier: The group containing the models we want to return
        """
        return await self._get(path="/process-models", params={"process_group_identifier": process_group_identifier})
    
    
    async def get_process_model_file(self, modified_process_model_identifier: str, file_name: str) -> dict[str, Any]:
        """
        GET /process-models/{modified_process_model_identifier}/files/{file_name}

        Fetches a process model file.
        """
        return await self._get(path=f"/process-models/{modified_process_model_identifier}/files/{file_name}")

    async def get_processes(self) -> dict[str, Any]:
        """
        GET /processes

        Returns all BPMN process definitions from all process models.
        Useful for finding processes for call activities.
        """
        return await self._get(f"/processes")

    # ------------------------
    # Tasks
    # ------------------------

    async def get_tasks_for_instance(self, instance_id: str) -> list[dict[str, Any]]:
        """
        GET /tasks

        Gets all tasks assigned to or available to the current user, 
        optionally filtered by process instance.
        """
        data = await self._get("/tasks", params={"process_instance_id": instance_id})
        return data.get("results", data)

    async def get_task(self, instance_id: str, task_id: str) -> dict[str, Any]:
        """
        GET /tasks/{task_id}

        Fetches details for a specific task within a process instance.
        """
        return await self._get(
            f"/tasks/{task_id}",
            params={"process_instance_id": instance_id},
        )
