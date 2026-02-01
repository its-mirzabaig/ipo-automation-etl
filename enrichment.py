import json
from tavily import TavilyClient
from google import genai
from config import CONFIG
from logger import logger

def perform_dual_search(company_name):
    """
    Executes TWO distinct searches:
    1. Navigational: To find the official URL.
    2. Informational: To find news/sentiment.
    """
    results = []
    # Only initialize if key exists
    if not CONFIG["TAVILY_KEY"]:
        logger.warning("⚠️ Tavily Key missing. Skipping search.")
        return []

    tavily = TavilyClient(api_key=CONFIG["TAVILY_KEY"])

    # Search 1: Navigational
    try:
        res_site = tavily.search(
            query=f"{company_name} official corporate website home page",
            search_depth="basic",
            max_results=2
        )
        results.extend(res_site.get('results', []))
    except Exception as e:
        logger.warning(f"⚠️ Search 1 (Site) Failed: {e}")

    # Search 2: Informational
    try:
        res_news = tavily.search(
            query=f"{company_name} IPO news business model analysis",
            topic="finance",
            max_results=3
        )
        results.extend(res_news.get('results', []))
    except Exception as e:
        logger.warning(f"⚠️ Search 2 (News) Failed: {e}")

    return results

def get_ai_analysis(company_name, search_results):
    try:
        if not CONFIG["GEMINI_KEY"]:
             logger.warning("⚠️ Gemini Key missing. Skipping AI.")
             return None

        client = genai.Client(api_key=CONFIG["GEMINI_KEY"])
        
        # Prepare Context (Deduplicate)
        context_list = []
        seen_urls = set()
        
        for r in search_results:
            if r['url'] not in seen_urls:
                context_list.append(f"- Title: {r['title']}\n  Content: {r['content']}\n  URL: {r['url']}")
                seen_urls.add(r['url'])
        
        context_text = "\n\n".join(context_list)

        prompt = f"""
        You are a financial analyst. Analyze this IPO candidate using the search data.

        Target Company: {company_name}

        Search Data:
        {context_text}

        Tasks:
        1. Website: Find the OFFICIAL corporate URL. If uncertain or only news links exist, return "Not Found".
        2. Summary: Write 2 professional sentences explaining their business model.
        3. Sentiment: Assess market sentiment (Positive, Neutral, Risky, Quiet).

        Output JSON only:
        {{
            "website": "url",
            "summary": "text",
            "sentiment": "text"
        }}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"❌ Gemini Analysis Failed: {e}")
        return None

def enrich_data(matches):
    mode = CONFIG["ENRICHMENT_MODE"]
    if mode == "NONE":
        return matches
    
    logger.info(f"🧠 Enrichment Started (Mode: {mode}) | Strategy: Dual Search")
    
    for m in matches:
        logger.info(f"   🔎 Researching: {m['name']}...")
        
        # 1. Execute Dual Search
        search_results = perform_dual_search(m['name'])
        m['search_results'] = search_results
        
        # 2. AI Analysis
        if mode == "AI_FULL":
            analysis = get_ai_analysis(m['name'], search_results)
            if analysis:
                m['ai_summary'] = analysis.get('summary', 'N/A')
                m['website'] = analysis.get('website', 'Not Found')
                m['sentiment'] = analysis.get('sentiment', 'N/A')
                logger.info(f"     ✅ Analyzed: {m['sentiment']} | Site: {m['website']}")
            else:
                m['ai_summary'] = "Analysis Failed"
                m['website'] = "Not Found"
                
    return matches