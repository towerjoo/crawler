#coding: utf-8
from bs4 import BeautifulSoup as BS
from config import default_config


class Handler:
    def __init__(self):
        self.key = "UNKNOWN"

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
    def __init__(self):
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
    def __init__(self):
        self.key = "meta"

    def handle_resp(self, orig_cont, rq):
        soup = BS(orig_cont)
        ret = {
            "title" : soup.title.string,
            "title-length" : len(soup.title.string),
            "meta" : soup.meta,
        }
        return ret
        
class Crawler:
    def __init__(self, url=None, config=default_config):
        self.url = url
        self.config = default_config

    def request(self):
        import urllib2
        rq = urllib2.urlopen(self.url)
        cont = rq.read()
        rq.close()
        return self.handle_response(cont, rq)

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
    
