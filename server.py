# Ofir Shtrosberg, Itamar Laredo
import socket, sys
import os

# Initialize server IP and Port (given as argument)
# and buffer to receive messages
TCP_IP = '0.0.0.0'
TCP_PORT = int(sys.argv[1])
BUFFER_SIZE = 10000

# Socket initializes and determines to listen to
# only one client.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

while True:
    # If timeout pass, passing to the next client
    conn, addr = s.accept()
    data = conn.recv(BUFFER_SIZE)
    print(data)
    IS_ALIVE = True
    conn.settimeout(1)
    try:
        while IS_ALIVE is True:
            # Split the data and save in str1 the client request
            str1 = data.split()[1]
            # In case client sent empty message -> connection close
            if not data:
                conn.close()
                break

            if str1 is '/':
                str1 = "index.html"
            else:
                str1 = str1[1:]

            # Case redirect sent the new location and close the connection
            if str1 == "redirect":
                conn.send('HTTP/1.1 301 Moved Permanently\n')
                conn.send('Connection: close\n')
                conn.send('Location: /result.html\n')
                conn.send('\n')
                conn.close()
                IS_ALIVE = False

            # Case file in path
            elif os.path.isfile(str1) is True:
                length = str(os.path.getsize(str1))
                condition = data.split("Connection: ")[1]
                condition = condition.split('\r\n')[0]
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Connection: ' + condition + '\n')
                conn.send('Content-Length: ' + length + '\n')
                conn.send('\n')
                if condition == "keep-alive":
                    IS_ALIVE = True
                else:
                    conn.close()
                    IS_ALIVE = False
                # Case file format is jpg or ico -> reading lines as bytes
                if str1.split('.')[1] == "jpg" or str1.split('.')[1] == "ico":
                    with open(str1, "rb") as file:
                        lines = file.read()
                    conn.send(lines)
                # Otherwise, read lines
                else:
                    with open(str1, "r") as file:
                        lines = file.read()
                    conn.send(lines)
            # The requested file is not in the folder -> connection close
            else:
                conn.send('HTTP/1.1 404 Not Found\n')
                conn.send('Connection: close\n')
                conn.send('\n')
                conn.close()
                IS_ALIVE = False
            if not IS_ALIVE:
                break
            data = conn.recv(BUFFER_SIZE)
            print(data)
    except socket.timeout:
        conn.close()
        IS_ALIVE = False
