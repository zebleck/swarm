from anthropic import AnthropicVertex

LOCATION = "europe-west1"
PROJECT_ID = "gen-lang-client-0851976833"
ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com"

MODEL = "claude-3-5-sonnet@20240620"  # @param ["claude-3-5-sonnet@20240620", "claude-3-opus@20240229", "claude-3-haiku@20240307", "claude-3-sonnet@20240229" ]
if MODEL == "claude-3-5-sonnet@20240620":
    available_regions = ["us-east5", "europe-west1", "asia-southeast1"]
elif MODEL == "claude-3-opus@20240229":
    available_regions = ["us-east5"]
elif MODEL == "claude-3-haiku@20240307":
    available_regions = ["us-east5", "europe-west1", "asia-southeast1"]
elif MODEL == "claude-3-sonnet@20240229":
    available_regions = ["us-east5"]

client = AnthropicVertex(region=LOCATION, project_id=PROJECT_ID)
message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Send me a recipe for banana bread.",
        }
    ],
    model=MODEL,
)
print(message.model_dump_json(indent=2))
