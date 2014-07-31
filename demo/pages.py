'''
Created on 29 Jul 2014

@author: 42601487
'''
import pyalveo

def main(client):
    with open('main.html', 'r') as p:
        output = p.read()
    lists = get_lists(client)
    output = output.replace("#lists", lists)
    return output

def generate_result(result):
    template = """
    <div>
        <label><a href="">#document</a></label>
        <ul>
            #offsets
        </ul>
    </div>"""
    document = str(result[0])
    offsets = result[1]
    template = template.replace("#document", document)
    list = ""
    for offset in offsets:
        list = list + "<li>" + str(offset) + "</li>\n"
    template = template.replace("#offsets", list)
    return template
        
def get_lists(client):
    ownerships = client.get_item_lists()
    all_servers = []
    pattern = """
    <div id="listNames">
        <ul>
            #itemLists
        </ul>
    </div>
    """
    lists = ""
    for ownership in ownerships:
        for server in ownerships[ownership]:
            all_servers.append(server)
    for server in all_servers:
        item_list_url = server['item_list_url']
        item_list = client.get_item_list(item_list_url)
        list = "<li><a class='list'>%s</a></li>\n" %(str(item_list.name()))
        lists = lists + list
    pattern = pattern.replace("#itemLists", lists)
    return pattern
            
            
            