import requests
from bs4 import BeautifulSoup

class KrScraper:
    BASE_URL = "https://36kr.com"
    URL = "https://36kr.com/motif/327685521409"

    @staticmethod
    def get_first_news_link():
        """
        Fetch the first news link from the 36kr news page.
        Returns:
            str: Full URL of the first news article or None if not found.
        """
        try:
            response = requests.get(KrScraper.URL)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                first_news_item = soup.find('a', class_='article-item-title weight-bold')
                if first_news_item:
                    relative_link = first_news_item.get('href')
                    return f"{KrScraper.BASE_URL}{relative_link}"
                else:
                    print("No news item found!")
                    return None
            else:
                print(f"Failed to fetch the page. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

__all__ = ['KrScraper']
