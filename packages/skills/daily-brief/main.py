import time
import sys
import uuid
from duckduckgo_search import DDGS

# Import from Brain Core SDK
from brain.core.config import config
from brain.core.logger import setup_logger
from brain.core.workflow import create_news_graph

logger = setup_logger("skill.daily-brief")

def search_news(topics, max_results):
    logger.info(f"Searching news for topics: {topics}...")
    all_articles = []
    
    try:
        with DDGS() as ddgs:
            for topic in topics:
                logger.info(f"Searching for: {topic}")
                results = list(ddgs.text(f"{topic} news", max_results=max_results))
                for r in results:
                    # Normalize to Article State format
                    all_articles.append({
                        "url": r.get('href'),
                        "title": r.get('title'),
                        "body": r.get('body'),
                        "source": "DuckDuckGo",
                        "topic": topic,
                        "score": 0.0, # Will be filled by EvaluateNode
                        "reason": ""
                    })
                time.sleep(1) # Be polite
        logger.info(f"Found {len(all_articles)} articles in total.")
        return all_articles
    except Exception as e:
        logger.error(f"Search failed: {e}. Returning mock data.")
        # Mock data for testing flow
        return [
            {
                "url": f"http://mock.com/{uuid.uuid4()}",
                "title": "Mock News: AI is Great",
                "body": "AI is changing the world in 2026...",
                "source": "MockSource",
                "topic": "AI",
                "score": 0.0,
                "reason": ""
            }
        ]

def run():
    logger.info("=== Starting Daily Brief Agent (v2 with Workflow) ===")
    
    # 1. Load Config
    topics = config.get("topics", ["Technology"])
    max_results = config.get("max_results", 3)
    
    # 2. Search (Input Phase)
    raw_articles = search_news(topics, max_results)
    
    if not raw_articles:
        logger.warning("No articles found. Exiting.")
        return

    # 3. Execute Workflow (Process Phase)
    # Initialize State
    initial_state = {
        "articles": raw_articles,
        "final_brief": "",
        "config": {
            "language": config.get("language", "中文")
        }
    }
    
    app = create_news_graph()
    
    # Run graph
    try:
        result = app.invoke(initial_state)
        logger.info("Workflow executed successfully.")
        # logger.info(f"Final Brief Length: {len(result['final_brief'])}")
    except Exception as e:
        logger.critical(f"Workflow execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()
