from bottle import route, run, error, get, request, response
import templates
from alveo_redis_query import AlveoIndex


@route('/')
def home_page():
    response.set_cookie("apikey", "place-your-apikey-here")
    return templates.generate_home_page()

@get('/search')
def query_result():
    apikey = request.get_cookie("apikey")
    index = AlveoIndex(apikey)
    query = request.GET['query']
    results = index.execute_query(query)
    if results:
        textResults = index._get_text_for_results(results, (-20, 80), True)
        page = """
        <div>
        <link rel="stylesheet" type="text/css" href="/static/css/doc_view.css" />"""
        for doc in textResults.keys():
            textList = textResults[doc]
            content = templates.generate_query_results(doc, textList)
            page = page + content
        page += """
        </div>
        """
        return page

@route('/static/<path:path>')
def static_file(path):
    return templates.get_static_file(path)

@error(404)
def error404(error):
    return 'Nothing here, sorry'


if __name__ == '__main__':
    run(host='localhost', port=8080)