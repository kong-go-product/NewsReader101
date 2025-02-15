import asyncio
import feedparser
import newspaper
import smtplib
import time
import pyppeteer
import tldextract
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from fpdf import FPDF
import subprocess
from readability import Document
import requests
from PDF_Layout import PDFLayout
from Scrapers import *
import html2text
from newspaper import Article
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from requests_html import HTMLSession
from bs4 import BeautifulSoup


# 指定 pyppeteer 的 Chromium 目录
os.environ["PYPPETEER_BROWSER"] = "C:\chrome-win\chrome.exe"


# 用于同步的包装函数
def get_page_content_sync(link):
    return asyncio.get_event_loop().run_until_complete(get_page_content(link))


# 异步获取页面内容
async def get_page_content(link):
    # 启动 pyppeteer 浏览器
    browser = await pyppeteer.launch(
        executablePath=os.environ["PYPPETEER_BROWSER"], headless=True
    )
    page = await browser.newPage()

    # 访问页面
    await page.goto(link, {"waitUntil": "domcontentloaded"})

    # 获取页面的HTML内容
    html_content = await page.content()

    # 关闭浏览器
    await browser.close()

    return html_content


# RSS feeds to fetch articles from
RSS_FEEDS = [
    # "https://feeds.bbci.co.uk/news/politics/rss.xml",
    # "https://sspai.com/feed",
    # "https://www.techweb.com.cn/rss/focus.xml"
    # "https://xueqiu.com/hots/topic/rss",
    # "https://thefilmstage.com/feed/"
    #   "https://collider.com/feed/"
    # "https://www.slashfilm.com/feed/"
    # Add more RSS feed URLs as needed
    "https://36kr.com/feed",
    "https://rss.huxiu.com/",
    # "https://www.tmtpost.com/feed",
    "https://www.geekpark.net/rss",
    # "https://www.techweb.com.cn/rss/focus.xml",
    # "https://rss.donews.com/rss/rss.xml"
    "https://www.ifanr.com/feed",
]

# Email Configuration
SMTP_SERVER = "smtp.exmail.qq.com"
SMTP_PORT = 587
USERNAME = "gaoqiangang@xhy353.wecom.work"
PASSWORD = f"password"
with open("recipients.txt", "r") as file:
    RECIPIENT_EMAIL = [line.strip() for line in file if line.strip()]
# 'gaomaixiaoxiao@126.com'


# Fetch article links from RSS feeds and include publication time
def fetch_article_links():
    links = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:  # Limit to top 5 articles
            # Retrieve publication date if available
            if "published" in entry:
                pub_date = entry.published
            elif "updated" in entry:
                pub_date = entry.updated
            elif "dc:date" in entry:
                pub_date = entry["dc:date"]
            else:
                pub_date = "Unknown Date"  # Default value if no date is available

            article_data = {
                "title": entry.title,
                "link": entry.link,
                "source": feed.feed.title,
                "pub_time": pub_date,  # Include publication time with a default value
            }
            links.append(article_data)
    return links


def get_second_level_domain(url):
    # Extract components of the URL
    ext = tldextract.extract(url)

    # The second-level domain is just the 'domain' component
    return ext.domain


