import operator
from typing import Annotated, List, TypedDict, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from google import genai

from .logger import setup_logger
from .client import config, AIClientFactory, sidecar
from .storage import storage

logger = setup_logger("brain.core.workflow")

# --- State Definition ---
class Article(TypedDict):
    url: str
    title: str
    body: str
    source: str
    score: float  # 0-10
    reason: str   # Why this score?
    topic: str

class NewsState(TypedDict):
    articles: List[Article]
    final_brief: str
    config: dict

# --- Nodes ---

def search_node(state: NewsState):
    """
    Execute search. This node expects 'search_func' to be injected or 
    passed via config, but for simplicity we'll assume the caller 
    updates 'articles' in state before starting, or we implement search here.
    
    Actually, to keep it generic, we'll assume the initial articles 
    are passed in the initial state or fetched here if empty.
    Let's assume the Skill implementation fetches raw data and passes it to the graph.
    So this node might be optional or a placeholder for future expansion.
    """
    logger.info(f"Entering Search Node. Current articles: {len(state['articles'])}")
    return {"articles": state['articles']}

def history_filter_node(state: NewsState):
    """Filter out articles that have been processed before."""
    raw_articles = state['articles']
    new_articles = []
    
    for art in raw_articles:
        if not storage.exists(art['url']):
            new_articles.append(art)
        else:
            logger.debug(f"Skipping duplicate URL: {art['url']}")
            
    logger.info(f"History Filter: {len(raw_articles)} -> {len(new_articles)}")
    return {"articles": new_articles}

def evaluate_node(state: NewsState):
    """Score articles using LLM."""
    articles = state['articles']
    if not articles:
        return {"articles": []}

    client = AIClientFactory.get_client()
    scored_articles = []
    
    # We can batch evaluate or single evaluate. Batch is faster.
    prompt = "Evaluate the following news articles. For each, assign a relevance score (0-10) and a brief reason.\n"
    prompt += "Criteria: High information density, recent, relevant to tech/AI/programming.\n"
    prompt += "Output JSON format: [{'index': int, 'score': float, 'reason': str}]\n\n"
    
    for i, art in enumerate(articles):
        prompt += f"Index {i}:\nTitle: {art['title']}\nSummary: {art['body'][:200]}...\n\n"

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        import json
        evaluations = json.loads(response.text)
        
        # Map back to articles
        for eval_item in evaluations:
            idx = eval_item.get('index')
            if idx is not None and 0 <= idx < len(articles):
                art = articles[idx]
                art['score'] = eval_item.get('score', 0)
                art['reason'] = eval_item.get('reason', '')
                if art['score'] >= 6.0: # Threshold
                    scored_articles.append(art)
                else:
                    logger.info(f"Filtered low score ({art['score']}): {art['title']}")
                    
    except Exception as e:
        logger.error(f"Evaluation failed: {e}. Keeping all articles.")
        scored_articles = articles # Fallback

    return {"articles": scored_articles}

def dedup_node(state: NewsState):
    """Simple semantic dedup (placeholder for complex logic)."""
    # For MVP, we'll just dedup by exact Title match if any slipped through
    # Real semantic dedup needs embeddings.
    seen_titles = set()
    unique_articles = []
    
    for art in state['articles']:
        if art['title'] not in seen_titles:
            seen_titles.add(art['title'])
            unique_articles.append(art)
            
    return {"articles": unique_articles}

def summarize_node(state: NewsState):
    """Generate final brief."""
    articles = state['articles']
    if not articles:
        return {"final_brief": "No significant news found today."}
        
    client = AIClientFactory.get_client()
    lang = state['config'].get('language', '中文')
    
    prompt = f"Generate a Daily Brief in {lang} based on these high-quality articles:\n\n"
    for art in articles:
        prompt += f"- [{art['score']}] {art['title']} ({art['source']})\n"
        prompt += f"  {art['body']}\n\n"
        
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return {"final_brief": response.text}
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return {"final_brief": "Error generating brief."}

def persist_node(state: NewsState):
    """Save processed articles to DB."""
    for art in state['articles']:
        storage.add_article(
            url=art['url'], 
            title=art['title'], 
            source=art['source']
        )
    return {}

def notify_node(state: NewsState):
    """Send result to Sidecar."""
    sidecar.notify("Daily Brief", state['final_brief'])
    return {}

# --- Graph Construction ---

def create_news_graph():
    workflow = StateGraph(NewsState)
    
    workflow.add_node("history_filter", history_filter_node)
    workflow.add_node("evaluate", evaluate_node)
    workflow.add_node("dedup", dedup_node)
    workflow.add_node("summarize", summarize_node)
    workflow.add_node("persist", persist_node)
    workflow.add_node("notify", notify_node)
    
    # Edges
    workflow.set_entry_point("history_filter")
    workflow.add_edge("history_filter", "evaluate")
    workflow.add_edge("evaluate", "dedup")
    workflow.add_edge("dedup", "summarize")
    workflow.add_edge("summarize", "persist")
    workflow.add_edge("persist", "notify")
    workflow.add_edge("notify", END)
    
    return workflow.compile()
