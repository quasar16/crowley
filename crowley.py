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
import json

from gensim.utils import simple_preprocess
from gensim.corpora.dictionary import Dictionary

tbl = dict.fromkeys(i for i in range(sys.maxunicode)
                    if unicodedata.category(chr(i)).startswith('P'))

NUM_TOPICS = 6

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


def format_topics_sentences(ldamodel, corpus, texts):
    # Init output
    sent_topics_df = pd.DataFrame()

    # Get main topic in each document
    for i, row in enumerate(ldamodel[corpus]):
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                sent_topics_df = sent_topics_df.append(
                    pd.Series([int(topic_num), round(prop_topic, 4), topic_keywords]), ignore_index=True)
            else:
                break
    sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']

    # Add original text to the end of the output
    contents = pd.Series(texts)
    sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
    return (sent_topics_df)


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
    all_urls = []
    for article in qc_articles.get('articles'):
        all_urls.append(article.get('url'))
    for article in qp_articles.get('articles'):
        all_urls.append(article.get('url'))

    print("All articles ", all_urls.__len__())

    # Get content of urls
    all_articles = NewsPlease.from_urls(all_urls)

    articles = {}
    for article in all_articles.values():
        articles[article.title] = Article(article.image_url, article.url, article.maintext)

    # Write urls in file
    open(outputfile, 'w').truncate(0)
    json_data = {}
    json_article = {}
    for article in articles:

        art_value = articles[article]
        if art_value.url is not None and article is not None and art_value.image_url is not None and \
                art_value.maintext is not None:
            json_article[art_value.url] = art_value.maintext
            print("Successfully wrote article %s " % article)

    json_data['content'] = json_article
    try:
        open(outputfile, 'w').write(json.dumps(json_data))
    except OSError:
        print("Failed to open file to write article %s" % article)

    df = pd.read_json(outputfile)
    df.head()
    data = df.content.values.tolist()
    data = [re.sub('\S*@\S*\s?', '', sent) for sent in data]
    data = [re.sub('\s+', ' ', sent) for sent in data]
    data = [re.sub("\'", "", sent) for sent in data]

    words_tokenized = tokenize(data)

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

        df_topic_sents_keywords = format_topics_sentences(ldamodel=ldamodel_all, corpus=corpus_all,
                                                          texts=without_stopwords)

        # Format
        df_dominant_topic = df_topic_sents_keywords.reset_index()
        df_dominant_topic.columns = ['Document_No', 'Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords', 'Text']

        # Show
        print(df_dominant_topic.head(5))

        # Group top 5 sentences under each topic
        sent_topics_sorteddf_mallet = pd.DataFrame()

        sent_topics_outdf_grpd = df_topic_sents_keywords.groupby('Dominant_Topic')

        for i, grp in sent_topics_outdf_grpd:
            sent_topics_sorteddf_mallet = pd.concat([sent_topics_sorteddf_mallet,
                                                     grp.sort_values(['Perc_Contribution'], ascending=[0]).head(1)],
                                                    axis=0)

        # Reset Index
        sent_topics_sorteddf_mallet.reset_index(drop=True, inplace=True)

        # Format
        sent_topics_sorteddf_mallet.columns = ['Topic_Num', "Topic_Perc_Contrib", "Keywords", "Text"]

        # Show
        print(sent_topics_sorteddf_mallet.head())

    all_topics = get_topics(ldamodel=ldamodel_all, num_words=10)
    for i, topic in enumerate(all_topics):
        print(i, topic)


main(sys.argv[1:])
