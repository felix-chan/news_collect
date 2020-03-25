"""
Get the news content from Ming Pao
"""
import os
import numpy as np
import sys
import time
from datetime import date, timedelta, datetime
import hashlib
import json
import re

from news_collect.News import News
from news_collect.mingPaoClient import mingPaoClient

import logging
logging.basicConfig(level=logging.INFO,
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            filename="log/mingpao.log")

daily_url = [
    'pns/%E8%A6%81%E8%81%9E/section/latest/s00001', 
    'pns/%E6%B8%AF%E8%81%9E/section/latest/s00002', 
    'pns/%E7%B6%93%E6%BF%9F/section/latest/s00004', 
    'pns/%E7%A4%BE%E8%A9%95/section/latest/s00003', 
    'pns/%E8%A7%80%E9%BB%9E/section/latest/s00012', 
    'pns/%E4%B8%AD%E5%9C%8B/section/latest/s00013', 
    'pns/%E5%9C%8B%E9%9A%9B/section/latest/s00014'
]

# Internal functions
def transform_url(url):
    # Replace the ../
    url = re.sub(r'^\.\.', '', url)
    if url.find('news.mingpao.com') == -1:
        if url[0] == '/':
            sep = ''
        else:
            sep = '/'
        return f'https://news.mingpao.com{sep}{url}'
    else:
        return url

def save_content(news_list):
    for x in news_list:
        x_dict = x.to_dict()
        full_url = transform_url(x_dict['url'])
        tx = hashlib.md5()
        tx.update(full_url.encode('utf-8'))
        md5_string = tx.hexdigest()
        dt = x_dict['datetime'].strftime('%Y%m%d')

        if not os.path.exists(f'./mp/directory/{dt}'):
            os.makedirs(f'./mp/directory/{dt}')

        if not os.path.isfile(f'./mp/directory/{dt}/{md5_string}'):
            with open(f'./mp/directory/{dt}/{md5_string}', 'w') as file:
                file.write(x.to_json())
        else:
            logging.warning(f'{md5_string} file already exists')

if __name__ == "__main__":
    mode = 1
    start_running_time = datetime.now()
    if len(sys.argv) > 1:
        mode = int(sys.argv[1])

    # Create news client
    mp_news = mingPaoClient()

    if mode != 2:
        logging.info('Working on recent news')
        main_page = mp_news.get_article_list()
        save_content(main_page)
        time.sleep(4)

        # Other items in main page
        for current_url in daily_url:
            logging.info(f'Working on {current_url}')
            temp_content = mp_news.get_daily_news_list(transform_url(current_url))
            save_content(temp_content)
        
            time.sleep(8)
    else:
        logging.warning('Skip directory')

    if mode > 0:
        time_list = []
        if mode == 1:
            start_time = (datetime.now() - timedelta(days=1)).date()
            end_time = datetime.now().date()

            time_list = []
            while start_time <= end_time:
                time_list.append(start_time.strftime('%Y%m%d'))
                start_time += timedelta(days=1)
        else:
            time_list = os.listdir('./mp/directory')

        if len(time_list) > 0:
            for dt in time_list:
                logging.info(f'Running for {dt}')
                if os.path.exists(f'./mp/directory/{dt}'):
                    file_list = os.listdir(f'./mp/directory/{dt}')
                    for file_name in file_list:
                        if not os.path.isfile(f'./mp/content/{dt}/{file_name}'):
                            with open(f'./mp/directory/{dt}/{file_name}', 'r') as file:
                                old_info = json.loads(file.read())

                            article_detail = mp_news.get_article_detail(
                                transform_url(old_info['url']), 
                                old_info['category']
                            )
                            
                            if article_detail:
                                logging.info(f'Saving json {file_name}')
                                if not os.path.exists(f'./mp/content/{dt}'):
                                    os.makedirs(f'./mp/content/{dt}')
                                with open(f'./mp/content/{dt}/{file_name}', 'w') as file:
                                    file.write(article_detail.to_json())

                            time.sleep(15)
                else:
                    logging.warning(f'Path {dt} does not exists')
    else:
        logging.warning('Skip news content')

    print('Overall running time: {d}'.format(
        d = (datetime.now() - start_running_time)
    ))