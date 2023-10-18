import requests
from bs4 import BeautifulSoup



URL = "https://realpython.github.io/fake-jobs/"
print("Fetching your shit from: " + URL)
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")
print(soup.prettify())