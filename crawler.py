#coding: utf-8
from bs4 import BeautifulSoup as BS
from config import default_config


class Handler(object):
    def __init__(self, config=default_config):
        self.key = "UNKNOWN"
        self.config = config

    def handle_resp(self, orig_cont, rq):
        """orig_cont is the content readed from urllib2
        rq is the urllib2.addinfourl instance after calling *close*
        """
        raise NotImplementedError()

    def __call__(self, func):
        def wrapper(inst, orig_cont, rq):
            added_cont = self.handle_resp(orig_cont, rq)
            resp = func(inst, orig_cont, rq)
            resp.update({self.key : added_cont})
            return resp
        return wrapper
            
class HeaderHandler(Handler):
    def __init__(self, config=default_config):
        super(HeaderHandler, self).__init__(config)
        self.key = "header"

    def handle_resp(self, orig_cont, rq):
        code = rq.code
        headers = rq.headers
        ret = {
            "status-code" : str(code),
        }
        ret.update(headers.dict)
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
        
class Crawler:
    def __init__(self, url=None):
        self.url = url

    def request(self):
        import urllib2
        rq = urllib2.urlopen(self.url)
        cont = rq.read()
        rq.close()
        return self.handle_response(cont, rq)

    @LinkHandler()
    @MetaHandler()
    @HeaderHandler()
    def handle_response(self, cont, rq):
        return {}

    def output(self, ret):
        import pprint
        pprint.pprint(ret, indent=4)


if __name__ == "__main__":
    url = "http://localhost:4000"
    crawler = Crawler(url)
    crawler.output(crawler.request())
    
