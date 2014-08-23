from bottle import static_file

def generate_home_page():
    with open('static/templates/main.html', 'r') as file_content:
        content = file_content.read()
    return content

def generate_query_results(document, textList):
    with open('static/templates/doc_view.html', 'r') as file_content:
        content = file_content.read()
    content = content.replace("#url", document)
    temp = ""
    for text in textList:
        temp = temp + "<li>..." + text[0] + "...</li>\n"
    content = content.replace("#text", temp.decode('utf-8'))
    return content

def get_static_file(path):
    return static_file(path, root='./static')

