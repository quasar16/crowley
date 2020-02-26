# crowley
Crawler for news regarding Quantum physics and Quantum computation

Usage: crowley date output_file

It uses newsapi to get URLs of articles about quantum computing and quantum physics to get the latest articles.
It uses news-please to get the content of the URLs and then it uses LDA to create topics of the articles.

After getting the articles is uses LDA topic modeling to get the most important topics and based 
on them selects the most relevant articles.
