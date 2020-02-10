from newsapi import NewsApiClient
from newsplease import NewsPlease

from article import Article
from nltk.corpus import stopwords

import sys
import gensim

import numpy as np
import pandas as pd
import re, nltk, spacy

import unicodedata
import sys

from gensim.utils import simple_preprocess
from gensim.corpora.dictionary import Dictionary

tbl = dict.fromkeys(i for i in range(sys.maxunicode)
                    if unicodedata.category(chr(i)).startswith('P'))

NUM_TOPICS = 20

path_to_lda_all = 'ldamodel_all'


def remove_punctuation(txt):
    return txt.translate(tbl)


def tokenize(txt):
    X = []
    for t in txt:
        for sentence in nltk.sent_tokenize(t):
            # print(sentence)
            X.append(nltk.word_tokenize(remove_punctuation(t)))
    return X


def remove_stopwords(texts, stop_words):
    return [[word for word in simple_preprocess(str(doc)) if word not in stop_words] for doc in texts]


table = str.maketrans({'\"': ''})


def get_topics(ldamodel, num_words):
    topics_list = []
    all_topics = ldamodel.print_topics(num_words=num_words)
    for topic_index, topic in all_topics:
        sentence = []
        for value in topic.split('+'):
            value = value[value.index('*') + 1:]
            sentence.append(value.strip().translate(table))
        topics_list.append(sentence)
    return topics_list


def remove_duplicates(x):
    return list(dict.fromkeys(x))


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
            if art_value.url is not None:
                open(outputfile, 'a+').write(art_value.url)
                open(outputfile, 'a+').write("\n")
            if article is not None:
                open(outputfile, 'a+').write(article)
                open(outputfile, 'a+').write("\n")
            if art_value.image_url is not None:
                open(outputfile, 'a+').write(art_value.image_url)
                open(outputfile, 'a+').write("\n")
            if art_value.maintext is not None:
                open(outputfile, 'a+').write(art_value.maintext)
                open(outputfile, 'a+').write("\n\n\n")
        except OSError:
            print("Failed to open file to write article %s" % article)
        else:
            print("Successfully wrote article %s " % article)

    words = []
    with open(outputfile, 'r') as fin:
        for cnt, line in enumerate(fin):
            if line != "\n" and not line.startswith("http"):
                words.append(line)

    words_tokenized = tokenize(words)

    stop_words = stopwords.words('english')
    stop_words.extend(['from', 'subject', 're', 'edu', 'use', 'to', 'the', 'of', 'a', 'and', 'that', 'in', 'is', 'can',
                       'with', 'for', 'are', 'has'])

    without_stopwords = remove_stopwords(words_tokenized, stop_words)

    try:
        ldamodel_all = gensim.models.ldamodel.LdaModel.load(path_to_lda_all)
    except:
        print("Could not find models on disk! Will train.")
        print("Will generate dictionaries.")
        dictionary_all = Dictionary(without_stopwords)
        print("Will generate corpus")
        corpus_all = [dictionary_all.doc2bow(text) for text in without_stopwords]
        print("Will begin training...")
        ldamodel_all = gensim.models.ldamodel.LdaModel(
            corpus=corpus_all, num_topics=NUM_TOPICS, id2word=dictionary_all,
            update_every=5, chunksize=10000, passes=1)
        ldamodel_all.save(path_to_lda_all)
    print("Done training models. Saved them on disk.")

    all_topics = get_topics(ldamodel=ldamodel_all, num_words=10)
    for i, topic in enumerate(all_topics):
        print(i, topic)

    # print(topics)
    # topics = remove_duplicates(topics)
    # print(topics)

main(sys.argv[1:])
