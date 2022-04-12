

from collections import defaultdict
import time
from xmlrpc.server import SimpleXMLRPCRequestHandler
from xmlrpc.server import SimpleXMLRPCServer
from matplotlib.pyplot import title
import requests
import threading, queue
from multiprocessing.pool import ThreadPool
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
q = queue.Queue()




class TreeNode:

    def __init__(self, node):
        self.node_value = node
        self.parent = None
        self.links = []


    
    def add_link(self, new_link, parent):
        
        new_child = TreeNode(new_link)
        new_child.parent = parent
        parent.links.append(new_child)
      
        q.put(new_child)
    

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
        
    #print(len(link_list))
    return link_list

def seach_tree(start_node, end_value):

    if start_node is None:
        return 
    
    
    for link in start_node.links:

        if (link.node_value == end_value):
            print('Found the end value')
            print(link.node_value, end_value)
            return link

    return start_node

def print_path(head):
    path =  []
    temp = head
    while temp is not None:
        print(temp.node_value)
        path.append(temp.node_value)
        temp = temp.parent
    
    path.reverse()

    for index in range(len(path)):
                    
        if(index +1 < len(path)):
            print(path[index], end=' --> ')
        else:
            print(path[index])
    return 

def search (start, end):

    #links = proxy.wikipediaSearch(start)
    #print(links)

    root_node = TreeNode(start)
    value_found = False
    search_term = start
    success = False
    own_queue = []
    own_queue.append(start)
    q.put(root_node)
    while not q.empty():

        q.task_done()
        #t1 = time.time()
        links = wikipediaSearch(search_term)
       # t2 = time.time()
        #full = t2-t1
        #print(full)
        for link in links:
            root_node.add_link(link, root_node)
        
        value_found = seach_tree(root_node, end)
        
        if(value_found != root_node):
            print_path(value_found)
            success = True
            break
        else:
           root_node = q.get()
           search_term = root_node.node_value
           #print(q.qsize())
          # print(search_term)
           success = False


def Main2():
    st = time.time()
    search("Mämmi", "Fox")
    et = time.time()
    took = et-st
    print(took)
Main2()






def iterateList(graph,end_topic,visited,topic,link):

    #while True:
        
       # graph = item[0]
       # end_topic = item[1]
       #visited = item[2]
       # topic = item[3]
       # link = item[4]
        #found = item[5]
        #print(link)
        value = []
        if (link == end_topic):
            print('Topic found')
            
            #print("It took",taken_time,"seconds")
            graph[link] = graph[topic] + [link]
            print(graph[link])
            
            #q.task_done() 
            value = []
            value.append(graph[link])
            value.append(True)
            
            return   [graph[link], True]
            
        #if not
        else:
            #add new link to graph only if it is not there yet (could lead to interesting results otherwise)
            if(link not in graph):

                #add new link to graph. Idea {linkname: previous levels, linkname}
                graph[link] = graph[topic] + [link]
                #visited.append(link)
                value.append(graph[link])
                #value.append(visited)
                value.append(False)
                visited.append(link)
                return  [link, False]
            #return q.task_done() 
        return [link, False]
        

       
                
      


      

def Main():
    begin_time = time.time()
    #start_topic = "Halo 3"
    start_topic = "United States"
    #start_topic = "Elizabeth II"
    #end_topic = "Alligator"
    #end_topic = "Bread"
    #end_topic = "New York City Police Department"
    #end_topic = "New York City"
    end_topic = "London"
    #end_topic = 'Elon Musk'
    #https://www.geeksforgeeks.org/shortest-path-unweighted-graph/
    graph = {}

 
    graph[start_topic] = [start_topic]
    visited = []
   
    visited.append(start_topic)
    index = 0
    topic_list = wikipediaSearch(start_topic) #0...280
    
    while True:

        #get links for the topic name
        topic = visited[index]
        topic_list = wikipediaSearch(topic)
        results = []
      
        
        #send_list = []
        #https://stackoverflow.com/questions/26104512/how-to-obtain-the-results-from-a-pool-of-threads-in-python/26104609#26104609
        pool = ThreadPool(30)
        results = []
        for link in topic_list:
            results.append(pool.apply(iterateList, args=(graph,end_topic,visited,topic,link)))
        pool.close()
        pool.join()
        
        for r in results:
            

            if(r[1] == True):
        #        print(r[0])
                end_time = time.time()
                taken_time = end_time - begin_time
                print("It took",taken_time,"seconds")
                return 0


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

#the algorithm function
def search(start, end):



    return ["Halo 3","7-Eleven","London"]
server.register_function(checkCorrectParameters)
server.register_function(search)
server.register_function(wikipediaSearch)
#Main()

#def main():
#    try:
#        print('Starting server')
#        server.serve_forever() #runnin the server
#    except KeyboardInterrupt:
#        print('Shutting down the server')
#main()
