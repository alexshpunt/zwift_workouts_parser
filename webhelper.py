from bs4 import BeautifulSoup

def get_web_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Vivaldi/4.3',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
    }

    import ssl, certifi, urllib.request
    req = urllib.request.Request(url, headers=headers)
    context = ssl.create_default_context(cafile=certifi.where())
    response = urllib.request.urlopen(req, context=context)
    return response.read().decode('utf-8')

def get_filtered_web_content(url, tag, tag_class):
    content = get_web_content(url)

    soup = BeautifulSoup(content, features='html.parser')
    return soup.find_all(tag, class_ = tag_class)
