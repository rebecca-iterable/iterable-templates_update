import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Your Iterable API key and endpoint
API_KEY = os.getenv('ITERABLE_API_KEY')
BASE_URL = "https://api.iterable.com"
GET_TEMPLATES_URL = f"{BASE_URL}/api/templates"
UPDATE_TEMPLATE_URL = f"{BASE_URL}/api/templates/email/update"
HEADERS = {'Api-Key': API_KEY, 'Content-Type': 'application/json'}

# Template types to fetch
TEMPLATE_TYPES = ['Base', 'Blast', 'Triggered', 'Workflow']

# Function to fetch templates of a specific type
def fetch_templates(template_type):
    # TODO: remove date range from url when done testing
    response = requests.get(f"{GET_TEMPLATES_URL}?templateType={template_type}&messageMedium=Email&startDateTime=2025-06-27T07%3A00%3A00.000Z&endDateTime=2025-12-01T06%3A59%3A00.000Z", headers=HEADERS)
    if response.status_code == 200:
        templates = response.json().get('templates', [])
        return templates
    else:
        print(f"Failed to fetch {template_type} templates: {response.status_code}")
        return []

# Function to update a template's clientTemplateId
def update_template_client_id(template_id, client_template_id):
    payload = {
        "templateId": template_id,
        "clientTemplateId": client_template_id
    }
    response = requests.post(UPDATE_TEMPLATE_URL, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"Successfully updated template {template_id} with clientTemplateId {client_template_id}")
    else:
        print(f"Failed to update template {template_id}: {response.status_code}")

def update_local_metadata_file(template_name):
    """
    Finds the local JSON metadata file by convention and updates clientTemplateId
    """
    metadata_path = os.path.join(LOCAL_METADATA_FOLDER, f"{template_name}_metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        metadata['clientTemplateId'] = template_name

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Updated local metadata file: {metadata_path}")

        # Optionally add, commit, push
        subprocess.run(["git", "add", metadata_path])
        subprocess.run(["git", "commit", "-m", f"Update clientTemplateId to {template_name}"])
        subprocess.run(["git", "push", "origin", "new_marketing_branch"])
        print("🚀 Changes committed & pushed to GitHub!")
    else:
        print(f"⚠️ Metadata file not found: {metadata_path}")

# Main function to fetch and update templates for each type
def update_client_ids_for_all_templates():
    for template_type in TEMPLATE_TYPES:
        templates = fetch_templates(template_type)
        print(f"Found {len(templates)} {template_type} templates")
        for template in templates:
            template_id = template['templateId']
            template_name = template['name']
            update_template_client_id(template_id, template_name)

# Run the main function
update_client_ids_for_all_templates()
