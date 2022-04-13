

import json
import time
from xmlrpc.server import SimpleXMLRPCServer
import requests
import threading, queue
from socketserver import ThreadingMixIn


#https://www.youtube.com/watch?v=_8xXrFWcWao
#https://docs.python.org/3/library/xmlrpc.server.html 
#https://stackoverflow.com/questions/53621682/multi-threaded-xml-rpc-python3-7-1
#creates multihreaded server that can handle moany clients at the same time
class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass
# run server
def run_server():

    #port, host and address
    host = 'localhost'
    port = 1234
    server_addr = (host, port)

    #create server and add functions that clients can use
    server = SimpleThreadedXMLRPCServer(server_addr)
    server.register_function(checkCorrectParameters)
    server.register_function(search)
    print("Server started...")
    print('listening on {} port {}'.format(host, port))
    server.serve_forever()


#query class
class Query:

    def __init__(self):
        self.END = False #found end point
        self.path = [] #path to the end point
        


#https://stackoverflow.com/questions/2358045/how-can-i-implement-a-tree-in-python 
class TreeNode:

    #tree object
    def __init__(self, node):
        self.node_value = node
        self.parent = None
        self.links = []


    #add to list
    def add_link(self, new_link, parent):
        
        #create new node and add it to parent and parent to it
        new_child = TreeNode(new_link)
        new_child.parent = parent
        parent.links.append(new_child)
      
        #q.put(new_child)
        
#wikipedia seach to ge tall of the links
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
    #response
    response = session.get(url=url, params=params)
    data = response.json()

    #get page data
    pages = data["query"]["pages"]
    
    #list of link for the topic
    link_list = []
    
    try:
        #items from the page
        for key, value in pages.items():

            #links from the page
            for link in value["links"]:

                #is regular link
                if(link['ns'] == 0):
                    link_list.append(link["title"])

    #no links found  
    except KeyError:
        pass

    #https://stackoverflow.com/questions/14882571/how-to-get-all-urls-in-a-wikipedia-page
    #get all of the links as max number in one request is 500
    while True:

        #keyerror --> no more links
        try:

            #get extra pages
            extra_data = data['continue']['plcontinue']
            params['plcontinue'] = extra_data

            #response
            response = session.get(url=url, params=params)
            data = response.json()

            #get page data
            new_pages = data["query"]["pages"]

            #items from the page
            for key, value in new_pages.items():

                #links from the page
                for link in value["links"]:

                    #is regular link
                    if(link['ns'] == 0):
                        link_list.append(link["title"])
        except KeyError:
            break
        except json.decoder.JSONDecodeError:
            break
    return link_list

#search the tree node links
def seach_tree(start_node, end_value, query):
    
    #is start
    if start_node is None:
        return 
    
    #go through all of the links for that node
    for link in start_node.links:

        #has value and no other thread has found the path
        if (link.node_value == end_value and not query.END ):
            #print('Found the end value')
            query.END = True

            #return the link
            return link

    #did not find the link --> return the original node
    return start_node

#getting the right path
def print_path(head):
    
    #path list
    path =  []

    #temp for the list head
    temp = head

    #go from the end point to start point and add to list
    while temp is not None:
        path.append(temp.node_value)
        temp = temp.parent
    
    #as the list is backwards reverse it
    path.reverse()

    #for index in range(len(path)):
    #                
    #    if(index +1 < len(path)):
    #        print(path[index], end=' --> ')
    #    else:
    #        print(path[index])
    return path

#function that runs the algorithm. each thread run this function separitely
def algo (root_node, end,q, query):
    #https://onestepcode.com/graph-shortest-path-python/?utm_source=rss&utm_medium=rss&utm_campaign=graph-shortest-path-python
    #loop as long as no path found
    while not query.END:

        #path found
        if (query.END):
            break
        # if queue has data
        if (not q.empty()):

            #get next search node from queue
            root_node = q.get()

            #get the search value
            search_term = root_node.node_value

            #get links for that page
            links = wikipediaSearch(search_term)

            #add links to tree for tha  root node
            for link in links:
                root_node.add_link(link, root_node)
                
                #add links to queue
                q.put(root_node.links[-1])

            #search the links for the end value
            value_found = seach_tree(root_node, end, query)

            #end value found
            if(value_found != root_node):
               
                #add path to list
                path = print_path(value_found)

                #add query and set end to true so other threads know that path has been found
                query.path = path
                query.END = True
                return 

#seach/worker unit that takes the query from the client and handles it           
def search (start, end):

    #create a new query for this request
    query = Query()
    
    #create new queue for this request
    q = queue.Queue()
    
    #add start page to tree as root node and put it to queue
    root_node = TreeNode(start)
    q.put(root_node)

    #list for threads
    thread_list = []
    #st = time.time()

    #create 10 threads that run algo() function that try to find the path
    #https://www.tutorialspoint.com/python/python_multithreading.htm
    for i in range(10):
        
        work =  threading.Thread(target=algo, args=(root_node, end , q, query), daemon=True)
        work.start()
        thread_list.append(work)
    
    print('\nStarted 10 threads.')

    #join the threads together
    for thread in thread_list:
        thread.join()

    #run as long as path is found
    while True:

        #path found and return the path to client
        if(query.END):
           # et = time.time()
            #took = et-st
            #print(took)
            print('Threads closed')
            return query.path
            


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




run_server()