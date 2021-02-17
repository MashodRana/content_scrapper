from content_scrapper import ContentScrapper


if __name__ == '__main__':

    # Create object
    con_scrapper = ContentScrapper()

    # Scrape all headlines of prothom alo newspaper
    headlines = con_scrapper.get_titles("https://www.prothomalo.com/")
    print(headlines)

    # Scrape a specific article information
    article = con_scrapper.get_article_info("https://www.analyticsvidhya.com/blog/2018/04/a-comprehensive-guide-to-understand-and-implement-text-classification-in-python/")
    print(article)

    # Scrape first 5 urls from google search result corresponding a query
    con_scrapper.query = "latest news on corona virus"
    _5_urls = con_scrapper.get_google_search_url(limit=5)
    print(_5_urls)


    # # Scrape a artilce corresponding to a query from the google search
    con_scrapper.query = "latest news on corona virus"
    # query_result = con_scrapper.query_result()
    # print(query_result)


