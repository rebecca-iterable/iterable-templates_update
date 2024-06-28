import os
import json
import requests
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Your Iterable API key and endpoint
API_KEY = os.getenv('ITERABLE_API_KEY')
BASE_URL = "https://api.iterable.com"
# TODO: remove date range when done testing
GET_ALL_TEMPLATES = f"{BASE_URL}/api/templates?templateType=Base&messageMedium=Email&startDateTime=2024-06-27T07%3A00%3A00.000Z&endDateTime=2024-06-28T06%3A59%3A00.000Z"
GET_SINGLE_TEMPLATE = f"{BASE_URL}/api/templates/email/get"
HEADERS = {'Api-Key': API_KEY, 'Content-Type': 'application/json'}

# Lookup table for message type IDs and their corresponding folder names
FOLDER_LOOKUP = {
    "64268": "src/templates/email/marketing/cartReminders_64268",
    "64265": "src/templates/email/marketing/dailyPrommotional_64265",
    "64269": "src/templates/email/marketing/productSuggestions_64269",
    "64267": "src/templates/email/marketing/weeklyNewsletter_64267",
    "64266": "src/templates/email/marketing/weeklyPromotional_64266"
    # TODO: include transactional paths and message types
}

# Function to sanitize template names
def sanitize_filename(filename):
    return re.sub(r'[^\w\-_. ]', '_', filename).strip().lower().replace(" ", "_")

# Function to fetch a template
def fetch_template(template_id, message_type_id, template_name):
    print(f"Fetching template {template_id}...")
    response = requests.get(f"{GET_SINGLE_TEMPLATE}?templateId={template_id}", headers=HEADERS)
    if response.status_code == 200:
        template = response.json()
        folder_name = FOLDER_LOOKUP.get(str(message_type_id), "unknown")
        
        # Sanitize template name
        sanitized_name = sanitize_filename(template_name)

        # Ensure the main folder exists
        os.makedirs(folder_name, exist_ok=True)

        # Save the JSON file without the "html" property
        template_metadata = template
        html_content = template_metadata.pop("html", "")

        with open(os.path.join(folder_name, f"{sanitized_name}_metadata.json"), 'w') as json_file:
            json.dump(template_metadata, json_file, indent=4)
        
        # Save the HTML content
        with open(os.path.join(folder_name, f"{sanitized_name}.html"), 'w') as html_file:
            html_file.write(html_content)
    else:
        print(f"Failed to fetch template {template_id}: {response.status_code}")

# Function to fetch all templates and their details
def fetch_all_templates():
    response = requests.get(GET_ALL_TEMPLATES, headers=HEADERS)
    if response.status_code == 200:
        templates = response.json().get('templates', [])
        print(f"Found {len(templates)} templates")
        for template in templates:
            template_id = template['templateId']
            message_type_id = template['messageTypeId']
            template_name = template['name']
            fetch_template(template_id, message_type_id, template_name)
    else:
        print(f"Failed to fetch templates list: {response.status_code}")

# Fetch all templates
fetch_all_templates()
