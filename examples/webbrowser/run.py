import logging
from swarm.repl import run_demo_loop
from agents import web_browser_agent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="run.log",
    filemode="a",
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        run_demo_loop(web_browser_agent)
    finally:
        from agents import close_browser
        close_browser()
