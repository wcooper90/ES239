import socket, threading
import sys

from queue import Queue
from queue_content import QueueContent

host = '0.0.0.0'
port = 7976

# to change colors of terminal text
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


VERSION_NUMBER = '1'
commands = {'LOGIN': '1',
            "CREATE": '2',
            'ENTER': '3',
            'LOGIN_NAME': '4',
            "CREATE_NAME": '5',
            'DISPLAY': '6',
            'HELP': '7',
            'SHOW_QUEUE': '8',
            'ENQUEUE': '9',
            'DEQUEUE': 'a',
            'NOTHING': 'b',
            'DELETE': 'c'}

hostname=socket.gethostname()
IPAddr=socket.gethostbyname(hostname)
print("Your Computer Name is:"+hostname)
print("Your Computer IP Address is:"+IPAddr)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)              #socket initialization
server.bind((host, port))                                               #binding host and port to socket
server.listen()


# globals
USERNAMES = []
clients = {}
LOGGED_IN = set([])
oh_name = "CS 124"
OHQ = Queue(oh_name)

# deletes a username from list of usernames, removes the association from the client, and sends the appropriate message
def delete_account(client, message):
    out = 'Account deleted'
    LOGGED_IN.remove(clients[client])
    USERNAMES.remove(clients[client])

    num_deleted_items = 0
    for item in OHQ.queue:
        if item.client_id == clients[client]:
            num_deleted_items += 1

    for i in range(num_deleted_items):
        OHQ.dequeue(clients[client])

    clients[client] = ''
    return (VERSION_NUMBER + commands['DELETE'] + out).encode('ascii')


# displays the other users on the current server.
def show_queue(client, message):
    out = ''
    if len(OHQ.queue) == 0:
        out += OHQ.name + ' queue is currently empty!'
    else:
        out += repr(OHQ)
    return (VERSION_NUMBER + commands['DISPLAY'] + out).encode('ascii')


# displays the list of possible commands.
def help(client, message):
    out = 'Commands: \n /S (show existing queue) \n /E [question number(s)] -- [time_estimate(s)] -- [question notes(s)] (enqueue a question) \n /H (help) \n /D (delete account and exit) \n /X (dequeue your question)\n'
    client.send((VERSION_NUMBER + commands['DISPLAY'] + out).encode('ascii'))


# prompts the user for another input (only used when the user just presses 'enter' without typing anything)
def prompt(client, message):
    client.send((VERSION_NUMBER + commands['DISPLAY'] + '').encode('ascii'))


# conditional logic for logging in / creating an account. Updates USERNAMES and clients global data as necessary.
def login_username(username, client):
    error_message = ''
    if username[1] == commands['LOGIN_NAME']:
        if username[2:] not in USERNAMES:
            error_message = 'Username not found'
        elif username[2:] in LOGGED_IN:
            error_message = 'User currently logged in!'
        else:
            clients[client] = username[2:]
            LOGGED_IN.add(username[2:])

    if username[1] == commands['CREATE_NAME']:
        if username[2:] in USERNAMES:
            error_message = 'Username taken'
        elif ' ' in username[2:]:
            error_message = "Your username can not have spaces"
        elif '*' in username[2:]:
            error_message = "You username can not have '*'"
        else:
            USERNAMES.append(username[2:])
            clients[client] = username[2:]
            LOGGED_IN.add(username[2:])
    return error_message


# called whenever user submits a "non-command". If connected to another user, send them the chat
def text(client, message):

    sender = client
    receiver = None

    # prompt if not connected to anyone
    if not receiver:
        client.send((VERSION_NUMBER + commands['DISPLAY'] + 'Unrecognized command submitted. Type /H for help.  ').encode('ascii'))
        return


# conditional logic for disconnecting from another user. Updates connections accordingly. Prompts user for new connection.
def exit(client, message):
    return (VERSION_NUMBER + commands['DISPLAY'] + 'Commands: \n /S (show existing queue) \n /E [question number(s)] -- [time_estimate(s)] -- [question notes(s)] (enqueue a question) \n /H (help) \n /D (delete account and exit) \n /X (dequeue your question)\n').encode('ascii')


def enqueue(client, message):
    # strip header on packet
    message = message[2:]
    components = message.split('--')
    client_id = clients[client]
    while len(components) != 3:
        components.append(None)
    queue_content = QueueContent(client_id, components[0], components[1], components[2])
    OHQ.enqueue(queue_content)
    client.send((VERSION_NUMBER + commands['DISPLAY'] + 'Your question has successfully been added to the queue. You are in position number: ' + str(len(OHQ.queue))).encode('ascii'))


def dequeue(client, message):
    OHQ.dequeue(clients[client])
    client.send((VERSION_NUMBER + commands['DISPLAY'] + 'Your question has successfully been removed from the queue ').encode('ascii'))


def handle(client):
    while True:
        # for debugging purposes
        print('*'*80)
        print('clients:', clients)
        print('users:', USERNAMES)
        print('queue:', repr(OHQ))

        try:
            # wait for messages
            message = client.recv(1024).decode()

            # command conditionals
            if message[1] == commands['ENQUEUE']:
                enqueue(client, message)
            elif message[1] == commands['DEQUEUE']:
                dequeue(client, message)
            elif message[1] == commands['SHOW_QUEUE']:
                client.send(show_queue(client, message))
            elif message[1] == commands['HELP']:
                help(client, message)
            elif message[1] == commands['DELETE']:
                client.send(delete_account(client, message))
            else:
                prompt(client, message)

        except Exception as e:
            if message[1] != commands['DELETE']:
                LOGGED_IN.remove(clients[client])
            print("Broken connection: " + e)
            clients.pop(client)
            client.close()
            break


# after starting the server, allows server to accept clients
def receive():
    while True:
        client, address = server.accept()
        clients[client] = ''
        error_message = ''
        username = ''
        print("Connected with {}".format(str(address)))
        # handle logging in before starting a new thread for this user
        while True:
            client.send((VERSION_NUMBER + commands['ENTER'] + error_message).encode('ascii'))
            username = client.recv(1024).decode('ascii')
            error_message = login_username(username, client)
            # if no error, break out of loop
            if error_message == '':
                break

        print("Username is {}".format(username[2:]))
        client.send((VERSION_NUMBER + commands['DISPLAY'] + \
            'Logged in! Commands: \n /S (show existing queue) \n /E [question number(s)] -- [time_estimate(s)] -- [question notes(s)] (enqueue a question) \n /H (help) \n /D (delete account and exit) \n /X (dequeue your question)\n').encode('ascii'))

        # begin handle thread
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


# start server
receive()
