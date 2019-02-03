import os
import re
import time
from io import BytesIO

import scrapy
from PIL import Image


class GoogleSpider(scrapy.Spider):
    name = "google"

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

                save_dir = os.path.join(self.save_root, keyword)
                if not os.path.exists(save_dir):
                    os.mkdir(save_dir)
        print('input keyword : %s' % self.keywords)

        self.start_urls = ['https://www.google.com']
        self.search_url = 'https://www.google.com/search?ei=F9JWXOu9F4O08QWjy734Cw&yv=3&newwindow=1&tbm=isch&vet=10ahUKEwirpfW5vJ_gAhUDWrwKHaNlD78QuT0IOygB.F9JWXOu9F4O08QWjy734Cw.i&ved=0ahUKEwirpfW5vJ_gAhUDWrwKHaNlD78QuT0IOygB&asearch=ichunk&async=_id:rg_s,_pms:s,_fmt:pc'
        self.max_page = 10
        self.re_imgurl = re.compile(r'imgurl=http[s]?://\S+.(?:jpg|jpeg|png)')

    def parse(self, response):
        for keyword in self.keywords:
            for i in range(0, self.max_page):
                new_url = '%s&q=%s&ijn=%d&start=%d' % (self.search_url, keyword, i, (i * 100))
                new_request = scrapy.Request(url=new_url,
                                             callback=self.parse_search)
                new_request.meta['keyword'] = keyword
                yield new_request

    def parse_search(self, response):
        keyword = response.meta['keyword']
        search_result = str(response.body)
        img_urls = self.re_imgurl.findall(search_result)
        for img_url in img_urls:
            img_url = img_url.replace('imgurl=','')
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
        save_path = os.path.join(self.save_root, keyword, filename)

        try:
            image.save(save_path)
        except IOError as e:
            print("fail to save:", e)
        except OSError as e:
            print("fail to save:", e)
