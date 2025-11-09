from bs4 import BeautifulSoup

def parse_html_code(content):
    soup = BeautifulSoup(content, "html.parser")
    scripts = [s.get("src") for s in soup.find_all("script") if s.get("src")]
    styles = [l.get("href") for l in soup.find_all("link") if l.get("rel") == ["stylesheet"]]
    return {"scripts": scripts, "styles": styles}
