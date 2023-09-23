import sys
import socket
import threading
import struct
import random

l = threading.RLock()
quizEasy = {
    "Kolku noze ima pajakot? a.7 b.8 v.9": "b",
    "Koj e glaven grad na Francija? a.London b.Skopje v.Pariz": "v",
    "Koj ja naslikal Mona Liza? a.Leonardo da Vinci b.Salvador Dali v.Pablo Picasso": "a"
}

quizMedium = {
    "Koja planeta e poznata pod imeto Crvena Planeta? a.Mars b.Saturn v.Venera": "a",
    "Koj avtor ja napishal novelata Gordost i Predrasudi? a.J.K.Rowling b.Jane Austin v.Franz Kafka": "b",
    "Koj e hemiskiot simbol na zlato? a.Au b.Ag v.Pb": "a"
}

quizHard = {
    "Koj e najgolemiot organ vo chovekovoto telo? a.Kozha b.Srce v.Crn Drob": "a",
    "Koga zapochnala prvata svetska vojna? a.1918 b.1914 v.1941": "b",
    "Koja e osnovnata edinica za digitalen podatok? a.Kilobyte b.Byte v.Bit": "v"
}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def recv_all(sock, length):
    data = ''
    while len(data) < length:
        more = sock.recv(length - len(data)).decode()
        if not more:
            raise EOFError('socket closed %d bytes into a %d byte message' % (len(data), length))
        data += more

    return data.encode()

def send_question(sock, question):
    length = len(question)
    msg = struct.pack("!i", length) + question.encode()
    sock.sendall(msg)

def answer_question(sock):
    asked_questions = []    # Vo ovaa niza se zapishuvaat prashanjata koi se vekje postaveni
    score = 0               #broj na osvoeni poeni (tochno odgovoreni prashanja)
    num_asked_questions = 0 #broj na pominati prashanja

    # Serverot ja dobiva od klientot posakuvanata tezhina
    length = struct.unpack("!i", recv_all(sock, 4))[0]
    difficulty = recv_all(sock, length).decode()

    # Go postavuvame soodvetniot kviz spored tezhinata
    if difficulty == "lesno":
        quiz = quizEasy
    elif difficulty == "sredno":
        quiz = quizMedium
    elif difficulty == "teshko":
        quiz = quizHard
    else:
        # Ako klientot ne postavil tezhina, po default e lesno
        quiz = quizEasy

    while True:
        remaining_questions = [q for q in quiz.keys() if q not in asked_questions] # Da ne dojde do povtoruvanje! Pravime niza od preostanatite prashanja koi ne bile postaveni

        if not remaining_questions:
            break  # Ako site prashanja se izminati

        #Ako ima ushte:
        random_question = random.choice(remaining_questions)
        correct_answer = quiz[random_question]
        asked_questions.append(random_question)

        send_question(sock, random_question)
        
        length = struct.unpack("!i", recv_all(sock, 4))[0]
        data = recv_all(sock, length)
        client_answer = data.decode()

        #Ako klientot saka da prekine so kvizot
        if client_answer.lower() == "exit":
            break

        if client_answer == correct_answer:
            response = "Tochno!"
            score += 1
            num_asked_questions += 1
        else:
            response = "Netochno!"
            num_asked_questions += 1
        
        send_question(sock, response)
    
    send_question(sock, "Kraj na kvizot. Tvojot osvoen broj poeni: %d/%d" % (score, num_asked_questions))
    sock.close()

if sys.argv[1:] == ['server']:
    s.bind(('localhost', 1061))
    s.listen(1)
    print('Listening at', s.getsockname())
    while True:
        sc, sockname = s.accept()
        threading.Thread(target=answer_question, args=(sc,)).start()
