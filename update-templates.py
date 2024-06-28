import os
import json
import requests
from dotenv import load_dotenv

try:
    ITERABLE_API_KEY = os.environ["ITERABLE_API_KEY"]
    DIRCTORY = os.environ["DIRCTORY"]
except KeyError:
    raise Exception("Error: Iterable API Key not found")

directory = DIRCTORY

# Your Iterable API key and endpoint
API_KEY = os.getenv('ITERABLE_API_KEY')
BASE_URL = "https://api.iterable.com"
UPSERT_TEMPLATE_URL = f"{BASE_URL}/api/templates/email/upsert"
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

# Your Iterable API key and endpoint
API_KEY = os.getenv('ITERABLE_API_KEY')
BASE_URL = "https://api.iterable.com"
UPSERT_TEMPLATE_URL = f"{BASE_URL}/api/templates/email/upsert"
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

# Function to process and upsert a template
def process_and_upsert_template(folder_name, campaign_name):
    try:
        print(f"Processing {campaign_name} in {folder_name}")
        metadata_path = os.path.join(folder_name, f"{campaign_name}_metadata.json")
        html_path = os.path.join(folder_name, f"{campaign_name}.html")

        if not os.path.exists(metadata_path) or not os.path.exists(html_path):
            print(f"Missing metadata or HTML file for {campaign_name}")
            return

        with open(metadata_path, 'r') as metadata_file:
            template_metadata = json.load(metadata_file)

        with open(html_path, 'r') as html_file:
            html_content = html_file.read()

        # Create the payload for upserting the template
        payload = {
            "clientTemplateId": template_metadata.get("clientTemplateId", ""),
            "name": template_metadata.get("name", ""),
            "fromName": template_metadata.get("fromName", ""),
            "fromEmail": template_metadata.get("fromEmail", ""),
            "replyToEmail": template_metadata.get("replyToEmail", ""),
            "subject": template_metadata.get("subject", ""),
            "preheaderText": template_metadata.get("preheaderText", ""),
            "ccEmails": template_metadata.get("ccEmails", []),
            "bccEmails": template_metadata.get("bccEmails", []),
            "html": html_content,
            "plainText": template_metadata.get("plainText", ""),
            "googleAnalyticsCampaignName": template_metadata.get("googleAnalyticsCampaignName", ""),
            "linkParams": template_metadata.get("linkParams", []),
            "dataFeedId": template_metadata.get("dataFeedId", 0),
            "dataFeedIds": template_metadata.get("dataFeedIds", []),
            "cacheDataFeed": template_metadata.get("cacheDataFeed", {}),
            "mergeDataFeedContext": template_metadata.get("mergeDataFeedContext", True),
            "messageTypeId": template_metadata.get("messageTypeId", 0),
            "isDefaultLocale": template_metadata.get("isDefaultLocale", True),
            "messageMedium": template_metadata.get("messageMedium", {})
        }

        # Lowercase boolean values in the payload
        payload_str = json.dumps(payload).replace("True", "true").replace("False", "false")
        payload_json = json.loads(payload_str)  # Convert back to dictionary to ensure proper JSON structure

        print(f"Payload for {campaign_name}: {json.dumps(payload_json, indent=4)}")

        response = requests.post(UPSERT_TEMPLATE_URL, headers=HEADERS, json=payload_json)
        if response.status_code == 200:
            print(f"Successfully upserted template for {campaign_name}")
        else:
            print(f"Failed to upsert template for {campaign_name}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error processing {campaign_name} in {folder_name}: {e}")

# Main function to process and upsert all templates
def update_all_templates():
    for folder_name in FOLDER_LOOKUP.values():
        print(f"Checking folder: {folder_name}")
        if os.path.exists(folder_name):
            for file_name in os.listdir(folder_name):
                if file_name.endswith('_metadata.json'):
                    campaign_name = file_name.replace('_metadata.json', '')
                    process_and_upsert_template(folder_name, campaign_name)
        else:
            print(f"Folder does not exist: {folder_name}")

# Run the main function
update_all_templates()
