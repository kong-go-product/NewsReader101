import requests
from bs4 import BeautifulSoup
import json

class HuxiuScraper:
    URL = "https://www.huxiu.com/club/1000.html?object_type=51&object_id=1"

    @staticmethod
    def get_first_news_link():
        """
        Fetch the first news link from the huxiu news page.
        Returns:
            str: Full URL of the first news article or None if not found.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        response = requests.get(HuxiuScraper.URL, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the first '.content-item' element
        content_item = soup.find('div', class_='content-item')
        if not content_item:
            return None  # No matching element found

        # Extract the 'event-track-params' attribute
        event_track_params = content_item.get('event-track-params')
        if not event_track_params:
            return None  # Attribute not found

        # Decode JSON-like string (replacing &quot; with ")
        try:
            event_data = json.loads(event_track_params.replace('&quot;', '"'))
            brief_id = event_data['customize']['brief_id']
            # Construct the URL
            url = f'https://www.huxiu.com/brief/{brief_id}.html'
            return url
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON or extracting brief_id: {e}")
            return None
__all__ = ['HuxiuScraper']

HuxiuScraper.get_first_news_link()
