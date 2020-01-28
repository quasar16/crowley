from newsplease import NewsPlease
from newsplease.crawler.spiders.rss_crawler import RssCrawler
from newsplease.helper import Helper

#art_name = 'https://news.google.com/search?cf=all&q=quantum&hl=en-US&gl=US&ceid=US:en'
# articles = NewsPlease.from_url(art_name)
# for article in articles:
#     print(article.title)

helper = Helper(cfg_heuristics=None,
                cfg_savepath=None,
                relative_to_path=None,
                format_relative_path=None,
                sites_object=None,
                crawler_class=RssCrawler,
                working_path=None
                )
rssCrawler = RssCrawler(helper=helper,
                        url='https://news.google.com/rss/search?q=quantum&hl=en-US&gl=US&ceid=US:en',
                        config='/usr/local/lib/python3.7/site-packages/newsplease/config/config.cfg',
                        ignore_regex=True)
response = []
rssCrawler.parse(rssCrawler, response)

print(response)


