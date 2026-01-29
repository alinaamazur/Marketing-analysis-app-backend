LIKELY is a marketing analytics platform that helps people understand their social media presence and brand positioning. It provides actionable insights into post performance, audience engagement, and the way a brand communicates online.

Features:
  1. Built with FastAPI: Handles API requests efficiently and securely.
  2. Instagram Data Retrieval: Fetches profile info, post metrics, and media details via the Instagram Graph API.
  3. Brand Tone Analysis: Uses text analysis on captions to categorize brand tone.
  4. Metrics Computation: Calculates likes, comments, engagement rate (ER), and aggregates sentiment across posts.
  5. Top Posts Identification: Returns top posts by engagement and brand tone.
  6. Flexible & Secure: Environment-configured with Instagram access tokens and business IDs.

Example API Endpoint:
GET /api/instagram/analysis?url=https://www.instagram.com/nike/&posts_limit=200

Returns:
  1. Profile info (name, username, profile picture, followers).
  2. Post metrics (likes, comments, ER).
  3. Brand Tone summary (Positive / Neutral / Negative).
  4. Top posts with captions, engagement, and sentiment.
