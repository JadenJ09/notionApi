# %%
import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timezone


# Load the environment variables from the .env file
load_dotenv()

# Use the environment variable
notion_token = os.getenv('NOTION_TOKEN')
database_id = os.getenv('DATABASE_ID')

headers = {
    "Authorization": "Bearer " + notion_token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def get_pages(num_pages = None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
        
    # Comment this out to dump all data to a file
    # import json
    # with open('db.json', 'w', encoding='utf8') as f:
    #    json.dump(data, f, ensure_ascii=False, indent=4)

    results = data["results"]
    
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results

pages = get_pages()

for page in pages:
    page_id = page["id"]
    props = page["properties"]
    if props["URL"]["title"]:
        url = props["URL"]["title"][0]["text"]["content"]
    else:
        url = None
    if props["Title"]["rich_text"]:
        title = props["Title"]["rich_text"][0]["text"]["content"]
    else:
        title = None
    if props["Published"]["date"]:
        published = props["Published"]["date"]["start"]
        published = datetime.fromisoformat(published)
    else:
        published = None

# %%
def create_page(data: dict):
    create_url = "https://api.notion.com/v1/pages"

    payload = {"parent": {"database_id": database_id}, "properties": data}

    res = requests.post(create_url, headers=headers, json=payload)
    # print(res.status_code)
    return res

url = "Test URL 2"
title = "Test Title 2"
published_date = datetime.now(timezone.utc).isoformat()
data = {
    "URL": {"title": [{"text": {"content": url}}]},
    "Title": {"rich_text": [{"text": {"content": title}}]},
    "Published": {"date": {"start": published_date, "end": None}}
}

create_page(data)

# %%
def update_page(page_id: str, data: dict):
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {"properties": data}

    res = requests.patch(url, json=payload, headers=headers)
    return res

page_id = "87f02c10-1f59-4875-82dd-09e297d77827"

title = "Updated Title 2"
update_data = {"Title": {"rich_text": [{"text": {"content": title}}]}}
# new_date = datetime(2023, 1, 15).astimezone(timezone.utc).isoformat()
# update_data = {"Published": {"date": {"start": new_date, "end": None}}}

update_page(page_id, update_data)

# %%
def delete_page(page_id: str):
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {"archived": True}

    res = requests.patch(url, json=payload, headers=headers)
    return res

page_id = "87f02c10-1f59-4875-82dd-09e297d77827"

delete_page(page_id)