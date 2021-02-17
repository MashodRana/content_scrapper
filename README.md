# content_scrapper
This is an scrapping project. Scrappe content from any webpage.

## Features
- scrape titles/headlines with their url of an webpage.
- scrape article and few information about that article from provided webpage url.
- scrape google search result corresponding to a query.
- scrape google search result urls corresponding to a query.

## How build
I used 

[**googlesearch-python**](https://pypi.org/project/googlesearch-python/) for google searching and scrapping

[**newspaper3k**](https://pypi.org/project/newspaper3k/) for scrapping article information of an specific webpage.

But scrapping **titles/headlines** resource was not so much developed. Thats why I developed that part with [**BeautifulSoap**](https://pypi.org/project/beautifulsoup4/).
And you can scrape titles/headlines from any webpage not just only from newspaper.

## How to use
My pyhon version was `python==3.6.9`

First install the dependencies with the `requirements.txt.`

Switched to the content_scrapper directory and run the main.py file with the following command

    python main.py
    
you can go through the `main.py` file to understand how it works.

*Note*: may you can face problem with google search like `to many requests`. In future I will come with solution to this problem.

If you found any bug please raise issues. I will try my best to solve the issues.


                                      **Happy Coding**


