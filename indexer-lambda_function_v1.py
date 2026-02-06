import json
import uuid
import requests
import boto3
from bs4 import BeautifulSoup
from config import (
    CONFLUENCE_URL,
    CONFLUENCE_API_TOKEN,
    CONFLUENCE_SPACE_KEY,
    OPENSEARCH_ENDPOINT,
    OPENSEARCH_INDEX,
    OS_USERNAME,
    OS_PASSWORD
)

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
    return response_body["embedding"]

def index_document(doc):
    url = f"{OPENSEARCH_ENDPOINT}/{OPENSEARCH_INDEX}/_doc/{doc['id']}"
    headers = { "Content-Type": "application/json" }
    auth = requests.auth.HTTPBasicAuth(OS_USERNAME, OS_PASSWORD)

    # Normalize to float32
    if "embedding" in doc:
        doc["embedding"] = [float(x) for x in doc["embedding"]]
        if len(doc["embedding"]) < 1536:
            doc["embedding"] += [0.0] * (1536 - len(doc["embedding"]))
        elif len(doc["embedding"]) > 1536:
            doc["embedding"] = doc["embedding"][:1536]

    res = requests.put(url, headers=headers, data=json.dumps(doc), auth=auth)

    if res.status_code not in [200, 201]:
        print("❌ Failed to index:", res.status_code, res.text)
    else:
        print("✅ Indexed:", doc["title"])

# === MAIN HANDLER ===

def lambda_handler(event, context):
    headers = {
        "Authorization": f"Bearer {CONFLUENCE_API_TOKEN}",
        "Accept": "application/json"
    }

    pages_url = f"{CONFLUENCE_URL}/wiki/api/v2/pages?spaceKey={CONFLUENCE_SPACE_KEY}&limit=50"
    #res = requests.get(pages_url, headers=headers)
    #res.raise_for_status()
    #pages = res.json()["results"]
res = requests.get(pages_url, headers=headers)

try:
    res.raise_for_status()
    data = res.json()
    pages = data.get("results", [])
except requests.exceptions.HTTPError as e:
    print("❌ HTTP error:", e)
    print("🔍 Response text:", res.text)
    raise
except json.JSONDecodeError as e:
    print("❌ Failed to decode JSON")
    print("🔍 Raw response:", res.text)
    raise
    for page in pages:
        page_id = page["id"]
        title = page["title"]

        body_url = f"{CONFLUENCE_URL}/wiki/api/v2/pages/{page_id}?body-format=storage"
        body_res = requests.get(body_url, headers=headers)
        body_res.raise_for_status()

        html = body_res.json()["body"]["storage"]["value"]
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