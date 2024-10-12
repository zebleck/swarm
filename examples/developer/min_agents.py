import os
from swarm import Agent
from swarm.types import Result
from selenium import webdriver
from selenium.webdriver.common.by import By
from utils import login


MODEL = "claude-3-5-sonnet@20240620"  # @param ["claude-3-5-sonnet@20240620", "claude-3-opus@20240229", "claude-3-haiku@20240307", "claude-3-sonnet@20240229" ]
if MODEL == "claude-3-5-sonnet@20240620":
    available_regions = ["us-east5", "europe-west1", "asia-southeast1"]
elif MODEL == "claude-3-opus@20240229":
    available_regions = ["us-east5"]
elif MODEL == "claude-3-haiku@20240307":
    available_regions = ["us-east5", "europe-west1", "asia-southeast1"]
elif MODEL == "claude-3-sonnet@20240229":
    available_regions = ["us-east5"]

alice_agent = Agent(
    name="Alice Agent",
    model="gpt-4o",
    provider="openai",
    instructions="""You are a helpful agent called Alice.""",
)

bob_agent = Agent(
    name="Bob Agent",
    model=MODEL,
    provider="anthropic",
    instructions="""You are a helpful agent called Bob.""",
)

charlie_agent = Agent(
    name="Charlie Agent",
    model="gpt-4o",
    provider="openai",
    instructions="""You are a helpful agent called Charlie.""",
)


# Transfer functions
def transfer_to_bob():
    """Call this function if a user is asking about a topic that is not handled by the current agent."""
    return bob_agent


def transfer_to_alice():
    return alice_agent


def transfer_to_charlie():
    return charlie_agent


# Add transfer functions to other agents
alice_agent.functions.append(transfer_to_bob)
alice_agent.functions.append(transfer_to_charlie)
bob_agent.functions.append(transfer_to_alice)
bob_agent.functions.append(transfer_to_charlie)
charlie_agent.functions.append(transfer_to_alice)
charlie_agent.functions.append(transfer_to_bob)
