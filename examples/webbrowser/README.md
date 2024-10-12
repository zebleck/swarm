# Web Browser Agent

This example demonstrates a Swarm containing a web browser agent that can navigate websites and answer questions using Selenium.

## Setup

1. Install the required dependencies:

```shell
pip install selenium webdriver_manager
```

2. Run the web browser agent Swarm:

```shell
python3 run.py
```

## Usage

The web browser agent can perform the following actions:
- Navigate to a website
- Search for information on a page
- Answer questions based on the content of the current page

Example queries:
- "Go to https://www.example.com"
- "Search for 'Python' on the page"
- "What is the main heading on this page?"

## Note

This agent uses Selenium with Chrome. Make sure you have Chrome installed on your system. The WebDriver will be automatically managed by the `webdriver_manager` library.