# Extract full article content from each link
def extract_article_content(link):
    try:
        # Create an HTML Session
        # session = HTMLSession()

        # Get the page with JavaScript rendering
        # r = session.get(link)
        # r.html.render(timeout=20)  # Render JavaScript content

        # Use Readability to parse the HTML and extract main content
        # doc = Document(r.html.html)
        html_content = get_page_content_sync(link)
        doc = Document(html_content)
        title = doc.title()
        domain = get_second_level_domain(link)
        print(f"✦{title}" + "\n")  # Get the article title
        content = (
            f"**{title}**" + doc.summary()
        )  # Combine bold title and main content as HTML

        # Convert HTML to Markdown
        # html_to_md = html2text.HTML2Text()
        # html_to_md.ignore_links = False
        # html_to_md.ignore_images = False
        # html_to_md.body_width = 0  # Don't wrap text
        # text_content = html_to_md.handle(doc.title() + "\n\n" + content)
        # # Convert HTML to plain text
        # text_content = doc.title() + "\n\n" + content.strip()

        # Clean up the text content
        # cleaned_content = clean_text(content)
        soup = BeautifulSoup(content, "html.parser")
        # Convert heading and strong tags to markdown bold
        for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "strong"]):
            tag.string = f"**{tag.get_text()}**"

        for a_tag in soup.find_all(["a", "strong"]):
            a_tag.unwrap()

        soup = BeautifulSoup(str(soup), "html.parser")

        extracted_content = soup.get_text(separator="\n", strip=True)
        # extracted_content = '\n'.join([p.get_text(strip=True) for p in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong','p'])])

        # Close the session
        # session.close()

        return extracted_content

    except Exception as e:
        print(f"Error extracting content from {link}: {e}")
        return "Failed to fetch the article"


def clean_text(text):
    import re

    # Remove HTML tags for <p>, <img>, and <div>
    text = re.sub(r"<p.*?>", "", text)  # Remove <p> tags
    text = re.sub(r"</p>", "\n", text)  # Replace closing </p> with double newlines
    text = re.sub(r"<img.*?>", "", text)  # Remove <img> tags
    text = re.sub(r"<div.*?>", "", text)  # Remove <div> tags
    text = re.sub(r"</div>", "\n", text)  # Replace closing </div> with double newlines
    text = re.sub(r"<body.*?>", "", text)  # Remove <body> tags
    text = re.sub(
        r"</body>", "\n\n", text
    )  # Replace closing </body> with double newlines
    text = re.sub(r"<html.*?>", "", text)  # Remove <html> tags
    text = re.sub(
        r"</html>", "\n\n", text
    )  # Replace closing </html> with double newlines
    text = re.sub(r"<a.*?>", "", text)  # Remove <a> tags
    text = re.sub(r"</a>", "", text)  # Remove closing </a> tags

    # Remove extra whitespace and newlines
    lines = text.splitlines()
    cleaned_lines = [
        line.strip() for line in lines if line.strip()
    ]  # Remove empty lines

    # Remove any unwanted characters or HTML entities
    cleaned_lines = [
        re.sub(r"&[a-zA-Z0-9#]+;", "", line) for line in cleaned_lines
    ]  # Remove HTML entities
    cleaned_lines = [
        re.sub(r"\s+", " ", line) for line in cleaned_lines
    ]  # Replace multiple spaces with a single space

    # Join lines with double newlines for spacing
    cleaned_text = "\n\n".join(cleaned_lines)

    # Further clean up by removing any trailing spaces
    cleaned_text = cleaned_text.strip()

    return cleaned_text


# Generate the merged TXT file with articles and publication time
def create_txt_file(articles):
    with open("merged_articles.txt", "w", encoding="utf-8") as file:
        for article in articles:
            # Add a clear header section
            # file.write(" "*80 + "\n")
            # file.write("\n")

            # Write the article title and content
            file.write(article["content"])

            # Add a clear separator between articles
            file.write("\n" + "-" * 30 + "\n")


