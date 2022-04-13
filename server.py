

from http import client
import json
import time
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
import requests
import threading, queue
#https://www.youtube.com/watch?v=_8xXrFWcWao
#https://docs.python.org/3/library/xmlrpc.server.html 
#host and port
host = 'localhost'
port = 1234

#server request handler
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)
#creating server
server = SimpleXMLRPCServer((host,port), requestHandler=RequestHandler,logRequests=True ,allow_none=True,encoding='utf-8')

END = False
Client_list =  {}
clients = {}
client_done = {}


#https://stackoverflow.com/questions/2358045/how-can-i-implement-a-tree-in-python 
class TreeNode:

    def __init__(self, node):
        self.node_value = node
        self.parent = None
        self.links = []


    
    def add_link(self, new_link, parent):
        
        new_child = TreeNode(new_link)
        new_child.parent = parent
        parent.links.append(new_child)
      
        #q.put(new_child)
        

    

def wikipediaSearch(start_topic):

  
    #https://www.mediawiki.org/wiki/API:Search
    #creaiting new request
    session = requests.Session()

    #url
    url = "https://en.wikipedia.org/w/api.php"

    #open search parameters
    params = {
        "action": "query",
        "titles": start_topic,
        "prop": "links",
        "format": "json",
        "pllimit": "max"
    }
    
    #https://stackoverflow.com/questions/14882571/how-to-get-all-urls-in-a-wikipedia-page
    response = session.get(url=url, params=params)
    data = response.json()
    pages = data["query"]["pages"]
    
    link_list = []
    
    try:
        for key, value in pages.items():
            for link in value["links"]:
                if(link['ns'] == 0):
                    link_list.append(link["title"])
          
    except KeyError:
        pass

    #https://stackoverflow.com/questions/14882571/how-to-get-all-urls-in-a-wikipedia-page
    while True:
        try:
            extra_data = data['continue']['plcontinue']
            params['plcontinue'] = extra_data

            response = session.get(url=url, params=params)
            data = response.json()
            new_pages = data["query"]["pages"]
            for key, value in new_pages.items():
                for link in value["links"]:
                    if(link['ns'] == 0):
                        link_list.append(link["title"])
        except KeyError:
            break
        except json.decoder.JSONDecodeError:
            break
        
    #print(len(link_list))
    return link_list

def seach_tree(start_node, end_value):

    if start_node is None:
        return 
    
    
    for link in start_node.links:

        if (link.node_value == end_value):
            print('Found the end value')
            
            return link

    return start_node

def print_path(head):
    path =  []
    temp = head
    while temp is not None:
       # print(temp.node_value)
        path.append(temp.node_value)
        temp = temp.parent
    
    path.reverse()

    for index in range(len(path)):
                    
        if(index +1 < len(path)):
            print(path[index], end=' --> ')
        else:
            print(path[index])
    return path

def worker (root_node, end,q,id):
    global END
    global Client_list
    global clients
    global client_done
    found = False

    
    while not  client_done[id]:
        
        if (not q.empty()):
            root_node = q.get()
            search_term = root_node.node_value
            
            links = wikipediaSearch(search_term)
            for link in links:
                root_node.add_link(link, root_node)
                q.put(root_node.links[-1])
            value_found = seach_tree(root_node, end)
           # print(found)
            if(value_found != root_node):
            #    found = True
           # if(found):
                path = print_path(value_found)

                q.task_done()
                Client_list[id] = path
                client_done[id] = True
                
def search2 (start, end, clientID,q):
    global client_done
    global clients
    #links = proxy.wikipediaSearch(start)
    #print(links)
    print('new connection')
   

    root_node = TreeNode(start)
    clients[clientID] = root_node
    
    q.put(root_node)
    thread_list = []
   
    for i in range(10):
        work =  threading.Thread(target=worker, args=(clients[clientID], end,q, clientID ), daemon=True)
        work.start()
        thread_list.append(work)
    for thread in thread_list:
        thread.join()
    while True:
        if(client_done[clientID]):
            #print(Client_list)
            #print(clients[clientID].node_value)
            return Client_list[clientID]
            



def Main2(start, end):
    global clients
    global client_done
    st = time.time()
    print(start, end)
    q = queue.Queue()
    


    new_client_identifier = len(clients) + 1
    clients[new_client_identifier] = [start]
    client_done[new_client_identifier] = False



    #start a new thread for the client that handles client messages
    client_thread = threading.Thread(target=search2, args=(start,end, new_client_identifier,q), daemon=True)
    client_thread.start()
    
    while True:
       if(client_done[new_client_identifier]):
            print(Client_list)
            return Client_list[new_client_identifier]
    #search2("Halo 3", "London")
    #et = time.time()
    #took = et-st
    #print(took)
    #print(Client_list)
    #return Client_list
#Main2()



def print_line():
    return "hello"




#checking the correct seachterm
def checkCorrectParameters(parameter):

    #https://www.mediawiki.org/wiki/API:Search
    #creaiting new request
    session = requests.Session()

    #url
    url = "https://en.wikipedia.org/w/api.php"

    #open search parameters
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": parameter
    }
    
    #https://stackoverflow.com/questions/14882571/how-to-get-all-urls-in-a-wikipedia-page
    response = session.get(url=url, params=params)
    data = response.json()

    #check that parameter is real page
    if data['query']['search'][0]['title'] == parameter:
        return True
    else:
        return False


server.register_function(checkCorrectParameters)
server.register_function(search2)
server.register_function(wikipediaSearch)
server.register_function(Main2)
server.register_function(print_line)
print('Starting server')
server.serve_forever()


#def main():
#    try:
#        print('Starting server')
#        server.serve_forever() #runnin the server
#    except KeyboardInterrupt:
#        print('Shutting down the server')

#ain()