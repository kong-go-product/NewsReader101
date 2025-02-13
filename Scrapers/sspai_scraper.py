import requests
from bs4 import BeautifulSoup

class SspaiScraper:
    def get_first_news_link(url="https://sspai.com/"):
        """
        Fetches the newest article containing '派早报' from the specified URL.
        
        :param url: The URL of the webpage to scrape
        :return: The full URL of the newest article or None if not found
        """
        # Fetch the HTML content from the URL
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all anchor tags containing '派早报'
        articles = []

        # Loop through all anchor tags and filter based on the text content
        for a in soup.find_all('a'):
            if a.text and '派早报' in a.text:
                href = a.get('href')
                # Handle relative and absolute URLs
                full_url = href if href.startswith('http') else f'https://sspai.com{href}'
                articles.append(full_url)
        
        # Return the newest article, which is expected to be the first in the list
        if articles:
            return articles[0]
        else:
            return None


# #Usage example:
# url = 'https://sspai.com/'
# newest_article = get_first_news_link(url)

# if newest_article:
#     print(f"The link to the newest article: {newest_article}")
# else:
#     print("No '派早报' article found.")

    



