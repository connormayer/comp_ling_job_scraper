from bs4 import BeautifulSoup
from urlparse import urljoin
import requests

KEYWORDS = [
    "computational linguistics",
    "natural language processing",
    "nlp",
    "natural language",   
]

BASE_INDEED_URL = "http://ca.indeed.com/jobs?q={}"


class Scraper():
    """
    Base class for job scrapers.
    """
    _visited_urls = []
    _unvisited_urls = []
    _keyword_counts = {}
    _name = ""

    def get_name(self):
        return self._name

    def write_results(self):
        raise NotImplementedError

    def format_search_url(self, keyword):
        raise NotImplementedError

    def scrape(self):
        for keyword in KEYWORDS:
            url = self.format_search_url(keyword)
            response = requests.get(url, verify=False)
            self.parse_search_result(url, response.text)
            while len(self._unvisited_urls) > 0:
                job_url = self._unvisited_urls.pop(0)
                job_response = requests.get(job_url, verify=False)
                self.parse_result(job_response.text)
                self._visited_urls.append(job_url)


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
        # TODO
        pass


if __name__ == "__main__":
    scrapers = [
        IndeedScraper()
    ]
    for scraper in scrapers:
        scraper.scrape()
