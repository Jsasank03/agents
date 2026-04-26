from ddgs import DDGS

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from playwright.sync_api import sync_playwright
from typing import List, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor

def is_dynamic_url(url: str, timeout: int = 10) -> bool:
    """
    Check if a URL is dynamic by comparing requests and selenium content.
    Returns True if dynamic, False if static.
    """
    try:
        # Get content with requests
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        requests_content = response.text

        # Get content with Playwright (faster than Selenium)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=timeout*1000)
            playwright_content = page.content()
            browser.close()

        # Compare lengths - if significantly different, likely dynamic
        len_requests = len(requests_content)
        len_playwright = len(playwright_content)

        # If Playwright content is significantly larger, it's dynamic
        if len_playwright > len_requests * 1.5:  # 50% larger suggests dynamic content
            return True

        # Check for common dynamic page indicators
        soup = BeautifulSoup(requests_content, 'html.parser')
        if soup.find('div', {'id': 'root'}) or soup.find('div', {'id': 'app'}):
            return True

        return False

    except Exception as e:
        print(f"Error checking {url}: {str(e)}")
        return True  # Assume dynamic if we can't check properly

def separate_static_dynamic_urls(urls: List[str]) -> Tuple[List[str], List[str]]:
    """
    Separate URLs into static and dynamic lists.
    Returns (static_urls, dynamic_urls)
    """
    static_urls = []
    dynamic_urls = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(is_dynamic_url, urls))

    for url, is_dynamic in zip(urls, results):
        if is_dynamic:
            dynamic_urls.append(url)
        else:
            static_urls.append(url)

    return static_urls, dynamic_urls

def fetch_static_content(urls: List[str]) -> List[Dict]:
    """
    Fetch content from static URLs using requests.
    Returns list of {'url': str, 'content': str}
    """
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            results.append({
                'url': url,
                'content': response.text
            })
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            results.append({
                'url': url,
                'content': f"Error fetching content: {str(e)}"
            })

    return results

def fetch_dynamic_content(urls: List[str]) -> List[Dict]:
    """
    Fetch content from dynamic URLs using Playwright.
    Returns list of {'url': str, 'content': str}
    """
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for url in urls:
            try:
                page = browser.new_page()
                page.goto(url, timeout=30000)
                content = page.content()
                results.append({
                    'url': url,
                    'content': content
                })
                page.close()
            except Exception as e:
                print(f"Error fetching {url}: {str(e)}")
                results.append({
                    'url': url,
                    'content': f"Error fetching content: {str(e)}"
                })
        browser.close()

    return results

def get_combined_html_content(urls: List[str]) -> List[Dict]:
    """
    Main function to get combined HTML content from all URLs.
    Returns list of {'url': str, 'content': str} for LangChain processing.
    """
    # Separate static and dynamic URLs
    static_urls, dynamic_urls = separate_static_dynamic_urls(urls)

    print(f"Detected {len(static_urls)} static URLs and {len(dynamic_urls)} dynamic URLs")

    # Fetch content in parallel
    with ThreadPoolExecutor(max_workers=2) as executor:
        static_future = executor.submit(fetch_static_content, static_urls)
        dynamic_future = executor.submit(fetch_dynamic_content, dynamic_urls)

        static_results = static_future.result()
        dynamic_results = dynamic_future.result()

    # Combine results
    combined_results = static_results + dynamic_results
    return combined_results



def external_search_api_duck(query: str, max_results: int = 3) -> list:
    """Search DuckDuckGo and return results with URLs."""
    results = DDGS().text(query, max_results=max_results)
    return [
        {"title": result["title"], "url": result["href"], "snippet": result["body"]}
        for result in results
    ]



# Example usage
if __name__ == "__main__":

    # Example usage
    results = external_search_api_duck("Top 5 smartphones in 2026")
    for result in results:
        print(result["url"])
    results = external_search_api_duck("List of present MPs of AP constituency wise of 2024 general elections", max_results=1)
    urls = []
    for result in results:
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"Snippet: {result['snippet']}\n")
        urls.append(result['url'])

    results = get_combined_html_content(urls)
    # Now you can use these results with LangChain
    for result in results:
        print(f"URL: {result['url']}")
        print(f"Content length: {len(result['content'])} characters")
        print("---")