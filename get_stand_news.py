"""
Get the news content from the Standard news
"""
import os
import numpy as np
import sys
import time
from datetime import date, timedelta, datetime
import hashlib
import json

from news_collect.News import News
from news_collect.theStandNewsClient import theStandNewsClient

# Internal functions
def transform_url(url):
    if url.find('thestandnews.com') == -1:
        if url[0] == '/':
            sep = ''
        else:
            sep = '/'
        return f'https://thestandnews.com{sep}{url}'
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

        if not os.path.exists(f'./directory/{dt}'):
            os.makedirs(f'./directory/{dt}')

        if not os.path.isfile(f'./directory/{dt}/{md5_string}'):
            with open(f'./directory/{dt}/{md5_string}', 'w') as file:
                file.write(x.to_json())
        else:
            print(f'{md5_string} file already exists')

if __name__ == "__main__":
    mode = 1
    start_running_time = datetime.now()
    if len(sys.argv) > 1:
        mode = int(sys.argv[1])

    # Create news client
    stand_news = theStandNewsClient()

    if mode != 2:
        main_page = stand_news.get_article_list()
        save_content(main_page)
        time.sleep(4)

        # Other items in main page
        for items in stand_news.menu_items:
            print(f'Working on {items["category"]}')
            temp_content = stand_news.get_article_list(items['link'], items["category"])
            save_content(temp_content)
            
            time.sleep(10)
    else:
        print('Skip directory')

    if mode > 0:
        time_list = []
        if mode == 1:
            start_time = (datetime.now() - timedelta(days=3)).date()
            end_time = datetime.now().date()

            time_list = []
            while start_time <= end_time:
                time_list.append(start_time.strftime('%Y%m%d'))
                start_time += timedelta(days=1)
        else:
            time_list = os.listdir('./directory')

        if len(time_list) > 0:
            for dt in time_list:
                print(f'Running for {dt}')
                file_list = os.listdir(f'./directory/{dt}')
                for file_name in file_list:
                    if not os.path.isfile(f'./content/{dt}/{file_name}'):
                        with open(f'./directory/{dt}/{file_name}', 'r') as file:
                            old_info = json.loads(file.read())

                        article_detail = stand_news.get_article_detail(
                            transform_url(old_info['url']), 
                            old_info['category']
                        )
                        
                        if article_detail:
                            if not os.path.exists(f'./content/{dt}'):
                                os.makedirs(f'./content/{dt}')
                            with open(f'./content/{dt}/{file_name}', 'w') as file:
                                file.write(article_detail.to_json())

                        time.sleep(15)
    else:
        print('Skip news content')

    print('Overall running time: {d}'.format(
        d = (datetime.now() - start_running_time)
    ))