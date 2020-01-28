from newsplease import NewsPlease

art_name = 'https://news.google.com/search?cf=all&q=quantum&hl=en-US&gl=US&ceid=US:en'
articles = NewsPlease.from_url(art_name)
for article in articles:
    print(article.title)
