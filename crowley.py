from newsapi import NewsApiClient
from newsplease import NewsPlease

from article import Article
import sys


def main(argv):

    if argv.__len__() < 2:
        print("Usage: crowley date output_file")

    date = argv[0]
    outputfile = argv[1]

    print
    'Date is "', date
    print
    'Output file is "', outputfile

    newsapi = NewsApiClient(open("token", 'r').read())

    # Get articles urls
    qc_articles = newsapi.get_everything(q='quantum computing',
                                         from_param=date,
                                         language='en',
                                         sort_by='relevancy')
    qp_articles = newsapi.get_everything(q='quantum physics',
                                         from_param=date,
                                         language='en',
                                         sort_by='relevancy')
    qm_articles = newsapi.get_everything(q='quantum physics',
                                         from_param=date,
                                         language='en',
                                         sort_by='relevancy')
    all_urls = []
    for article in qc_articles.get('articles'):
        all_urls.append(article.get('url'))
    for article in qp_articles.get('articles'):
        all_urls.append(article.get('url'))
    for article in qm_articles.get('articles'):
        all_urls.append(article.get('url'))

    # Get content of urls
    all_articles = NewsPlease.from_urls(all_urls)

    articles = {}
    for article in all_articles.values():
        articles[article.title] = Article(article.image_url, article.url, article.maintext)

    # Write urls in file
    for article in articles:

        art_value = articles[article]
        try:
            open(outputfile, 'a+').write(art_value.url)
            open(outputfile, 'a+').write("\n")
            open(outputfile, 'a+').write(article)
            open(outputfile, 'a+').write("\n")
            open(outputfile, 'a+').write(art_value.image_url)
            open(outputfile, 'a+').write("\n")
            open(outputfile, 'a+').write(art_value.maintext)
            open(outputfile, 'a+').write("\n\n\n")
        except OSError:
            print("Failed to open file to write article %s" % article)
        else:
            print("Successfully wrote article %s " % article)


main(sys.argv[1:])
