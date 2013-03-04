#coding: utf-8
from bs4 import BeautifulSoup as BS
from config import default_config


class Handler(object):
    def __init__(self, config=default_config):
        self.key = "UNKNOWN"
        self.config = config
        self.supported_types = ["text/html"]

    def handle_resp(self, orig_cont, rq):
        """orig_cont is the content readed from urllib2
        rq is the urllib2.addinfourl instance after calling *close*
        """
        raise NotImplementedError()

    def can_handle(self, content_type):
        if "all" in self.supported_types:
            return True
        if content_type in self.supported_types:
            return True
        return False

    def __call__(self, func):
        def wrapper(inst, orig_cont, rq):
            headers = rq.headers
            resp = func(inst, orig_cont, rq)
            if not self.can_handle(headers.get("content-type")):
                return resp
            added_cont = self.handle_resp(orig_cont, rq)
            resp.update({self.key : added_cont})
            return resp
        return wrapper
            
class HeaderHandler(Handler):
    def __init__(self, config=default_config):
        super(HeaderHandler, self).__init__(config)
        self.key = "header"
        self.supported_types = ["all"]  # means support all

    def handle_resp(self, orig_cont, rq):
        code = rq.code
        headers = rq.headers
        ret = {
            "status-code" : str(code),
        }
        for k in self.config.get('interests').get('header'):
            ret.update({ k : headers.dict.get(k)})
        return ret

class MetaHandler(Handler):
    def __init__(self, config=default_config):
        super(MetaHandler, self).__init__(config)
        self.key = "meta"

    def parse_meta(self, soup):
        metas_interests = self.config.get("interests").get("meta")
        metas = soup.find_all("meta")
        ret = {}
        for m in metas:
            if "charset" in metas_interests and m.get('charset'):
                ret.update({"charset" : m.get("charset")})
            if m.name.lower() in metas_interests:
                ret.update({m.name.lower() : m.content})
        return ret

    def handle_resp(self, orig_cont, rq):
        soup = BS(orig_cont)
        ret = {
            "word-count" : len(soup.get_text().split(" ")), # not precise, can be refined later
            "title" : soup.title.string,
            "title-length" : len(soup.title.string),
        }
        ret.update(self.parse_meta(soup))
        return ret

class LinkHandler(Handler):
    def __init__(self, config=default_config):
        super(LinkHandler, self).__init__(config)
        self.key = "link"

    def parse_links(self, soup):
        links = soup.find_all("a")
        ret = []
        for link in links:
            ret.append({"title" : link.string, "url" : link.get("href")})
        return ret

    def handle_resp(self, orig_cont, rq):
        soup = BS(orig_cont)
        ret = {
            "links" : self.parse_links(soup),
        }
        return ret

class TitleHandler(Handler):
    def __init__(self, config=default_config):
        super(TitleHandler, self).__init__(config)
        self.key = "title"

    def parse_titles(self, soup, tag="h1"):
        titles = soup.find_all(tag)
        ret = []
        for t in titles:
            ret.append(t.string)
        return ret

    def handle_resp(self, orig_cont, rq):
        soup = BS(orig_cont)
        titles_interests = self.config.get('interests').get('title')
        for t in titles_interests:
            ret = {
                t : self.parse_titles(soup, t),
            }
        return ret
        
        
class Crawler:
    def __init__(self, url=None):
        self.url = url

    def request(self):
        import urllib2
        rq = urllib2.urlopen(self.url)
        cont = rq.read()
        rq.close()
        return self.handle_response(cont, rq)

    @TitleHandler()
    @LinkHandler()
    @MetaHandler()
    @HeaderHandler()
    def handle_response(self, cont, rq):
        return {}

    def output(self, ret):
        import pprint
        pprint.pprint(ret, indent=4)


if __name__ == "__main__":
    import sys
    url = "http://localhost:4000"
    if len(sys.argv) == 2:
        url = sys.argv[1]
    crawler = Crawler(url)
    crawler.output(crawler.request())
    
