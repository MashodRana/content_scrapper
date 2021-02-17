import os
import json
from googlesearch import search
from scraper import TitleScraper, ArticleScrapper


class ContentScrapper:
    def __init__(self, query=None):
        self.query = query
        self.limit = 5

    def get_google_search_url(self, limit=5):
        """
            Extract the  URLs which provide the google search result corresponding to the query.
        :param:
            limit: int type.
            how many URLs will be pick from google search result.
        :return: a list.
         Contains extracted urls from google search result.
         """
        print(self.query)
        print('-'*150)
        results = search(self.query, num_results=limit)
        urls = [url for url in results]
        return urls

    def query_result(self):
        """
            extract a specific content details from the URLs
        :return:
        """

        # getting URLs from the google based on query
        urls = self.get_google_search_url(self.query)

        art_scr = ArticleScrapper(urls)  # creating a object with the URLs

        articles_info = []
        flag = False

        # visit all the URLs till to find the specific content article
        for url in art_scr.article_urls:
            article_info = art_scr.get_article_info(url)
            if article_info and article_info['is_valid']:
                flag = True
                break
            else:
                articles_info.append(article_info)
                print('Going to next url....')

        if flag:
            return article_info
        else:
            # Return the article_info which has maximum length
            news = ""
            article_info = None
            for art in articles_info:
                text = ' '.join([art['headline'], art['text']])
                if len(news) < len(text):
                    news = text
                    article_info = art
            return article_info

    @staticmethod
    def get_article_info(url, summary=False):
        """
            This method download the article html file, then parse it. extract the information about the
            article (headline, author, publish_date, summary)
        :param:
            url: str type.
            url of the web page for the article
        :return: a dictionary.
            Contains (keys: headline, author, published_date, text, summary) if article has a valid
            html body. Either return None.
        """
        info = ArticleScrapper.get_article_info(article_url=url, is_summary=summary)
        return info

    def get_titles(self, url):
        """
            this method extract the headlines/title and href of contents from a web-page.
        :param:
            url: str type.
            URL of the web-page which content information will be extracted.
        :return: a dictionary.
            Contains source url and titles (key:href, value:headline)
        """
        # create the object by providing the web-page URL
        scrapper_obj = TitleScraper(url=url)

        # pre-processing the web-page data
        scrapper_obj.pre_processing()

        # extracting all contents which is bound to <a> tag and <a> tag must have attribute 'href'
        scrapper_obj.extract_content_blocks(a_tags=scrapper_obj.a_tags)

        # filtering content block to remove unnecessary content
        filtered_block = [block for block in scrapper_obj.content_blocks if scrapper_obj.extreme_filter(block)]

        # remove content which has same href
        filtered_block.reverse()  # reverse the filtered content to keep latest content in the as value in the dict
        titles = {}
        for block in filtered_block:
            href, data = block
            dat = data[0]
            if len(data) > 1:
                for d in data:
                    if len(d) > len(dat):
                        dat = d
            titles[href] = dat  # keep length text as headline/title

        # keeping latest content in the top of the dict
        hrefs = list(titles.keys())
        hrefs.reverse()

        final_blocks = {}
        for href in hrefs:
            if scrapper_obj.root not in href:
                final_blocks[scrapper_obj.root_left + scrapper_obj.root + href] = titles[href]

        # return the headlines/titles with their href
        # return final_blocks
        return {
            'source_url': scrapper_obj.page_url,
            'titles': final_blocks
        }
