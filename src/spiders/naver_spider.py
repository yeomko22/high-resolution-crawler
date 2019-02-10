import os
import re
from urllib.parse import unquote
import time
from io import BytesIO

import scrapy
from PIL import Image


class NaverSpider(scrapy.Spider):
    name = "naver"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keywords = []
        self.save_root = os.path.abspath('./download')
        if not os.path.exists(self.save_root):
            os.mkdir(self.save_root)

        # read keywords.txt and make save directories
        with open(os.path.abspath('./keywords.txt'), 'r') as keywords:
            for line in keywords:
                keyword = line.replace('\n', '')
                self.keywords.append(keyword)

                save_dir = os.path.join(self.save_root, keyword + '_naver')
                if not os.path.exists(save_dir):
                    os.mkdir(save_dir)
        print('input keyword : %s' % self.keywords)

        self.start_urls = ['https://www.naver.com']
        self.search_url = 'https://search.naver.com/search.naver?where=image&sm=tab_jum'
        self.max_page = 20
        self.re_imgurl = re.compile(r'originalUrl":"http\S+.(?:jpg|jpeg|png)')

    def parse(self, response):
        for keyword in self.keywords:
            for i in range(0, self.max_page):
                new_url = '%s&query=%s&start=%d&display=%d' % (self.search_url, keyword, ((50*i)+1), 50)
                new_request = scrapy.Request(url=new_url,
                                             callback=self.parse_search)
                new_request.meta['keyword'] = keyword
                yield new_request

    def parse_search(self, response):
        keyword = response.meta['keyword']
        search_result = str(response.body)
        img_urls = self.re_imgurl.findall(search_result)
        for img_url in img_urls:
            img_url = unquote(img_url)
            img_url = img_url.replace('originalUrl":"', '')
            img_url = img_url.replace('"', '')

            new_request = scrapy.Request(url=img_url,
                                         callback=self.parse_img)
            new_request.meta['keyword'] = keyword
            yield new_request

    def parse_img(self, response):
        # download image file and exception covers
        try:
            image = Image.open(BytesIO(response.body))
        except OSError as e:
            print("fail to download:", e)
            return
        except KeyError as e:
            print("fail to download:", e)
            return
        except IOError as e:
            print("fail to download:", e)
            return

        # filter too small image
        width, height = image.size
        if width < 200 and height < 200:
            return

        keyword = response.meta['keyword']
        filename = '%s.jpg' % str(time.time())
        save_path = os.path.join(self.save_root, keyword + '_naver', filename)

        try:
            image.save(save_path)
        except IOError as e:
            print("fail to save:", e)
        except OSError as e:
            print("fail to save:", e)