# Send the TXT file via email
def send_email(recipient, titles):
    # Email setup
    msg = MIMEMultipart()
    msg["From"] = "半路<" + USERNAME + ">"
    msg["To"] = recipient
    msg["Subject"] = "今天高效读报了吗？"

    # Create the email body with titles
    body = ""
    for title in titles:
        body += f"✦ {title.strip('*')}\n"  # Format each title with a bullet point
    body += "\nPlease find the attached articles.\n\nBest regards,\nYour NewsBoy\n"

    msg.attach(MIMEText(body, "plain"))

    # Attach PDF file
    with open(f"news_{datetime.now().strftime('%Y-%m-%d')}.pdf", "rb") as pdf_file:
        pdf_part = MIMEBase("application", "octet-stream")
        pdf_part.set_payload(pdf_file.read())
        encoders.encode_base64(pdf_part)
        pdf_part.add_header(
            "Content-Disposition",
            f'attachment; filename=news_{datetime.now().strftime("%Y-%m-%d")}.pdf',
        )
        msg.attach(pdf_part)
    # with open("merged_articles.txt", "rb") as file:
    #     part = MIMEBase('application', 'octet-stream')
    #     part.set_payload(file.read())
    #     encoders.encode_base64(part)
    #     part.add_header('Content-Disposition', f'attachment; filename=merged_articles.txt')
    #     msg.attach(part)

    # Send email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)


# Function to convert TXT to PDF with three columns, landscape A4 layout
def convert_txt_to_pdf():
    pdf = FPDF(orientation="L", unit="mm", format="A4")  # Landscape orientation
    pdf.add_page()

    # Set font for the document
    pdf.set_font("Arial", size=10)

    # Define the width of the columns
    column_width = (
        pdf.w - 20
    ) / 3  # Subtracting 20 for margins, then dividing by 3 columns

    # Read the TXT file to get the content
    with open("merged_articles.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Variables to track position in columns
    y_position = 10  # Starting Y position
    x_position = 10  # Starting X position

    # Write the content to the PDF
    for line in lines:
        if y_position > pdf.h - 20:  # Check if we are near the bottom of the page
            pdf.add_page()  # Add a new page if needed
            y_position = 10  # Reset Y position
            x_position = 10  # Reset X position

        pdf.set_xy(x_position, y_position)  # Set position for each line

        # Add text to the current column
        pdf.multi_cell(
            column_width, 10, line.encode("latin-1", "replace").decode("latin-1")
        )

        # Update Y position
        y_position += 10

        # If the current column is full, move to the next column
        if x_position + column_width < pdf.w - 10:
            x_position += column_width
        else:
            # Move to the next row if all columns are filled
            x_position = 10
            y_position += 10

    # Output the PDF to file
    pdf.output("merged_articles.pdf")
    print("PDF created successfully with three columns layout.")


# Main task to fetch, extract, and send articles
def main_task():
    print("Starting article fetch and send process...")
    titles = []
    articles = []
    scraped_links = []
    scraped_links.append(kr_scraper.KrScraper.get_first_news_link())
    scraped_links.append(Geek_scraper.GeekScraper.get_first_news_link())
    scraped_links.append(ifanr_scraper.IfanrScraper.get_first_news_link())
    scraped_links.append(huxiu_scraper.HuxiuScraper.get_first_news_link())
    scraped_links.append(sspai_scraper.SspaiScraper.get_first_news_link())

    # Combine all links
    print(scraped_links)

    for item in scraped_links:
        content = extract_article_content(item)
        articles.append({"content": content})
        # Assuming extract_article_content returns the title as well
        title = content.split("\n")[0]  # Get the title from the content
        titles.append(title)  # Store the title

    create_txt_file(articles)
    # subprocess.run(["python", "PDF_Layout.py"])
    txt_files = ["merged_articles.txt"]
    output_filename = f"news_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    pdf_layout = PDFLayout(output_filename, txt_files)
    pdf_layout.create_pdf()

    # Send email with titles included in the body
    for recipient in RECIPIENT_EMAIL:  # You can add more recipients to this list
        send_email(recipient, titles)  # Pass titles to the email function

    print("Articles fetched and email sent successfully.")
    print("PDF created successfully.")


# Run the main task immediately
import schedule
import time

# def job():
main_task()

# #Schedule the job to run at 8:45 every morning
# schedule.every().day.at("08:45").do(job)

# while True:
#    schedule.run_pending()
#   time.sleep(60)  # Wait one minute
