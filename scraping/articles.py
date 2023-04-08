from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from db import db
from urllib.parse import urlparse, parse_qs, quote
from urllib.request import urlretrieve
from schema import Article
from PIL import Image
from datetime import datetime
from peewee import fn
from pathlib import Path

load_dotenv()

def getAllArticles():
    result = requests.get('https://www.nktolmin.si/arhiv/')
    result.encoding = result.apparent_encoding
    doc = BeautifulSoup(result.text, "html.parser")
    content = doc.find("div", {"class": "content withsidebar"})
    for article in content.find_all("a"):
        url = article.get('href')
        date = article.next_sibling.strip()
        print(url + " " + date)
        getArticle(url, date)
        
def getArticle(url, date):
    article_date = datetime.strptime(date, '(%d. %m. %Y)')
    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")
    article_id = Article.select(fn.MAX(Article.article_id)).scalar()
    article_id = 1 if article_id is None else article_id + 1
    content = doc.find("div", {"class": "content"})
    title = content.h2.text.strip()
    article = content.article
    allImages = [img.get('src') for img in article.find_all("img")]
    images=[]
    Path(f'./assets/articles/{article_id}').mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(allImages):
        if img is not None:
            img_name = img.split('/')[-1]
            img_path = f'./assets/articles/{article_id}/{quote(img_name)}'
            parsed = urlparse(img)
            full_path = os.getenv('BASE_URL')+f'api/assets/articles/{article_id}/{quote(img_name)}'
            try:
                if img.startswith('http'):
                    urlretrieve(f'{parsed.scheme}://{quote(parsed.netloc+parsed.path)}', img_path)
                else:
                    urlretrieve(urlparse(f'https://www.nktolmin.si/{img}'), img_path)
                article.find_all("img")[i]['src'] = full_path
                if article.find_all("img")[i].parent.name == 'a':
                    article.find_all("img")[i].parent['href'] = full_path
                    article.find_all("img")[i].parent['target'] = '_blank'
                    
                article.find_all("img")[i]['width'] = '100%'
                article.find_all("img")[i]['srcset'] = None
                article.find_all("img")[i]['sizes'] = None
                if article.find_all("img")[i]['height']:
                    article.find_all("img")[i]['height'] = None
                images.append(img_path[2:])
                # print(article.find_all("img")[i].parent)
                
            except Exception as e:
                print("Error: ", e)
    Article.create(article_id=article_id, title=title, content=str(article), created=article_date, updated=article_date, visible=True, images=images)
    
# getArticle('https://www.nktolmin.si/remi-za-uverturo-pred-novo-tribuno/', '(12. 3. 2023)')
# getAllArticles()
# getClubsFromSeason(seasons[6])
# addClub(693, '2022')
