import os
import json
import re
import requests
from bs4 import BeautifulSoup
from tldextract import extract as domain_extract
from tqdm import tqdm
import newspaper as NewsPaper


class TitleScraper:
    """
        This class scrape the web page and  extract the content properties like: content title, summary, url
    """

    def __init__(self, url):
        """
            create the an instance of HeadlineScraper by initializing the necessary variables and methods
        :param url: the web page URL on which scrapping will be done
        """
        self.titles = None
        self.authors = None
        self.summaries = None
        self.published_dates = None

        self.page_url = url  # target web page URL

        # get the root url from the page url
        self.root = '.'.join(domain_extract(self.page_url))

        # get the right and left side of the root url
        self.root_right = self.page_url.split(self.root)[1]
        self.root_left = "https://"

        # url keywords
        self.url_keywords = [w for w in re.split('\W', self.root_right) if w]

        self.raw_page = None  # html page into text format
        self.parsed_page = None  # parsed with BeautifulSoup
        self.a_tags = None  # all selective anchor tag '<a>'

        # contents
        self.content_block = []  # used store a single content data
        self.content_blocks = []  # store all contents data

        # get the web page content
        self.__get_contents()

    def __get_contents(self):
        """
            This method is used to get the web-page content by downloading with get request
        :return: void
        """

        # Raise an error if failed to download the web-page content
        try:
            req = requests.get(self.page_url)  # requesting and downloading
            self.raw_page = req.text  # content into text format
        except Exception as E:
            print('Failed to obtain the content from the source. And cause is: %s' % E)

    def pre_processing(self):
        """
            This method is used to create an parsed object with the BeautifulSoup.
        :return:
        """

        # parsed the text formatted web-page content with HTML parser
        try:
            self.parsed_page = BeautifulSoup(self.raw_page, 'html.parser')
        except Exception as E:
            print(E)
            return

        # Remove tag <script> and <noscript> which has no anchor tag <a>
        scripts = self.parsed_page.find_all('script')
        for script in scripts:
            if not script.find('a'):
                script.decompose()

        noscripts = self.parsed_page.find_all('noscript')
        for noscript in noscripts:
            if not noscript.find('a'):
                noscript.decompose()

        # Obtain all the anchor tag '<a>'
        a_tags = self.parsed_page.find_all('a')
        self.a_tags = [t for t in a_tags if t.get('href')]  # remove tag <a> which has no 'href'

    @staticmethod
    def text_cleaning(text):
        """
            This method is used to clean the unnecessary space, new line, tab
        :param text: string type
        :return: clean text into string type
        """
        text = re.sub('\n+|\t+', ' ', text)  # replace unnecessary tabs and newline with space
        text = re.sub(' +', ' ', text).strip()  # replace more than one space with single space
        return text

    def get_tag_text(self, tag):
        """
            This method is used to obtain the text of a tag and its children.
            Also remove the tag from the parsed tree after obtain the text.
        :param tag: a tag from the parsed tree
        :return: void
        """

        # if tag is not NoneType
        if tag.name:
            childs = tag.content  # get the children

            # if there are children
            if childs:
                for child in childs:
                    if child.name: self.get_tag_text(child)  # if child is not NoneType go for to get the text

            # get the text of the tag
            tag_text = tag.get_text()
            if tag_text:
                self.content_block.append(
                    self.text_cleaning(tag_text))  # add the text of the tag if tag text is not empty

            # remove the tag from the parsed tree
            tag.decompose()

    def process_siblings(self, tag):
        """
            This method is used to to visit the next siblings to find the necessary content if we failed to obtain
            content from the target tag
        :param tag: a tag from the parsed tree
        :return: void
        """
        siblings = []
        sibling = tag

        # find all sibling of tag untill a anchor tag '<a>' is discovered
        while (sibling.next_sibling):
            sibling = sibling.next_sibling
            if not sibling.name:
                continue
            if sibling.name == 'a' or sibling.find('a'):
                break
            siblings.append(sibling)

        # Obtain the textual content of the siblings
        for sibling in siblings:
            # print("processing Parent child.....")
            self.get_tag_text(sibling)

    def extract_content_blocks(self, a_tags):
        """
            This method is used to obtain and store the contents for every anchor tag '<a>'.
            And also remove the tag from the parsed tree after obtaining the content
        :param a_tags: a list of anchor tag '<a>'
        :return: void
        """

        # used to store all content
        self.content_blocks = []

        print('Extracting contents................')
        for i, tag in enumerate(tqdm(a_tags)):
            # used to store a content
            self.content_block = []

            # Obtain the text and children of tag <a>
            if not tag.name:
                continue  # if tag is NoneType go to next tag

            tag_text = tag.get_text()  # textual content
            href = tag.get('href')  # URL of the content
            childs = tag.content  # children of tag
            parent = tag.parent  # parent of tag

            if not tag_text:
                """
                if tag has no textual content that means it has not child which should we visit. So go to tag
                siblings and searching for textual content.
                If number of element in the content is more than three stire the content element with url.
                If number of element in the content is not more than three go through the siblings of the parent
                and search for textual element to store.
                """
                # print("Case-1\n--------------------------")
                self.process_siblings(tag)  # go through tag siblings
                if len(self.content_block) > 3:
                    self.content_blocks.append((href, self.content_block))  # store content
                else:
                    # print("2.2:Process Grand Parents\n--------------------")
                    self.process_siblings(parent)  # go through tag parent siblings
                    self.content_blocks.append((href, self.content_block))  # store content
                # count_twt += 1
            elif tag_text and not childs:
                # print("Case-2\n--------------------------")
                self.content_block.append(self.text_cleaning(tag_text))
                # need parents to get other contents
                # print("Second Case:\n___________________")
                self.process_siblings(tag)
                if len(self.content_block) > 3:
                    self.content_blocks.append((href, self.content_block))
                else:
                    # need to be checked that is author is found or not
                    # print("2.2:Process Grand Parents\n--------------------")
                    self.process_siblings(parent)
                    self.content_blocks.append((href, self.content_block))
            elif tag_text and childs:
                # print("Case-3\n--------------------------")
                for child in childs:
                    self.get_tag_text(child)
                if len(self.content_block) > 3:
                    # process to stroe as expected content and remove the tag <a>
                    self.content_blocks.append((href, self.content_block))
                else:
                    # get parent and work with him
                    self.process_siblings(tag)

                    if len(self.content_block) > 3:
                        self.content_blocks.append((href, self.content_block))
                    else:
                        # grand parent
                        response = self.process_siblings(parent)
                        self.content_blocks.append((href, self.content_block))
            tag.decompose()
        # Remove duplicate and empty tag text from each of the headline_block
        self.content_blocks = [(href, [d for i, d in enumerate(block) if d and d not in block[i + 1:]]) for href, block
                               in self.content_blocks]

    @staticmethod
    def letter_count(string):
        string = string.lower()
        count = 0
        for s in string:
            if s.isalpha():
                count += 1
        return count

    @staticmethod
    def extreme_filter(block):
        """ It will filter the title extremely. A valid title would be through out. """
        if not block[1]:
            return False
        if len(block[1]) > 1:
            return True

        # if a title contains less than 4 words will not be considered as a title.
        return False if len(block[1][0].split(' ')) < 4 else True

    def hard_filter(self, block):
        href, data = block

        if not block[1]:
            return False
        if len(data) > 1:
            return True

        sentence = data[0].lower()
        split = re.split(self.root_url, href)
        href_right = split[1] if len(split) == 2 else split[0]
        words_href = re.split('/', href_right)
        part_1 = words_href[-1] if words_href[-1] != '' else words_href[-2]
        part_1 = re.sub('[^a-zA-Z]', '', part_1.lower())
        sentence = re.sub('[^a-zA-Z]', '', sentence)
        #     print(part_1)
        #     print(sentence)
        if part_1 == sentence:
            return False
        else:
            return True

    def soft_filter(self, block):
        href, data = block
        if len(data) > 1:
            return True
        sentence = data[0]
        split = re.split(self.root_url, href)
        href_right = split[1] if len(split) == 2 else split[0]
        count_href = self.letter_count(href_right)
        count_sent = self.letter_count(sentence)
        try:
            if (count_href / count_sent) - (count_sent / count_href) < 0.3:
                return False
            else:
                return True
        except ZeroDivisionError:
            return False


