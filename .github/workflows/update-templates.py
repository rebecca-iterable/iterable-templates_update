import os
import json
import requests

def read_html_file(html_file):
    with open(html_file, 'r') as f:
        return f.read()

def read_json_file(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def update_json_with_html(json_data, html_string):
    json_data['html'] = html_string
    return json_data

def send_post_request(url, headers, json_data):
    response = requests.post(url, headers=headers, json=json_data)
    return response

if __name__ == "__main__":

    try:
        ITERABLE_API_KEY = os.environ["ITERABLE_API_KEY"]
    except KeyError:
        raise Exception("Error: Iterable API Key not found")

    directory = '../..'
    url = 'https://api.iterable.com/api/templates/email/update'
    headers = {'Api-Key': ITERABLE_API_KEY}

    for folder in os.listdir(directory):
        folder_path = os.path.join(directory, folder)
        if os.path.isdir(folder_path):
            html_file = os.path.join(folder_path, f'{folder}.html')
            json_file = os.path.join(folder_path, f'{folder}.json')

            if os.path.exists(html_file) and os.path.exists(json_file):
                html_string = read_html_file(html_file)
                json_data = read_json_file(json_file)
                updated_json_data = update_json_with_html(json_data, html_string)
                response = send_post_request(url, headers,updated_json_data)
                if response.status_code == 200:
                    print(f"POST request for template {folder} successful!")
                else:
                    print(f"POST request for template {folder} failed with status code: {response.status_code}")
