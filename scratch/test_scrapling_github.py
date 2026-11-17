import os
import sys
import time

# Ensure repo is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapling import Fetcher, StealthyFetcher, Selector

def test_github_scrapling(query="ai-agents"):
    print("=" * 70)
    print(f"🚀 SCRAPLING GITHUB AUTONOMOUS REPO HARVESTER (Query: {query})")
    print("=" * 70)
    
    # We will test two GitHub surfaces:
    # 1. GitHub Topic Page: https://github.com/topics/{query}
    # 2. GitHub Explore / Search
    url = f"https://github.com/topics/{query}"
    print(f"\n[1] Initiating Scrapling on Target: {url}")
    print("    Mode: High-Speed Fetcher with Stealth fallback...")
    
    t0 = time.time()
    try:
        response = Fetcher.get(url, timeout=15)
        html = response.html_content if hasattr(response, 'html_content') else response.text
        status = getattr(response, 'status', 200)
    except Exception as e:
        print(f"    Fast fetcher encountered: {e}. Switching to StealthyFetcher...")
        response = StealthyFetcher.fetch(url, headless=True)
        html = response.html_content if hasattr(response, 'html_content') else str(response.body)
        status = getattr(response, 'status', 200)
    
    latency = (time.time() - t0) * 1000
    print(f"    Status: {status} | Latency: {latency:.1f}ms | HTML Size: {len(html)} bytes")
    
    print("\n[2] Handing over DOM Parsing to Scrapling Selector...")
    page = Selector(html)
    
    # Extract Repository Articles on GitHub Topics
    repo_articles = page.css("article.border")
    if not repo_articles:
        repo_articles = page.css("article")
    
    print(f"    Found {len(repo_articles)} candidate repository elements on GitHub!")
    
    results = []
    for idx, article in enumerate(repo_articles[:10], 1):
        # Extract owner and repo link accurately
        links = article.css("h3 a::attr(href)").getall()
        if len(links) >= 2:
            owner = links[0].strip("/ ")
            repo = links[1].strip("/ ")
            full_slug = f"{owner}/{repo}"
        elif len(links) == 1:
            full_slug = links[0].strip("/ ")
        else:
            full_slug = "Unknown/Repo"
            
        repo_url = f"https://github.com/{full_slug}"
        
        # Extract Star Count
        star_count = article.css("#repo-stars-counter-star::text").get()
        if not star_count:
            star_count = article.css("span.Counter::text").get() or "N/A"
            
        # Extract Description
        desc = article.css("div.color-fg-muted::text, p.color-fg-muted::text, p::text").get()
        desc_clean = desc.strip() if desc else "No description provided."
        
        # Extract Topic Tags
        topics = article.css("a.topic-tag::text").getall()
        topics_clean = [t.strip() for t in topics if t.strip()]
        
        results.append({
            "rank": idx,
            "repo": full_slug,
            "url": repo_url,
            "stars": star_count.strip(),
            "description": desc_clean,
            "topics": topics_clean[:4]
        })
        
    print("\n[3] Extracted GitHub Repositories via Scrapling Autonomous Engine:")
    print("-" * 70)
    for r in results:
        print(f"#{r['rank']:02d} | ⭐ {r['stars']:<6} | {r['repo']}")
        print(f"     URL:  {r['url']}")
        print(f"     Desc: {r['description'][:85]}...")
        if r['topics']:
            print(f"     Tags: [{', '.join(r['topics'])}]")
        print("-" * 70)
        
    return results

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "ai-agents"
    test_github_scrapling(q)
