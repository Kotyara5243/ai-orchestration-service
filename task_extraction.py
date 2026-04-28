import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List

TASK_DEFINITIONS = [
    "userTask",
    "manualTask",
    "scriptTask",
    "serviceTask",
    "sendTask",
]

LLM_INSTRUCTIONS = "./bpmn:collaboration/bpmn:documentation"

TASK_NAMES_IGNORE = ["Send data to gateway", "Send request to gateway"]

MESSAGE_REF = "bpmn:messageEventDefinition"

NAMESPACES = {
    "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
    "dc": "http://www.omg.org/spec/DD/20100524/DC",
    "spiffworkflow": "http://spiffworkflow.org/bpmn/schema/1.0/core",
    "di": "http://www.omg.org/spec/DD/20100524/DI"
}


def extract_tasks_from_model(xml_file: Path) -> tuple[List[Dict[str, Any]], str | None]:
    tree = ET.parse(xml_file)
    root = tree.getroot()

    extracted_tasks: List[Dict[str, Any]] = []

    for task_type in TASK_DEFINITIONS:
        for task in root.findall(f".//bpmn:{task_type}", NAMESPACES):
            task_name = task.get("name", "Unknown")
            if task_name in TASK_NAMES_IGNORE:
                continue

            docs = task.find("bpmn:documentation", NAMESPACES)
            if docs is None:
                docs = ""
            else :
                docs = docs.text
            
            extracted_tasks.append(
                {
                    "id": task.get("id", "Unknown"),
                    "name": task_name,
                    "type": task_type,
                    "documentation": docs
                }
            )

    event = root.find(".//bpmn:intermediateCatchEvent[@name='wait for reply from gateway']/bpmn:messageEventDefinition", NAMESPACES)
    if event is None or event.text is None :
        raise Exception("InvalidModel") # TODO: exception InvalidModel

    return extracted_tasks, event.get("messageRef")


def extract_instructions(xml_file: Path) -> str | None:
    tree = ET.parse(xml_file)
    root = tree.getroot()

    docs = root.find(LLM_INSTRUCTIONS, NAMESPACES)
    if docs is None:
        return None

    return docs.text


def main() -> None:
    model_file = Path(__file__).with_name("model.xml")

    if not model_file.exists():
        print(f"Error: {model_file} not found")
        return

    tasks, message = extract_tasks_from_model(model_file)
    instructions = extract_instructions(model_file)

    print(f"Extracting tasks from {model_file}...")
    if instructions:
        print("\nLLM instructions:")
        print(instructions)

    if message:
        print("\nMessage: ")
        print(message)

    for index, task in enumerate(tasks, start=1):
        print(f"\n[{index}] Task ID: {task['id']}")
        print(f"    Name: {task['name']}")
        print(f"    Type: {task['type']}")
        print(f"    Documentation: {task['documentation']}")


if __name__ == "__main__":
    main()
