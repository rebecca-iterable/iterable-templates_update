import os
import json
import requests

try:
    ITERABLE_API_KEY = os.environ["ITERABLE_API_KEY"]
    GITHUB_REPO = os.environ["GITHUB_REPO"]
    GITHUB_SHA = os.environ["GITHUB_SHA"]
    GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
except KeyError as e:
    raise Exception(f"Error: Missing environment variable {e}")

BASE_URL = "https://api.iterable.com"
UPSERT_TEMPLATE_URL = f"{BASE_URL}/api/templates/email/upsert"
HEADERS = {'Api-Key': ITERABLE_API_KEY, 'Content-Type': 'application/json'}

GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/pulls"
GITHUB_HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# Lookup table for message type IDs and their corresponding folder names
FOLDER_LOOKUP = {
    "64268": "src/templates/email/marketing/cartReminders_64268",
    "64265": "src/templates/email/marketing/dailyPrommotional_64265",
    "64269": "src/templates/email/marketing/productSuggestions_64269",
    "64267": "src/templates/email/marketing/weeklyNewsletter_64267",
    "64266": "src/templates/email/marketing/weeklyPromotional_64266"
}

def get_changed_files():
    """Fetches the list of changed files in the merged PR."""
    response = requests.get(f"{GITHUB_API_URL}/commits/{GITHUB_SHA}", headers=GITHUB_HEADERS)

    if response.status_code != 200:
        print(f"Failed to get changed files: {response.status_code} - {response.text}")
        return []

    commit_data = response.json()
    changed_files = [file["filename"] for file in commit_data.get("files", [])]
    
    return changed_files

def process_and_upsert_template(folder_name, campaign_name):
    """Reads template data and upserts it to Iterable."""
    try:
        metadata_path = os.path.join(folder_name, f"{campaign_name}_metadata.json")
        html_path = os.path.join(folder_name, f"{campaign_name}.html")

        if not os.path.exists(metadata_path) or not os.path.exists(html_path):
            print(f"Missing metadata or HTML file for {campaign_name}")
            return

        with open(metadata_path, 'r') as metadata_file:
            template_metadata = json.load(metadata_file)

        with open(html_path, 'r') as html_file:
            html_content = html_file.read()

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

        response = requests.post(UPSERT_TEMPLATE_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            print(f"Successfully upserted template for {campaign_name}")
        else:
            print(f"Failed to upsert template for {campaign_name}: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error processing {campaign_name} in {folder_name}: {e}")

def update_changed_templates():
    """Processes only changed templates from the merged PR."""
    changed_files = get_changed_files()
    print(f"Changed files: {changed_files}")

    updated_templates = set()

    for file_path in changed_files:
        for message_type_id, folder_name in FOLDER_LOOKUP.items():
            if file_path.startswith(folder_name):
                campaign_name = os.path.basename(file_path).replace('_metadata.json', '').replace('.html', '')
                updated_templates.add((folder_name, campaign_name))

    if not updated_templates:
        print("No templates to update.")
        return

    for folder, campaign in updated_templates:
        process_and_upsert_template(folder, campaign)

# Run the function
update_changed_templates()
