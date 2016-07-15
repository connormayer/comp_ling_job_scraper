from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.tokenize import word_tokenize, sent_tokenize
from urlparse import urljoin
import nltk
import requests

SEARCH_KEYWORDS = [
    "computational linguistics",
    "natural language processing",
    "nlp",
    "natural language",
]

KEYWORDS = SEARCH_KEYWORDS + [
    "machine learning",
    "data mining",
    "python",
    "java",
    "math",
    "mysql",
    "sql",
    "c++",
    # "r", took this out because of a lot of occurrences in french text
    "hadoop",
    "big data",
    "software engineering",
    "software engineer",
    "matlab",
    "sas",
    "data analysis",
    "optimization",
    "perl",
    "linux",
    "predictive models",
    "statistics",
    "hive",
    "software development",
    "physics",
    "mapreduce",
    "data management",
]

BASE_INDEED_URL = "http://ca.indeed.com/jobs?q={}&limit=100"
BASE_INDEED_USA_URL = "http://indeed.com/jobs?q={}&limit=100"
LINGUIST_LIST_URL = ("http://linguistlist.org/jobs/search-job2.cfm?rank=98"
                     "&rank=10&rank=241&rank=9&rank=8&rank=15&rank=16"
                     "&lingfield=7191&lingfield=7223&multipleword=Any"
                     "&openonly=Y&Submit=Search+Jobs")

KEYWORD_COUNTS = defaultdict(int)

# Utility functions
def find_substring(text, substring):
    for i in xrange(len(text)):
        if text[i] == substring[0] and text[i:i + len(substring)] == substring:
            return True
    return False

def print_keyword_results():
    print "Found the following keyword counts:"
    for (key, value) in KEYWORD_COUNTS.iteritems():
        print "{}: {}".format(key, value)

class Scraper():
    """
    Base class for job scrapers.
    """
    _visited_urls = []
    _unvisited_urls = []
    _name = ""
    _listing_count = 0

    def write_results(self):
        raise NotImplementedError

    def format_search_url(self, keyword):
        raise NotImplementedError

    def _print_results(self):
        print "{} found {} listings".format(
            self._name, self._listing_count
        )

    def scrape(self):
        for keyword in SEARCH_KEYWORDS:
            url = self.format_search_url(keyword)
            print "Getting results from {}".format(url)
            self.get_search_results(url)
            print "Found {} listings for {}".format(
                len(self._unvisited_urls), keyword
            )
            print "Parsing results",
            while len(self._unvisited_urls) > 0:
                print ".",
                job_url = self._unvisited_urls.pop(0)
                try:
                    job_response = requests.get(job_url, verify=False)
                except Exception as e:
                    print "\nError getting page at {}: {}".format(job_url, e.message)
                else:
                    self.parse_result(job_response.text)
                self._visited_urls.append(job_url)
            print
        self._print_results()


class IndeedScraper(Scraper):
    """
    Class to scrape job information from indeed.
    """
    _base_url = BASE_INDEED_URL
    _name = "indeed_scraper"

    def format_search_url(self, keyword):
        return self._base_url.format(
            "\"" + "+".join(keyword.split(" ")) + "\""
        )

    def get_search_results(self, url, depth=0):
        url_with_start = url + "&start={}".format(depth * 100)
        response = requests.get(url_with_start, verify=False)
        has_next = self.parse_search_result(url, response.text)
        if has_next:
            self.get_search_results(url, depth + 1)

    def parse_search_result(self, url, result):
        soup =  BeautifulSoup(result)
        results_col = soup.find("td", id="resultsCol")
        if results_col:
            filter_by = {'data-tn-element': 'jobTitle'}
            for link in results_col.find_all('a', href=True, **filter_by):
                full_url = urljoin(url, link['href'])
                if full_url not in self._visited_urls:
                    self._unvisited_urls.append(full_url)
        search_dict = {"class": "np"}
        navigation_buttons = soup.find_all("span", **search_dict)
        has_next = False
        for button in navigation_buttons:
            if "Next" in button.text:
                has_next = True
        return has_next

    def parse_result(self, result):
        self._listing_count += 1
        soup = BeautifulSoup(result)
        body = ' '.join(
            [p.get_text() for p in soup.find_all('p', text=True)]
        )
        # tokens = [
        #     word.lower() for sent in sent_tokenize(body)
        #     for word in word_tokenize(sent)
        # ]
        for keyword in KEYWORDS:
            # if find_substring(tokens, keyword.split(' ')):
            if keyword in body.lower():
                KEYWORD_COUNTS[keyword] += 1

class IndeedAmericaScraper(IndeedScraper):
    """
    Class to scrape job information from American Indeed
    """
    _base_url = BASE_INDEED_USA_URL
    _name = "indeed_america_scraper"

class LingListScraper(Scraper):
    pass


if __name__ == "__main__":
    scrapers = [
        IndeedScraper(),
        IndeedAmericaScraper()
    ]
    for scraper in scrapers:
        scraper.scrape()
    print_keyword_results()
