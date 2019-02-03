import requests
from bs4 import BeautifulSoup
#====================================================
class Search:
    API_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    BASE_URL = 'https://test-legalresearch.api.sal.sg'
    headers = {
        'x-api-key':API_KEY,
        'cache-control':'no-cache',
        "Content-Type": "application/x-www-form-urlencoded"
        }
    params = {
        'apikey':API_KEY,
        'cats':'r1',
        'l2cats':'r1c1',
        'maxperpage': 50
    }
        
    def __init__(self, cat):
        self.params['l3cats'] = cat

    def get_params(self):
        return self.params

    def make_search(self, searchTerm, maxperpage = 20):
        fullURL = self.BASE_URL + '/v1-search/search'
        self.params['searchTerm'] = searchTerm
        self.params['maxperpage'] = maxperpage
        r = requests.post(
            fullURL, 
            headers=self.headers,
            params = self.params
        )
        return r.text

    def get_document(self, docUrl):
        fullURL = self.BASE_URL + '/v1-content/content'
        self.params['docUrl'] = docUrl
        r = requests.post(
            fullURL,
            headers = self.headers,
            params = self.params
        )
        return r.text