import web

urls = (
    '/', 'index'
)

class index:
    def GET(self):
        out = '''<form action="." method="POST">
        URL: <input type="text" name="url" value="http://www.google.com" />
        <input type="submit" value="Crawl!" />
        '''
        web.header('Content-Type', 'text/html')
        return out

    def POST(self):
        url = web.input().get("url")
        from crawler import Crawler
        c = Crawler(url)
        back_btn = "<a href='/'>Back</a></br>"
        resp = c.request()
        resp = back_btn + str(resp)
        web.header('Content-Type', 'text/html')
        return resp
        

        

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
