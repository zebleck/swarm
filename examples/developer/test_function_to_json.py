import os
from openai import AzureOpenAI
from swarm.util import function_to_json
import json


def get_weather(location, time="now"):
    """Get the current weather in a given location. Location MUST be a city."""
    return json.dumps({"location": location, "temperature": "65", "time": time})


openai_function = function_to_json(get_weather)

print(openai_function)

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
messages = [{"role": "user", "content": "Whats the weather in San Francisco?"}]

message = client.messages.create(
    max_tokens=1024,
    tools=[
        {
            "name": "get_weather",
            "description": "Get the current weather in a given location. Location MUST be a city.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "time": {
                        "type": "string",
                        "description": "The time of day, e.g. now, morning, afternoon",
                    },
                },
                "required": ["location"],
            },
        }
    ],
    messages=messages,
    model=MODEL,
)
print("Anthropic Response:")
print(message.model_dump_json(indent=2))

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-05-01-preview",
)
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Define the function for the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location. Location MUST be a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g. San Francisco",
                    },
                    "time": {
                        "type": "string",
                        "description": "The time of day, e.g. now, morning, afternoon",
                    },
                },
                "required": ["location"],
            },
        },
    }
]

# First API call: Ask the model to use the function
response = client.chat.completions.create(
    model=deployment_name,
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

print("Azure Response:")
print(response.choices[0].message.tool_calls)
