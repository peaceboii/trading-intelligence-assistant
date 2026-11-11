import aiohttp
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

async def fetch_market_news(symbol: str = "NVDA", limit: int = 5) -> List[Dict[str, str]]:
    sym = symbol.upper().strip()
    
    # 6-character forex pairs use =X (EURUSD=X); equities stay bare (NVDA)
    formatted_symbol = f"{sym}=X" if len(sym) == 6 and sym.isalpha() else sym
    
    # Primary working Yahoo RSS feed URL
    url = f"https://finance.yahoo.com/rss/headline?s={formatted_symbol}"
    
    news_items = []
    
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as response:
                if response.status == 200:
                    raw_xml = await response.text()
                    root = ET.fromstring(raw_xml)
                    
                    for item in root.findall(".//item")[:limit]:
                        title = item.find("title").text if item.find("title") is not None else ""
                        link = item.find("link").text if item.find("link") is not None else ""
                        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                        desc = item.find("description").text if item.find("description") is not None else ""
                        
                        clean_desc = desc.replace("<p>", "").replace("</p>", "").strip()
                        
                        if title:
                            news_items.append({
                                "title": title.strip(),
                                "summary": clean_desc[:250],
                                "published": pub_date,
                                "source": "Yahoo Finance RSS",
                                "url": link
                            })
        except Exception as e:
            print(f"[fetch_news] Error fetching from Yahoo RSS: {e}")
            
    # Secondary free fallback via Google News RSS if Yahoo yields 0 items
    if not news_items:
        google_url = f"https://news.google.com/rss/search?q={formatted_symbol}+stock+market&hl=en-US&gl=US&ceid=US:en"
        try:
            async with aiohttp.ClientSession(headers=HEADERS) as session:
                async with session.get(google_url, timeout=aiohttp.ClientTimeout(total=8)) as response:
                    if response.status == 200:
                        raw_xml = await response.text()
                        root = ET.fromstring(raw_xml)
                        for item in root.findall(".//item")[:limit]:
                            title = item.find("title").text if item.find("title") is not None else ""
                            link = item.find("link").text if item.find("link") is not None else ""
                            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                            
                            if title:
                                news_items.append({
                                    "title": title.strip(),
                                    "summary": title.strip(),
                                    "published": pub_date,
                                    "source": "Google Finance News",
                                    "url": link
                                })
        except Exception as e:
            print(f"[fetch_news] Error fetching from Google News fallback: {e}")

    return news_items