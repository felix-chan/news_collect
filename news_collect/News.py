"""
News object to store news contents
"""

import json
from dateutil import parser

class News:
    """
    News object to store news contents

    Args
    ====

        media: Media name
        title: News title
        author: Author Name
        category: News category
        url: Link to news content
        datetime_text: News reference datetime in text format
        summary: News description or full news content
    """
    media = None
    title = None
    author = None
    category = None
    url = None
    datetime = None
    summary = None
    
    def __init__(self, media, title, author, category, url, datetime_text, 
                 summary, datetime_fun = None):
        self.media = media
        self.title = title
        self.author = author
        self.category = category
        self.url = url
        self.summary = summary
        
        if datetime_fun is None:
            self.datetime = parser.parse('2019-02-03 12:33:12')
        else:
            self.datetime = datetime_fun(datetime_text)
            
    def to_json(self):
        """
        Return stringify JSON object

        Args
        ====
            None

        Return
        ======
            Stringify JSON object
        """
        return json.dumps({
            'media': self.media,
            'title': self.title,
            'author': self.author,
            'category': self.category,
            'url': self.url,
            'datetime': str(self.datetime),
            'summary': self.summary
        })

    def __str__(self):
        return self.to_json()