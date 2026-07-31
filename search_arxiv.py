import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

def search_arxiv(query):
    url = 'http://export.arxiv.org/api/query?search_query=' + urllib.parse.quote(query) + '&start=0&max_results=3'
    response = urllib.request.urlopen(url)
    xml_data = response.read()
    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    res = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.replace('\n', ' ')
        authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
        published = entry.find('atom:published', ns).text
        link = entry.find('atom:id', ns).text
        pdf_link = link.replace('abs', 'pdf') + '.pdf'
        res.append(f'Title: {title}\nAuthors: {authors}\nYear: {published[:4]}\nLink: {link}\nPDF: {pdf_link}')
    return '\n\n'.join(res)

output = ""
output += '--- Draper ---\n'
output += search_arxiv('all:"Addition on a Quantum Computer"')

output += '\n\n--- Vedral ---\n'
output += search_arxiv('all:"Quantum Networks for Elementary Arithmetic Operations"')

output += '\n\n--- Division ---\n'
output += search_arxiv('all:"restoring division algorithm" AND all:"quantum"')

with open('arxiv_results.txt', 'w', encoding='utf-8') as f:
    f.write(output)
