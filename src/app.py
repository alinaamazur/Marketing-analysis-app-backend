import os
import re
import time
from typing import List, Dict, Any
import requests
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_BUSINESS_ID = os.getenv("IG_BUSINESS_ID")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v24.0")

if not ACCESS_TOKEN or not IG_BUSINESS_ID:
    raise RuntimeError("ACCESS_TOKEN and IG_BUSINESS_ID must be set in .env")

app = FastAPI(title="Marketing Analysis App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_username(url: str) -> str:
    m = re.search(r"instagram\.com/([^/?#]+)/?", url)
    if not m:
        raise ValueError("Could not extract username from URL")
    return m.group(1)

def call_graph(api_path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{api_path}"
    params = params or {}
    params["access_token"] = ACCESS_TOKEN
    resp = requests.get(url, params=params, timeout=10)
    try:
        data = resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Invalid response from Graph API")
    if resp.status_code != 200 or "error" in data:
        # normalize error
        err = data.get("error", {})
        message = err.get("message") or data
        raise HTTPException(status_code=502, detail={"graph_error": message})
    return data

def fetch_business_discovery(username: str, posts_limit: int = 10) -> Dict[str, Any]:
    # fields: followers_count, media_count, media{like_count,comments_count,caption,timestamp,permalink}
    fields = (
        f"business_discovery.username({username})"
        "{followers_count,media_count,media.limit(%d){id,caption,like_count,comments_count,timestamp,permalink,media_type}}"
        % posts_limit
    )
    data = call_graph(f"{IG_BUSINESS_ID}", params={"fields": fields})
    return data.get("business_discovery")

def compute_metrics(business_discovery: Dict[str, Any]) -> Dict[str, Any]:
    # compute averages and engagement
    followers = business_discovery.get("followers_count")
    media_info = business_discovery.get("media", {}).get("data", [])
    posts_count = business_discovery.get("media_count") or len(media_info)

    posts = []
    likes_sum = 0
    comments_sum = 0
    er_list = []  # engagement per post = (likes + comments) / followers

    for p in media_info:
        likes = p.get("like_count") or 0
        comments = p.get("comments_count") or 0
        timestamp = p.get("timestamp")
        permalink = p.get("permalink")
        caption = p.get("caption") or ""
        posts.append({
            "id": p.get("id"),
            "caption": caption,
            "likes": likes,
            "comments": comments,
            "timestamp": timestamp,
            "permalink": permalink,
            "media_type": p.get("media_type")
        })
        likes_sum += likes
        comments_sum += comments
        if followers and followers > 0:
            er_list.append((likes + comments) / followers * 100.0)  # percent

    n = len(media_info) if media_info else 0
    avg_likes = likes_sum / n if n else 0
    avg_comments = comments_sum / n if n else 0
    avg_engagement = sum(er_list) / n if n else 0

    # ER total by last N posts (percent); also prepare data for chart (per post)
    chart = []
    for p, er in zip(media_info, er_list):
        chart.append({
            "timestamp": p.get("timestamp"),
            "permalink": p.get("permalink"),
            "er_percent": round(er, 4)
        })

    return {
        "followers": followers,
        "posts_count": posts_count,
        "n_returned_posts": n,
        "avg_likes": round(avg_likes, 2),
        "avg_comments": round(avg_comments, 2),
        "avg_engagement_percent": round(avg_engagement, 4),
        "posts": posts,
        "er_chart": chart,
    }

@app.get("/api/instagram/analysis")
def instagram_analysis(url: str = Query(..., description="Full Instagram profile url, e.g. https://www.instagram.com/nike/"), posts_limit: int = 10):
    """
    Returns:
      - followers
      - posts_count
      - avg_likes, avg_comments
      - avg_engagement_percent
      - posts[]
      - er_chart[]
    """
    try:
        username = extract_username(url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # fetch from Graph API
    bd = fetch_business_discovery(username, posts_limit=posts_limit)
    if not bd:
        raise HTTPException(status_code=404, detail="No business_discovery data. Maybe the account is not a Business/Creator account or not public.")

    result = compute_metrics(bd)
    # include username
    result["username"] = username
    result["scraped_at"] = int(time.time())
    return result