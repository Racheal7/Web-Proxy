
# import libraries
import socket
from socket import *
import sys
import datetime
from bs4 import BeautifulSoup

BUFFER_SIZE = 128*1024
hostName = "127.0.0.1"
hostPort = 2022
destination_web = "comp3310.ddns.net"
destination_port = 80

# Web proxy function
def runServer(hostName, hostPort):
    """
    This function creates a proxy server and accept connections from client browser
    and forward the request to remote server.

    Parameters
    ----------
    hostName : "localhost" or "127.0.0.1"
        Address of your computer.
    
    hostPort : port number that the proxy socket is bound to. Default set to 3310.

    """
    
    try:
        # Create a TCP Web Proxy socket.
        proxy_socket = socket(AF_INET, SOCK_STREAM)
        proxy_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)    # reuse the socket.
        proxy_socket.bind((hostName, hostPort))    # Bind the socket to localhost and port.
        proxy_socket.listen(20)     # Proxy is ready to accept connection.
        
        print("HTTP proxy socket is created on port", proxy_socket.getsockname()[1])
        print("*******************Start to get connection from Client*******************\n\n")
        print("=================Logs=================\n")

        # Start to get connection from client.
        while True:
            # Accept a client request and create a new socket for each request
            (client_socket, client_addr) = proxy_socket.accept()
            handle_client_request(client_socket, client_addr)

    except Exception as e:
        print(e)
        sys.exit(1) 
    
    # Finish and release the proxy socket.
    print("*******************Server closing all sockets and terminating*******************")
    proxy_socket.close()

def handle_client_request(client_socket, client_addr):
    """
    This function handles the client requests received by the web proxy. Rewrites the http request header
    and forward it to the remote web server.

    Parameters
    ----------
    client_socket : a client socket object.
        Usable for sending and receiving data between client browser and the web proxy.
    
    client_addr :  the address bound to the client socket on the client side.

    """
    
    # Receive data from client side.
    http_request = client_socket.recv(BUFFER_SIZE)
        
    # If no data received, close client socket.
    if len(http_request) == 0:
        print("No data received from: ", client_addr, ". Client has disconnected.")
        client_socket.close()
        return
    
    # Rewrite the http request received.
    new_request = http_parser(http_request)
    
    # Get the server IP address and create a new socket objet to transmit data between web proxy and remote server.
    (socketfamily, sockettype, _, _, dest_addr) = getaddrinfo(destination_web, destination_port)[0]
    server_socket = socket(socketfamily, sockettype)
    server_socket.setblocking(1)        # set the kernel to blocking mode.
    server_socket.settimeout(0.5)        # server_socket timeout after 0.5 seconds without responding
    server_socket.connect(dest_addr)  # connect to the remote server.
    
    # Send the modified client request to the remote server.
    server_socket.sendall(new_request)

    try:
        # Loop to receive all data.
        data = b''
        while True:
            recv_data = server_socket.recv(BUFFER_SIZE)
            
            if not recv_data:
                break
            else: 
                data = data + recv_data
                
    except timeout:
        pass
     
    # If no data received or not html page, print out the response.
    if data == b'' or b'text/html' not in data or b'404 Not Found' in data:
        get_response(data)              # Print out the response from remote server.
        client_socket.sendall(data)     # Send response to server.
    
    else:
        get_response(data)
        modified_response = modify_html(data)           # Modify the HTML page.     
        client_socket.sendall(modified_response)        # Send modified HTML to client browser
    
    # Terminate and release client socket.
    client_socket.close()


def http_parser(http_request):
    """
    This function parses the received http request and generate a new http request 
    with modified host to send to the remote server. 

    Parameters
    ----------
    http_request : http request received from the client.
    
    Returns
    -------
    new_request : the modified http request.

    """
    
    if http_request == b'':
        print("Received empty request!")
        return b''
    
    first_line_pos = http_request.find(b'\r\n')     # Get the ending position of the header first line "GET / HTTP/1.1"
    first_line = http_request[:first_line_pos]
    method, url, version = first_line.split()       # Split the first line
    
    # Print out first line of the request received from the client and time stamp
    print("\n" + first_line.decode("utf-8"))
    time_stamp = datetime.datetime.now()        # Get the request time stamp
    print("Request Time: ", time_stamp)
    
    # Rewrite the HTTP request for remote server.
    line_1 = b"GET " + url + b" HTTP/1.1\r\n"
    line_2 = b'Host: ' + destination_web.encode("utf-8") + b'\r\n'
    line_3 = b'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36\r\n\r\n'
    new_request = line_1 + line_2 + line_3
        
    return new_request


def get_response(data_from_server):
    """
    This function print out the response received from the server.

    Parameters
    ----------
    data_from_server : data received from the remote web server.

    """
    
    if data_from_server != b'':
        first_line_pos = data_from_server.find(b'\r\n')
        response = data_from_server[:first_line_pos+1]
        print("Response from server: ", response.decode("utf-8"))
        time_stamp = datetime.datetime.now()        # Get the request time stamp
        print("Response received time: ", time_stamp)


def modify_html(data_from_server):
    """
    This function modifies the received HTML file.
    It rewrites the links on the page and change the text.

    Parameters
    ----------
    data_from_server : data received from the remote web server.
    
    Returns
    -------
    modified_response : the modified http response request.

    """

    print("Start to modify the HTML")
    
    # Split the received data to http header and html. 
    pos = data_from_server.find(b'\r\n\r\n')
    header_str = data_from_server[:pos+4]
    html_str = data_from_server[pos+1:]
    
    link_change_count = 0       # counter for changed links
    text_change_count = 0       # counter for changed text
        
    # Modify text: replace "the" to "<b>eht</b>" and "The" to "<b>Eht</b> "
    html_str = html_str.replace(b" the ", b" <b>eht</b> ")  
    text_change_count += html_str.count(b"<b>eht</b>")
    html_str = html_str.replace(b"The ", b"<b>Eht</b> ")
    text_change_count += html_str.count(b"<b>Eht</b>")

    # Use BeautifulSoup library to parse the html page.
    parsed_html = BeautifulSoup(html_str, "lxml" ) 
        
    # Find all links in the html
    for link in parsed_html.find_all('a', href=True):
        if "#" in link['href']:
            continue
        
        # Change the relative links in the page
        elif ".html" not in link['href'] and link['href'][-1] != "/":
            link['href'] = link['href'] + '/'
            link_change_count += 1
            
        # For links linking to the original website, modify the link to point to the proxy.
        elif "http://www.anbg.gov.au" in link['href']:
            pos = link['href'].find("anbg.gov.au")
            new_link = link['href'][pos+11:]
            link['href'] = new_link
            link_change_count += 1

    
    # Print out modification log.
    print("+++++++ Modification Log +++++++")    
    print("Number of link changed: ", link_change_count)
    print("Number of text changed: ", text_change_count)
    print("\n")
    
    # Rewrite the response request
    first_line_pos = data_from_server.find(b'\r\n')
    first_line = data_from_server[:first_line_pos+4]
    modified_response = first_line + b'Content-Type: text/html; charset-UTF-8\r\n\r\n' + parsed_html.encode("UTF-8")

    return modified_response
            

if __name__ == "__main__":
    
    # User can choose a port number.
    if len(sys.argv) > 1:
        hostPort = int(sys.argv[1])
   
    try:
        runServer(hostName, hostPort)
        
    except KeyboardInterrupt:
        print("Stopping server")
        sys.exit(1)
        