import requests
from bs4 import BeautifulSoup


class EbayItem:
    """Class ebay item"""
    def __init__(self, contents):
        contents = [con for con in contents if con != "\n"]
        self.link = "https://www.ebay-kleinanzeigen.de" + contents[0].a['href']
        self.title = contents[0].a.text
        self.price = contents[0].strong.text
        self.id = contents[0]['data-adid']
        self.description = contents[0].p.text.replace("\n", " ")
        details = self.getDetails(contents[0])
        self.distance = details["distance"]
        self.city = details["city"]

    def __repr__(self):
        return '{}; {}; {}'.format(self.title, self.city, self.distance)

    def getDetails(self, content):
        details = content.find_all("div", {'class': "aditem-details"})[0].text.split("\n")
        details = [det.strip() for det in details]
        return {"distance": details[-1], "city": details[-2]}


def getPost(link):
    session = requests.Session()
    customHeader = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0"}
    response = session.get('{}'.format(link),
                           headers=customHeader)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all(attrs={"class": "ad-listitem lazyload-item"})
        items = [EbayItem(item) for item in articles]
        return items
    else:
        return None


if __name__ =="__main__":
    getPost("https://www.ebay-kleinanzeigen.de/s-weener/preis::250/lenovo/k0l2744r20")