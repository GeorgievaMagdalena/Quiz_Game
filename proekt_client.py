import sys
import socket
import struct

def recv_all(sock, length):
    data = b''
    while len(data) < length:
        more = sock.recv(length - len(data))
        if not more:
            raise EOFError("Socket closed %d bytes into a %d-byte message" % (len(data), length))
        data += more
    return data

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

if sys.argv[1:] == ['client']:
    s.connect(('localhost', 1061))
    print("Dobredojde vo Kvizot. Vnesi ja bukvata pred tvojot odgovor. Napishi exit za kraj")

    ###
    difficulty = input("Izberi tezhina (lesno, sredno, teshko): ")
    difficulty_length = len(difficulty)
    s.sendall(struct.pack("!i", difficulty_length))
    s.sendall(difficulty.encode())  

    while True:
        length = struct.unpack("!i", recv_all(s, 4))[0]
        question = recv_all(s, length).decode()
        print(question)

        if question.startswith("Kraj na kvizot"):
            break

        client_answer = input("Tvojot odgovor: ")

        length1 = len(client_answer)
        fullmsg = struct.pack("!i", length1) + client_answer.encode()
        s.sendall(fullmsg)

        length2 = struct.unpack("!i", recv_all(s, 4))[0]
        reply = recv_all(s, length2).decode()
        print(reply)

    s.close()
