import os
from swarm import Agent
from swarm.types import Result
from selenium import webdriver
from selenium.webdriver.common.by import By
from utils import login


def change_directory(path):
    """Change the current working directory to the given path."""
    os.chdir(path)
    return f"Changed directory to: {path}"


def list_directory(path="."):
    """List files and directories in the given path."""
    try:
        items = os.listdir(path)
        return "\n".join(items)
    except Exception as e:
        return f"Error listing directory: {str(e)}"


def read_file(filename):
    """Read and return the contents of a file."""
    try:
        with open(filename, "r") as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def edit_file(filename, content):
    """Edit the contents of a file."""
    try:
        with open(filename, "w") as file:
            file.write(content)
        return f"File {filename} has been updated."
    except Exception as e:
        return f"Error editing file: {str(e)}"


def create_file(filename, content=""):
    """Create a new file with optional content."""
    try:
        with open(filename, "w") as file:
            file.write(content)
        return f"File {filename} has been created."
    except Exception as e:
        return f"Error creating file: {str(e)}"


def delete_file(filename):
    """Delete a file."""
    try:
        os.remove(filename)
        return f"File {filename} has been deleted."
    except Exception as e:
        return f"Error deleting file: {str(e)}"


def find_file(filename):
    """Find a file in the current directory and its subdirectories."""
    for root, dirs, files in os.walk("."):
        if filename in files:
            return f"File {filename} found at: {os.path.join(root, filename)}"
    return f"File {filename} not found in the current directory or its subdirectories."


MODEL = "claude-3-5-sonnet@20240620"  # @param ["claude-3-5-sonnet@20240620", "claude-3-opus@20240229", "claude-3-haiku@20240307", "claude-3-sonnet@20240229" ]
if MODEL == "claude-3-5-sonnet@20240620":
    available_regions = ["us-east5", "europe-west1", "asia-southeast1"]
elif MODEL == "claude-3-opus@20240229":
    available_regions = ["us-east5"]
elif MODEL == "claude-3-haiku@20240307":
    available_regions = ["us-east5", "europe-west1", "asia-southeast1"]
elif MODEL == "claude-3-sonnet@20240229":
    available_regions = ["us-east5"]

developer_agent = Agent(
    name="Developer Agent",
    model=MODEL,
    provider="anthropic",
    instructions="""You are a developer agent capable of browsing the file system, viewing, and editing files.
    Use the provided functions to interact with the file system and implement features.
    When asked to implement a new feature:
    1. Analyze the feature description and determine which files need to be created or modified.
    2. Use the file system functions to make the necessary changes.
    3. Provide a clear summary of the changes made and any additional steps required.
    Always provide clear and concise responses about the actions you've taken.
    Be cautious when modifying or deleting files, and always ask for confirmation before performing destructive actions.""",
    functions=[
        list_directory,
        read_file,
        edit_file,
        create_file,
        delete_file,
        find_file,
    ],
)

# Initialize the WebDriver
driver = webdriver.Chrome()
login(driver)


def navigate_to_url(url):
    """Navigate to the specified URL."""
    driver.get(url)
    return f"Navigated to {url}"


def search_on_page(query):
    """Search for the given query on the current page."""
    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{query}')]")
    if elements:
        return f"Found {len(elements)} occurrences of '{query}' on the page."
    else:
        return f"No occurrences of '{query}' found on the page."


def click_element(selector):
    """Click on an element identified by the given CSS selector."""
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        element.click()
        return f"Clicked on element with selector: {selector}"
    except Exception as e:
        return f"Error clicking element: {str(e)}"


def type_into_element(selector, text):
    """Type text into an element identified by the given CSS selector."""
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        element.send_keys(text)
        return f"Typed '{text}' into element with selector: {selector}"
    except Exception as e:
        return f"Error typing into element: {str(e)}"


def get_page_content():
    """Get the main content of the current page."""
    return driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")


def close_browser():
    """Close the browser."""
    driver.quit()
    return "Browser closed."


web_browser_agent = Agent(
    name="Web Browser Agent",
    model="gpt-4o",
    provider="openai",
    instructions="""You are a web browser agent capable of navigating websites and interacting with web pages.
    Use the provided functions to interact with web pages, retrieve information, and test features.
    When asked to test a new feature:
    1. Navigate to the relevant page on the website.
    2. Interact with the new feature using the provided functions.
    3. Verify that the feature works as expected.
    4. Report any issues or confirm that the feature is working correctly.
    Always provide clear and concise responses based on the current page content and feature testing results.""",
    functions=[
        navigate_to_url,
        search_on_page,
        get_page_content,
        click_element,
        type_into_element,
        close_browser,
    ],
)

# Coordinator Agent
coordinator_agent = Agent(
    name="Coordinator Agent",
    model="gpt-4o",
    provider="openai",
    instructions="""You are a coordinator agent responsible for managing feature implementation and testing workflows.
    When a user requests a new feature or implementation:
    1. Transfer to the Developer Agent and provide clear instructions for implementing the feature.
    2. Once the Developer Agent reports the implementation is complete, transfer to the Web Browser Agent for testing.
    3. Provide the Web Browser Agent with clear instructions on how to test the new feature.
    4. If the Web Browser Agent reports any issues, transfer back to the Developer Agent with specific instructions for fixes.
    5. Repeat steps 2-4 until the feature is working correctly.
    6. Once the feature is successfully implemented and tested, provide a summary to the user.

    For general tasks:
    - If a task involves web browsing, transfer to the Web Browser Agent.
    - If a task involves file management or code editing, transfer to the Developer Agent.

    Coordinate between these agents to complete complex tasks that involve web browsing, code editing, and feature implementation.
    Keep track of the current state of feature implementation and testing to ensure the process is completed successfully.""",
)


# Transfer functions
def transfer_to_coordinator():
    """Call this function if a user is asking about a topic that is not handled by the current agent."""
    return coordinator_agent


def transfer_to_web_browser():
    return web_browser_agent


def transfer_to_developer():
    return developer_agent


# Add transfer functions to other agents
web_browser_agent.functions.append(transfer_to_coordinator)
developer_agent.functions.append(transfer_to_coordinator)
coordinator_agent.functions.append(transfer_to_web_browser)
coordinator_agent.functions.append(transfer_to_developer)
