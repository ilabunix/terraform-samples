import json
import uuid
import requests
import boto3
from bs4 import BeautifulSoup
from config import (
    CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN,
    CONFLUENCE_SPACE_KEY, OPENSEARCH_ENDPOINT, OPENSEARCH_INDEX,
    OS_USERNAME, OS_PASSWORD
)
from requests.auth import HTTPBasicAuth
from atlassian import Confluence

# === MAIN HANDLER ===
def lambda_handler(event, context):
    confluence = Confluence(
        url=CONFLUENCE_URL,
        username=CONFLUENCE_EMAIL,
        password=CONFLUENCE_API_TOKEN
    )

    pages = confluence.get_all_pages_from_space(CONFLUENCE_SPACE_KEY, limit=50)

    for page in pages:
        page_id = page["id"]
        title = page["title"]
        html = confluence.get_page_by_id(page_id, expand='body.storage')["body"]["storage"]["value"]
        text = strip_html_tags(html)
        chunks = split_text(text, chunk_size=512)

        for chunk in chunks:
            doc = {
                "id": str(uuid.uuid4()),
                "title": title,
                "content": chunk,
                "embedding": get_titan_embedding(chunk)
            }
            index_document(doc)

    return {
        "statusCode": 200,
        "body": json.dumps(f"✅ Indexed {len(pages)} pages.")
    }

# === HELPERS ===

def strip_html_tags(html):
    return BeautifulSoup(html, "html.parser").get_text()

def split_text(text, chunk_size=512):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def get_titan_embedding(text):
    bedrock = boto3.client("bedrock-runtime")
    payload = { "inputText": text }

    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload)
    )

    response_body = json.loads(response['body'].read())
    return response_body['embedding']

def index_document(doc):
    url = f"{OPENSEARCH_ENDPOINT}/{OPENSEARCH_INDEX}/_doc/{doc['id']}"
    headers = { "Content-Type": "application/json" }
    auth = HTTPBasicAuth(OS_USERNAME, OS_PASSWORD)

    # Cast embedding to float32
    if "embedding" in doc:
        embedding = doc["embedding"]

        if not isinstance(embedding, list):
            print(f"❌ Skipping document {doc['id']} - embedding is not a list")
            return

        # Normalize to 1536-dims
        if len(embedding) < 1536:
            embedding += [0.0] * (1536 - len(embedding))  # Pad
        elif len(embedding) > 1536:
            embedding = embedding[:1536]  # Truncate

        doc["embedding"] = [float(x) for x in embedding]

    res = requests.put(url, headers=headers, data=json.dumps(doc), auth=auth)

    if res.status_code not in [200, 201]:
        print("❌ Failed to index:", res.status_code, res.text)
    else:
        print("✅ Indexed:", doc["title"])
