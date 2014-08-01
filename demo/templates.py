from bottle import template, static_file
from alveo_redis_query import _client

def generate_home_page():
    with open('static/templates/main.html', 'r') as file_content:
        content = file_content.read()
    lists = _generate_item_lists()
    content = content.replace("#lists", lists)
    return content

def generate_query_results(result):
    with open('static/templates/doc_view.html', 'r') as file_content:
        content = file_content.read()
    document = str(result[0])
    text = str(result[1])
    offsets = result[2]
    content = content.replace("#url", document)
    temp = ""
    for offset in offsets:
        temp = temp + "<li>" + text[offset[0]-30:offset[0]] + '<mark>' + text[offset[0]:offset[1]] + '</mark>' + text[offset[1]:offset[1]+50] + "</li>\n"
    content = content.replace("#text", temp)
    return content

def get_static_file(path):
    return static_file(path, root='./static')

def _generate_item_lists():
    ownerships = _client.get_item_lists()
    all_servers = []
    with open('static/templates/itemlists.html', 'r') as f:
        itemlists = f.read()
    with open('static/templates/itemlist.html', 'r') as f:
        itemlist = f.read()
    lists = ""
    for ownership in ownerships:
        for server in ownerships[ownership]:
            all_servers.append(server)
    for server in all_servers:
        item_list_url = server['item_list_url']
        item_list = _client.get_item_list(item_list_url)
        result = itemlist.replace("#itemlist", str(item_list.name()))
        lists = lists + result
    itemlists = itemlists.replace("#itemLists", lists)
    return itemlists