class ArticleScrapper:
    """
        This class is able to extract article information from the web page. It has method which handle
        multiple webapages. It store the each article information. We get article headline, author,
        published_date, text and summary.
        Note:: We used the "newspaper" package for this part.
    """

    def __init__(self, article_urls, extract_info=False):
        """
            Initialize the necessary variables and call the necessary method to extract article information
            from the provided urls
        :param article_urls: list of urls of article from where information will be gathered
        :param extract_info: true or false; for true extract the each article information and stored
                            into a list.
        """
        print("I am initilizing..... the GettingNews class")
        self.article_urls = article_urls
        self.fake_urls = []
        # get the extracted information and store it
        if extract_info:
            self.all_article_info, self.fake_urls = self.get_articles_info(self.article_urls)

    def get_articles_info(self, article_urls):
        """
        this method extract the information of the article from each article url
        :param self:
        :param article_urls: list of urls of article web page
        :return:
        """
        articles_info = []
        fake_article = []
        # get the extracted article information for per article url
        print('Processing articel urls.....')
        for url in article_urls:
            info = self.get_article_info(url)
            if info:
                articles_info.append(info)
            else:
                fake_article.append(url)
        return articles_info, fake_article

    @staticmethod
    def get_article_info(article_url, is_summary=False):
        """
            This method download the article html file, then parse it. extract the information about the
            article (headline, author, publish_date, summary)
        :param article_url: url of the web page for the article
        :return: a dictionary (keys: headline, author, published_date, text, summary) if article has a valid
                html body. Either return None
        """

        try:
            article = NewsPaper.Article(article_url)
            article.download()  # download the article into html format
            article.parse()  # parse the html format
        except Exception:
            return None

        info = {}

        # put source URL
        info['source_url'] = article_url

        # check this is an article or just a page of collection of articles
        info['is_valid'] = True if article.is_valid_body() else False

        # extract the information of the article
        try:
            info['headline'] = article.title
            info['author'] = article.authors
            info['published_date'] = article.publish_date
            info['text'] = article.text
            if is_summary:
                article.nlp()
                info['summary'] = article.summary
        except KeyError as KE:
            print(KE)
        # print(info)
        return info

    def process_fake_url(self, url):
        """

        :param url:
        :return:
        """
        paper = NewsPaper.build(url, memoize_articles=False)
        article_urls = paper.article_urls()
        articles_info, fake_urls = self.get_articles_info(article_urls)
        return articles_info, fake_urls
