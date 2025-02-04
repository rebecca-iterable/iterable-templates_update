import os
import json
import requests

# Get required environment variables
try:
    ITERABLE_API_KEY = os.environ["ITERABLE_API_KEY"]
    GITHUB_REPO = os.environ["GITHUB_REPO"]
    PR_NUMBER = os.environ["PR_NUMBER"]
    GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
except KeyError as e:
    raise Exception(f"Missing environment variable: {e}")

BASE_URL = "https://api.iterable.com"
UPSERT_TEMPLATE_URL = f"{BASE_URL}/api/templates/email/upsert"
HEADERS = {'Api-Key': ITERABLE_API_KEY, 'Content-Type': 'application/json'}

# GitHub API URL for PR files and headers for authentication
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/pulls/{PR_NUMBER}/files"
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
    """Fetch the list of changed files in the PR using the PR number."""
    response = requests.get(GITHUB_API_URL, headers=GITHUB_HEADERS)
    if response.status_code != 200:
        print(f"Failed to get changed files: {response.status_code} - {response.text}")
        return []
    files_data = response.json()
    changed_files = [file["filename"] for file in files_data]
    return changed_files

def process_and_upsert_template(folder_name, campaign_name):
    """Reads template metadata and HTML, then upserts the template to Iterable."""
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

        # Send the upsert request to Iterable
        response = requests.post(UPSERT_TEMPLATE_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            print(f"Successfully upserted template for {campaign_name}")
        else:
            print(f"Failed to upsert template for {campaign_name}: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error processing {campaign_name} in {folder_name}: {e}")

def update_changed_templates():
    """Process only the changed templates based on the PR's changed files."""
    changed_files = get_changed_files()
    print(f"Changed files: {changed_files}")

    updated_templates = set()

    # For each changed file, determine if it belongs to one of our template folders.
    for file_path in changed_files:
        for message_type_id, folder_name in FOLDER_LOOKUP.items():
            # If the changed file is in one of the template directories
            if file_path.startswith(folder_name):
                # Extract the campaign name based on the file name pattern.
                # This handles both _metadata.json and .html file changes.
                base_name = os.path.basename(file_path)
                if base_name.endswith('_metadata.json'):
                    campaign_name = base_name.replace('_metadata.json', '')
                elif base_name.endswith('.html'):
                    campaign_name = base_name.replace('.html', '')
                else:
                    continue

                updated_templates.add((folder_name, campaign_name))

    if not updated_templates:
        print("No templates to update.")
        return

    for folder, campaign in updated_templates:
        process_and_upsert_template(folder, campaign)

# Execute the update for changed templates
update_changed_templates()
