import requests
from bs4 import BeautifulSoup

class GeekScraper:
    BASE_URL = "https://www.geekpark.net"
    URL = "https://www.geekpark.net/column/74"

    @staticmethod
    def get_first_news_link():
        """
        Fetch the first news link from the Geek news page.
        Returns:
            str: Full URL of the first news article or None if not found.
        """
        try:
            response = requests.get(GeekScraper.URL)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                first_news_item = soup.find('a', class_='img-cover-wrap')
                if first_news_item:
                    relative_link = first_news_item.get('href')
                    return f"{GeekScraper.BASE_URL}{relative_link}"
                else:
                    print("No news item found!")
                    return None
            else:
                print(f"Failed to fetch the page. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

__all__ = ['GeekScraper']
