from bottle import route, run, error, get, post, request, response
import templates
from alveo_redis_query import _client, Crawler, _redis_cli, QueryProcessor
import json
import cgi

"""@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)"""

@route('/')
def home_page():
    return templates.generate_home_page()

@get('/search')
def query_result():
    query = request.GET['query']
    results = QueryProcessor.process_query(query)
    page = ""
    for result in results:
        content = templates.generate_query_results(result)
        page = page + content
    return page

@route('/static/<path:path>')
def static_file(path):
    return templates.get_static_file(path)

@route('/update')
def update_index():
    form = cgi.FieldStorage(fp=request.environ['wsgi.input'], environ=request.environ)
    if form.has_key('list'):
        itemlistName = form.getvalue("list", "")
        result = []
        item_list = _client.get_item_list_by_name(itemlistName, "shared")
        message = Crawler.crawl(item_list)
        if message:
            result.append(False)
            result.append(message)
        else:
            result.append(True)
            result.append('')
        response.content_type = 'application/json'
        return json.dumps(result)

@error(404)
def error404(error):
    return 'Nothing here, sorry'


if __name__ == '__main__':
    _redis_cli.flushall()
    run(host='localhost', port=8080)