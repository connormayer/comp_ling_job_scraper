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

BASE_INDEED_URL = "http://ca.indeed.com/jobs?q={}"


class Scraper():
    """
    Base class for job scrapers.
    """
    _visited_urls = []
    _unvisited_urls = []
    _keyword_counts = defaultdict(int)
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
        print "Found the following keyword counts:"
        for (key, value) in self._keyword_counts.iteritems():
            print "{}: {}".format(key, value)

    def scrape(self):
        for keyword in SEARCH_KEYWORDS:
            url = self.format_search_url(keyword)
            response = requests.get(url, verify=False)
            self.parse_search_result(url, response.text)
            while len(self._unvisited_urls) > 0:
                job_url = self._unvisited_urls.pop(0)
                try:
                    job_response = requests.get(job_url, verify=False)
                    self.parse_result(job_response.text)
                    self._visited_urls.append(job_url)
                except Exception as e:
                    print "Error getting page at {}: {}".format(job_url, e.message)
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

    def parse_search_result(self, url, result):
        soup =  BeautifulSoup(result)
        results_col = soup.find("td", id="resultsCol")
        if results_col:
            filter_by = {'data-tn-element': 'jobTitle'}
            for link in results_col.find_all('a', href=True, **filter_by):
                full_url = urljoin(url, link['href'])
                if full_url not in self._visited_urls:
                    self._unvisited_urls.append(full_url)

    def parse_result(self, result):
        self._listing_count += 1
        soup = BeautifulSoup(result)
        body = ' '.join(
            [p.get_text() for p in soup.find_all('p', text=True)]
        )
        tokens = [
            word.lower() for sent in sent_tokenize(body)
            for word in word_tokenize(sent)
        ]
        for keyword in KEYWORDS:
            if self.find_substring(tokens, keyword.split(' ')):
                self._keyword_counts[keyword] += 1

    def find_substring(self, text, substring):
        for i in xrange(len(text)):
            if text[i] == substring[0] and text[i:i + len(substring)] == substring:
                return True
        return False

if __name__ == "__main__":
    scrapers = [
        IndeedScraper()
    ]
    for scraper in scrapers:
        scraper.scrape()
