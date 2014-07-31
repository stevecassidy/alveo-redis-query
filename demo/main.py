'''
Created on 29 Jul 2014

@author: 42601487
'''
from wsgiref import simple_server
import cgi
import pages
import os
import json
import redis
import alveo_redis_query as alveo

STATIC_URL_PREFIX = "/static/"
STATIC_FILE_DIR = os.path.dirname(__file__)
MIME_TABLE = {'.txt': 'text/plain',
              '.html': 'text/html',
              '.css': 'text/css',
              '.js': 'application/javascript',
              '.png': 'image/png'
             } 

def main_page(params, environ, start_response):
    headers = [('Content-Type', 'text/html')]
    start_response('200 OK', headers)
    
    page = pages.main(params['client'])
    
    return page

def no_page(params, environ, start_response):
    headers = [('Content-Type', 'text/html')]
    start_response('404 NOT FOUND', headers)
    return "There is no such page on this server"

def content_type(path):
    name, ext = os.path.splitext(path)
    
    if MIME_TABLE.has_key(ext):
        return MIME_TABLE[ext]
    else:
        return "application/octet-stream"

def static_file(params, environ, start_response):
    path = environ['PATH_INFO']
    path = os.path.normpath(path)
    if path.startswith("\\static\\"):
        path = environ['PATH_INFO']
        path = path.replace(STATIC_URL_PREFIX, "static/")
        path = os.path.join(STATIC_FILE_DIR, path)
        if os.path.exists(path):
            h = open(path, 'rb')
            content = h.read()
            h.close()
            
            headers = [('content-type', content_type(path))]
            start_response('200 OK', headers)
            return content 
        else:
            return no_page(params, environ, start_response)

def query_result(params, environ, start_response):
    headers = [('Content-Type', 'text/html')]
    start_response('200 OK', headers)
    page = ""
    results = params['result']
    for result in results:
        content = pages.generate_result(result)
        page = page + content
    return page

def update_index(params, environ, start_response):
    headers = [('content-type', 'application/json')]
    start_response("200 OK", headers)
    
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    client = params['client']
    result = []
    
    if form.has_key('list'):
        list_name = form.getvalue("list", "")
        item_list = client.get_item_list_by_name(list_name, "shared")
        message = alveo.Crawler.crawl(item_list)
        if message:
            result.append(False)
            result.append(message)
        else:
            result.append(True)
            result.append('')
    
    return json.dumps(result)
    
def application(environ, start_response):
    app = ""
    params = {}
    
    client = alveo.ClientFactory.get_client()
    params.setdefault("client", client)
    
    formdata = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
    
    if environ["PATH_INFO"] == "/":
        app = main_page
    elif environ["PATH_INFO"].startswith("/static"):
        app = static_file
    elif environ["PATH_INFO"].startswith("/update"):
        app = update_index
    elif environ["PATH_INFO"].startswith("/search"):
        if formdata.has_key("query"):
            query = formdata.getvalue("query")
            result = alveo.QueryProcessor.process_query(query)
            params.setdefault("result", result)
            app = query_result
        else:
            app = no_page
    else:
        app = no_page
    return app(params, environ, start_response)



if __name__ == '__main__':

    redis_cli = redis.StrictRedis(host='localhost', port=6379, db=0)
    redis_cli.flushall()

    host = 'localhost'
    port = 8000
    
    server = simple_server.make_server(host, port, application)
    print "Listening on http://%s:%d/" % (host, port)
    server.serve_forever()