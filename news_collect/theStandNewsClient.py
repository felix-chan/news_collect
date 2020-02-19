"""
The Stand News client to extract news from the Stand News. It can get
 the news index and the news content
"""
import requests
import lxml

from datetime import datetime, date
import json
from dateutil import parser
import re
from bs4 import BeautifulSoup
from News import News

class theStandNewsClient:
    
    menu_items = None
    
    def __get_html_file(self, url):
        """
        Get the HTML file from either url address (online)
         or local cached file

        Args
        ====
            url: The url / file path of html file
        
        Return
        ======
            String variable of html
        """
        if url.find('http') == 0:
            r = requests.get(url)
            if r.status_code == 200:
                # Success
                html_content = r.text
                return html_content
            else:
                raise Exception(f'Fail to open {url} with error code {r.status_code}')
        else:
            with open(url, 'rb') as file:
                html_content = file.read()
                return html_content
    
    def get_article_list(self, url = 'https://www.thestandnews.com/'):
        """
        Get the list of News object extract from news directory

        Args
        ====
            url: The url of news directory
        
        Return
        ======
            List of News Object
        """
        news_dir = self.__get_html_file(url)
        soup = BeautifulSoup(news_index, 'lxml')
        
        # Fulfill menu first
        if self.menu_items is None:
            menu = soup.select('.menu-list li a')
            menu_items = []
            appended_items = []
            for m_items in menu:
                if m_items['href'].find('thestandnews.com') == -1:
                    link = 'https://thestandnews.com{link}'.format(
                        link = m_items['href']
                    )
                else:
                    link = m_items['href']
                
                if (not link in appended_items) \
                    and (m_items.string is not None):
                    menu_items.append({
                        'category': m_items.string,
                        'link': link
                    })
                    appended_items.append(link)
                
            self.menu_items = menu_items
            
        
        news_list = []
        
        # Get the article list
        for items in soup.select("div.article-block"):
            try:
                title_obj = items.select('h3 a')
                summary = items.select('p.desc')
                author = items.select('.author a')
                cat = items.select('span.category-title')
                d = items.select('span.date')
                if len(title_obj) > 0:
                    news_item = News(
                        'The Stand News',
                        title_obj[0].string,
                        author[0].string.strip(),
                        cat[0].string,
                        title_obj[0]['href'],
                        d[0].string.split('—'),
                        summary[0].string.strip(),
                        self._standnews_dt
                    )
                    news_list.append(news_item)
            except:
                print(x)
                break
            
                
        return news_list
    
    def _standnews_dt(self, dt_obj):
        """
        Internal function to convert datetime in string format
         to datetime object
        
        Args
        ====
            dt_obj: List of string or string

        Return
        ======
            Datetime object
        """
        if len(dt_obj) > 1:
            dt_text = '{a} {b}'.format(
                a = dt_obj[0].strip(),
                b = dt_obj[1].strip()
            )
        else:
            dt_text = dt_obj
        
        return datetime.strptime(dt_text, '%Y/%m/%d %H:%M')
    
    def get_article_detail(self, url, cat = None):
        """
        Get the content of news article

        Args
        ====
            url: The url of news directory
            cat: Category of news article, default None
        
        Return
        ======
            News Object
        """
        news_content = self.__get_html_file(url)
        
        soup = BeautifulSoup(news_content, 'lxml')
        
        author = soup.select('h4 a[rel=author]')[0]
        title = soup.select('h1')[0]
        dt = soup.select('article .date')[0]
        article = soup.select('article .article-content')
        contents = BeautifulSoup(
            re.sub('<script[^>]*>[^<]*</script>', '', str(article[0]))
                .replace('</p>', '</p>\n'), 
            'lxml').text
        
        return News(
            'The Stand News',
            title.string.strip(),
            author.string.strip(),
            cat,
            url,
            dt.string.split('—'),
            contents.strip(),
            self._standnews_dt
        )