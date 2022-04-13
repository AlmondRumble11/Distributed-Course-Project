from operator import index
from os import link
import queue
from xmlrpc.client import ServerProxy
import sys
import time

#https://docs.python.org/3/library/xmlrpc.server.html
#server proxy
proxy = ServerProxy('http://localhost:1234')
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
        t1 = time.time()
        links = proxy.wikipediaSearch(search_term)
        t2 = time.time()
        full = t2-t1
        print(full)
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
           print(q.qsize())
           print(search_term)
           success = False


        


    




def Menu():
    print("**********************MENU****************************")
    print("1) Find the shortest path between 2 topic on Wikipedia")
    print("0) Close the program")

    while True:

        try:
            user_choice = int(input("Your choice: "))
            return user_choice
        except TypeError:
            print("Please give a number.")
        except KeyboardInterrupt:
            print("Closing the program")
            sys.exit(0)
        except ValueError:
            print("Please give a number.")
           


def main():
    print("***************************************************************")
    print("This program finds the shortest path between 2 wikipedia pages\n")
    
    while True:

        #get the use choice
        user_choice = Menu()

        #close the program
        if (user_choice == 0):
            print('Closing the program')
            break
        #seach the shortest path between the topics
        elif (user_choice == 1):
            
            try:
                start = input("\nGive wikipedia page where to start the search: ")
                end = input("Give wikipedia page where to end the search: ")
            except KeyboardInterrupt:
                print("Closing the program")
                sys.exit(0)
            except ValueError:
                print("Closing the program")
                sys.exit(0)

            if (start == end):
                print("Start and End are the same page --> shortest path is 0")
                continue

            print('Checking if both pages can be found. Please wait a moment.')

            try:
                start_found = proxy.checkCorrectParameters(start)
                end_found = proxy.checkCorrectParameters(end)
            except ConnectionRefusedError:
                print('Could not connect to wikipedia. Please try again\n')
                continue

            #checking if pages are found
            if(start_found == False):
                print('Start page not found. Please try differen search terms\n')
            elif(end_found == False):
                print('End page not found. Please try differen search terms\n')
            else:
                
                
                print('Both pages are found. Beginning the search')
                print("Searching...\n")

                #start the search timer
                start_time = time.time()
                try:
                    #call the seach function from the server
                    result = proxy.search(start, end)
                except ConnectionRefusedError:
                    print('Could not connect to wikipedia. Please try again\n')
                    continue
                #end timer
                end_time = time.time()

                #print out the results
                print("Shortest path from '{}' to '{}' is lenght of {}:".format(start,end,len(result)))
                for index in range(len(result)):
                    
                    if(index +1 < len(result)):
                        print(result[index], end=' --> ')
                    else:
                        print(result[index])
                #show the execution time
                execution_time = end_time - start_time 
                print('Execution time of the search was: ' + str(round(execution_time,2))+" seconds\n")
                    


       
        else:
            print("No functions for that number\n") 
main()

def Main():
    
    i = input("")
    x = input()
    st = time.time()
    res = proxy.search(i, x)
    print(res)
    et = time.time()
    took = et-st
    print(took)
#Main()

