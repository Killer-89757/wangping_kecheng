import requests


class Download:
    def __init__(self):
        pass

    def download(self, url):
        response = requests.get(url)
        print(response)
