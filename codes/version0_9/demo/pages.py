'''
Created on 29 Jul 2014

@author: 42601487
'''
def main():
    with open('main.html', 'r') as p:
        output = p.read()
    return output

def generate_result(result):
    template = """
    <div>
        <label><a href="">#document</a></label>
        <ul>
            #offsets
        </ul>
    </div>"""
    document = result[0]
    offsets = result[1]
    template = template.replace("#document", document)
    list = ""
    for offset in offsets:
        list = list + "<li>" + str(offset) + "</li>\n"
    template = template.replace("#offsets", list)
    return template
        
        