import requests
from bs4 import BeautifulSoup

url = 'https://www.osti.gov/biblio/4645943'

r = requests.get(url)
c1 = r.cookies['BIGipServerlbapp_tc3']
c2 = r.cookies['BIGipServerwww.osti.gov_pool']
c3 = r.cookies['JSESSIONID']
soup = BeautifulSoup(r.text, "html.parser")
print(soup)
pdf_url = soup.find("meta", {"name": "citation_pdf_url"})["content"]
print(c1,c2,c3)
cookies = {
    'BIGipServerlbapp_tc3': c1,
    'BIGipServerwww.osti.gov_pool':c2,
    'JSESSIONID':c3,
    '__utma': '249692800.1749221367.1564467097.1564467097.1564467097.1',
    '__utmc': '249692800',
    '__utmz': '249692800.1564467097.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
    '_ga': 'GA1.2.1749221367.1564467097',
    '_gid': 'GA1.2.298248318.1564467099',
    '__utmt': '1',
    '__utmb': '249692800.63.10.1564467097'
}

r2 = requests.get(pdf_url, cookies=cookies)
with open('pppppp.pdf', 'wb') as f:
    f.write(r2.content)
