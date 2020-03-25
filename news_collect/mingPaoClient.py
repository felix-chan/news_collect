"""
MingPao News client to extract news from MingPao. It can get
 the news index and the news content
"""
import requests
import lxml

from datetime import datetime, date
import json
from dateutil import parser
import re
from bs4 import BeautifulSoup
from .News import News
from urllib.parse import unquote
import logging

class mingPaoClient:
    
    menu_items = None
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) '
                       'Gecko/20100101 Firefox/73.0'),
        'Accept': ('text/html,application/xhtml+xml,application/xml;'
                   'q=0.9,image/webp,*/*;q=0.8'),
        'Cookie': 'mpLoginStatus=nologin'
    }
    
    def __get_html_file(self, url, this_headers = None):
        """
        Get the HTML file from either url address (online)
         or local cached file

        Args
        ====
            url: The url / file path of html file
            this_headers: Dict of suitable headers
        
        Return
        ======
            String variable of html
        """
        if url.find('http') == 0:
            headers = this_headers if this_headers is not None else \
                self.headers
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                # Success
                r.encoding = 'UTF-8'
                html_content = r.text
                return html_content
            else:
                raise Exception(f'Fail to open {url} with error code {r.status_code}')
        else:
            with open(url, 'rb') as file:
                html_content = file.read()
                return html_content
    
    def get_article_list(self, 
        url = 'https://news.mingpao.com/ins/%E5%8D%B3%E6%99%82%E6%96%B0%E8%81%9E/main'):
        """
        Get the list of News object extract from news directory

        Args
        ====
            url: The url of news directory
        
        Return
        ======
            List of News Object
        """

        news_list = []
        try:
            news_page = self.__get_html_file(url)
            load_page = True
        except Exception as e:
                logging.error(e)

        if load_page:
            soup = BeautifulSoup(news_page, 'lxml')

            news_box = soup.select('.contentwrapper')

            for items in news_box:
                try:
                    cat = items.select('h2')[0].text
                    url = items.select('h2 a')[0]['href']
                    title = items.select('h2')[1].text
                    summary = items.select('p')[0].text
                    dtval = items.select('.time script')[0]
                    news_item = News(
                        'MingPao',
                        title,
                        None,
                        cat if len(cat) > 0 else None,
                        url,
                        dtval.text,
                        summary,
                        self._mingpao_current_news_dt
                    )
                    news_list.append(news_item)
                except:
                    logging.error(items)
                    pass
        return news_list

    def get_daily_news_list(self, url):
        """
        Get the list of News object extract from daily news directory

        Args
        ====
            url: The url of news directory
        
        Return
        ======
            List of News Object
        """

        news_list = []
        try:
            news_page = self.__get_html_file(url)
            load_page = True
        except Exception as e:
                logging.error(e)

        if load_page:
            soup = BeautifulSoup(news_page, 'lxml')

            news_box = soup.select('.listing')

            for news_section in news_box:
                for link in news_section.select('a'):
                    try:
                        title = link.string
                        url = link['href']
                        url_zh = unquote(url).split('/')
                        news_item = News(
                            'MingPao',
                            title,
                            None,
                            url_zh[2] if len(url_zh) > 2 else None,
                            url,
                            url_zh[4] if len(url_zh) > 4 else None,
                            None,
                            self._mingpao_daily_news_dt
                        )
                        news_list.append(news_item)
                    except:
                        logging.warning(f'Fail to get the news URL: {link}')
                        pass
        
        return news_list


    def _mingpao_current_news_dt(self, time_txt):
        """
        Internal function to convert datetime in string format
         to datetime object
        
        Args
        ====
            time_txt: string or string

        Return
        ======
            Datetime object
        """

        t1 = re.search((r'(?P<year>[0-9]{4})\/(?P<month>[0-9]{1,2})\/'
                        r'(?P<day>[0-9]{1,2}) (?P<hour>[0-9]{1,2}):'
                        r'(?P<min>[0-9]{1,2}):(?P<second>[0-9]{1,2})'), 
                        time_txt)

        if t1:
            return datetime(int(t1.group('year')),
                            int(t1.group('month')),
                            int(t1.group('day')),
                            int(t1.group('hour')),
                            int(t1.group('min')),
                            int(t1.group('second')))
        else:
            logging.error(f'Fail to parse time {time_txt}')
            return datetime.now()

    def _mingpao_daily_news_dt(self, time_txt):
        """
        Internal function to convert datetime in string format
         to datetime object
        
        Args
        ====
            time_txt: string or string

        Return
        ======
            Datetime object
        """

        t1 = re.search((r'(?P<year>[0-9]{4})(?P<month>[0-9]{1,2})'
                        r'(?P<day>[0-9]{1,2})'), 
                        time_txt)

        if t1:
            return datetime(int(t1.group('year')),
                            int(t1.group('month')),
                            int(t1.group('day')))
        else:
            logging.error(f'Fail to parse time {time_txt}')
            now = datetime.now()
            return datetime(now.year, now.month, now.day)

    def _mp_dt(self, time_txt):
        """
        Internal function to convert datetime in string format
         to datetime object
        
        Args
        ====
            time_txt: string or string

        Return
        ======
            Datetime object
        """
        find_date = re.search('([0-9]{4})年([0-9]{1,2})月([0-9]{1,2})日', time_txt)
        if find_date:
            return datetime(int(find_date.group(1)), int(find_date.group(2)), 
                            int(find_date.group(3)))
        else:
            today = datetime.now()
            return datetime(today.year, today.month, today.day)

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

        try:
            news_content = self.__get_html_file(url)
            
            soup = BeautifulSoup(news_content, 'lxml')
            
            author = None
            cat_obj = soup.select('#blockcontent h3')
            if len(cat_obj) == 0:
                cat_obj = soup.select('.group h3')
            cat = cat_obj[0].string

            title = soup.select('h1')[0].text
            dt_obj = [x.string for x in soup.select('div.date') if x.string.find('年') > 0]
            if len(dt_obj) == 0:
                dt_obj = [x.string for x in soup.select('h6') if x.string.find('年') > 0]
            dt = dt_obj[0]

            article_obj = soup.select('article.txt4')
            if len(article_obj) == 0:
                article_obj = soup.select('.article_content')
            contents = article_obj[0].text.strip()
            
            return News(
                'MingPao',
                title,
                author,
                cat,
                url,
                dt,
                contents,
                self._mp_dt
            )
        except Exception as e:
            logging.error(f'Reading {url} with error')
            logging.error(e)

            return None