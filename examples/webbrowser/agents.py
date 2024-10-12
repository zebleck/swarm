from swarm import Agent
from swarm.types import Result
from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize the WebDriver
driver = webdriver.Chrome()


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
    instructions="""You are a web browser agent capable of navigating websites and answering questions about their content.
    Use the provided functions to interact with web pages and retrieve information.
    Always provide clear and concise responses based on the current page content.""",
    functions=[
        navigate_to_url,
        search_on_page,
        get_page_content,
        click_element,
        type_into_element,
        close_browser,
    ],
)

'''def transfer_to_web_browser():
    """Call this function if a user is asking about a topic that is not handled by the current agent."""
    return web_browser_agent

def transfer_to_triage_agent():
    """Call this function if a user is asking about a topic that is not handled by the current agent."""
    return triage_agent'''

'''triage_agent = Agent(
    name="Triage Agent",
    instructions="""Determine which agent is best suited to handle the user's request.
    If the user wants to interact with a website or search for online information, transfer to the Web Browser Agent.""",
    functions=[transfer_to_web_browser]
)'''

# web_browser_agent.functions.append(transfer_to_triage_agent)
