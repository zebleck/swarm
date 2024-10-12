import os
from swarm import Swarm, Agent
from dotenv import load_dotenv

load_dotenv()

# Initialize Swarm
client = Swarm()

# Create a simple agent
agent = Agent(
    name="Simple Agent",
    instructions="You are a helpful assistant that provides brief responses.",
)

# Run a simple conversation
response = client.run(
    agent=agent,
    messages=[{"role": "user", "content": "Hello! What's your name?"}],
)

# Print the response
print("Agent's response:")
print(response.messages[-1]["content"])
