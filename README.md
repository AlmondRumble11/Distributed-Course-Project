# Distributed-Course-Project
Repository for distributed systems course project

# Links
Link to video that explains the execution of code in detail: 
> https://youtu.be/im9HmwRDSGs

Link to PDF where detail infomation about the program can be found:
> https://drive.google.com/file/d/1cfqNFuChK7oQIjWqXRoKgAcnpV1xGgEd/view?usp=sharing 

# About
The task was to build a program that finds the shortest path between two Wikipedia pages. 
RPC is used as communication method between server and client(s). Server can handle multiple clients at the same time.
Threading is used to get results faster. Server creates own thread for each of the clients so clients do not need
to wait other clients to finish before getting their own request through. Server uses tree data structure to store links
and find the shortest path using BFS(Breadth-first search) algorithm.
More details about the program can be found from the PDF-link above.

# How to run
From the commandline
To start the client run:
> python3 client.py

To start the server run:
> python3 server.py

of just run the files using F5 in editor of your choice

# Example Input 

> Give wikipedia page where to start the search: Halo 3
> 
> Give wikipedia page where to end the search: London

# Example Output
> Shortest path from 'Halo 3' to 'London' is lenght of 2:
> 
> Halo 3 --> 7-Eleven --> London
> 
> Execution time of the search was: 1.87 seconds



