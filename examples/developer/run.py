import logging
from swarm.repl import run_demo_loop
from agents import coordinator_agent
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="run.log",
    filemode="a",
)

if __name__ == "__main__":
    """print("Welcome to the Feature Implementation and Testing System!")
    print("You can request new features, and the agents will coordinate to implement and test them.")
    print("The process works as follows:")
    print("1. You request a new feature.")
    print("2. The Coordinator Agent will instruct the Developer Agent to implement the feature.")
    print("3. Once implemented, the Web Browser Agent will test the feature.")
    print("4. If issues are found, the process will iterate until the feature works correctly.")
    print("5. You'll receive a summary of the implementation and testing process.")
    print("\nExample request: 'Implement a new login form on the homepage'")
    print("Type 'exit' to quit the program.")"""
    os.chdir("/home/zebleck/github/Cosmos/Cosmos-FrontEnd")
    run_demo_loop(coordinator_agent)
