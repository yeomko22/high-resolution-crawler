## High Resolution Crawler
Collects high resolution images(not thumbnails) from google and naver.
All source code is based on scrapy framework.

## Currently Supporting Web sites
- google
- naver

![intro](./assets/google.png)  
## Install
`pip install -r requirements.txt`

## Run
- Edit keywords in keywords.txt  
- At project root path, run below commands
- `scrapy crawl google`
- `scrapy crawl naver`

## Advanced Configuration
- Further options can be set in src/setting.py (ex.num of threads) 
- You can also check scrapy official documents. [[link]](https://docs.scrapy.org/en/latest/topics/settings.html)
