from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time, re
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver

url = 'https://mars.nasa.gov/news/'
image_url = "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html"
#aws = "https://data-class-jpl-space.s3.amazonaws.com/"
aws = "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/"
mars_facts_url = 'https://space-facts.com/mars/'
hemisphere_image_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
main_hemisphere_url = 'https://astrogeology.usgs.gov'

def fetch(url):
    executable_path = {'executable_path': GeckoDriverManager().install()}
    browser = Browser('firefox', **executable_path, headless=True)
    browser.visit(url)
    html = browser.html
    return bs(html, 'html.parser')

def scrape():
    executable_path = {'executable_path': GeckoDriverManager().install()}
    browser = Browser('firefox', **executable_path, headless=True)
    ###
    soup = fetch(url)
    slide_cl = soup.find_all('li', class_='slide')
    content_title = slide_cl[0].find('div', class_ = 'content_title')
    article_teaser_body = slide_cl[0].find('div', class_ = 'article_teaser_body')
    news_title = content_title.text.strip()
    news_p = article_teaser_body.text.strip()
    ###
    soup = fetch(image_url)
    image_uri=soup.find("a", class_ = "fancybox-thumbs")["href"]
    featured_image_url = aws+image_uri
    tables = pd.read_html(mars_facts_url)
    facts_df = tables[0]
    facts_df.columns = ['Description', 'Mars']
    facts_df['Description'] = facts_df['Description'].str.replace(':', '')
    facts_html = facts_df.to_html()
    ###
    soup = fetch(hemisphere_image_url)
    items_cl = soup.find_all('div', class_='item')
    img_url=[]
    titles = []
    for item in items_cl:
        img_url.append(main_hemisphere_url + item.find('a')['href'])
        titles.append(item.find('h3').text.strip())
    img_urls = []
    for oneurl in img_url:
        browser.visit(oneurl)
        html = browser.html
        soup = bs(html, 'html.parser')
        oneurl = main_hemisphere_url+soup.find('img',class_='wide-image')['src']
        img_urls.append(oneurl)
    hemisphere_image_urls = []
    for i in range(len(titles)):
         hemisphere_image_urls.append({'title':titles[i],'img_url':img_urls[i]})
    marspage = {}
    marspage["news_title"] = news_title
    marspage["news_p"] = news_p
    marspage["featured_image_url"] = featured_image_url
    marspage["marsfacts_html"] = facts_html
    marspage["hemisphere_image_urls"] = hemisphere_image_urls

    return marspage