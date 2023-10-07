import socket, threading
import sys
username = ""

# change color of terminal text
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

# USER MODIFY THE FOLLOWING LINE WITH IP_ADDRESS OF SERVER
IP_ADDRESS = '127.0.0.1'

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

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((IP_ADDRESS, 7976))

# pretty much same as Wednesday, removed the redundant connection at the beginning which asks for login/create account.
def login_message():
    global username
    choice = None
    while choice != "L" and choice != "C":
        choice = input("Log in (L) or create an account (C): ")
    if choice == "L":
        username = input("Enter username: ")
        return VERSION_NUMBER + commands['LOGIN_NAME'] + username
    else:
        username = input("Create new username: ")
        return VERSION_NUMBER + commands['CREATE_NAME'] + username


# parse user's input text. Specifically deal with commands beginning with '/'
def parse_arg(input):
    if not input:
        return VERSION_NUMBER + commands['NOTHING'] + ''

    input_strip = "".join(input.split())

    command = 'TEXT'
    if input_strip[0] == '/':
        if input_strip[1] == 'H':
            command = 'HELP'
        if input_strip[1] == 'E':
            command = 'ENQUEUE'
        if input_strip[1] == 'D':
            command = 'DELETE'
        if input_strip[1] == 'X':
            command = 'DEQUEUE'
        if input_strip[1] == 'S':
            command = 'SHOW_QUEUE'

    if command == 'TEXT' or command == 'HELP' or command == 'DEQUEUE' or command == 'DELETE' or command == 'SHOW_QUEUE':
        out_message = VERSION_NUMBER + commands[command] + ''
        return out_message
    elif command == 'ENQUEUE':
        enqueue = check_enqueue_validity(input_strip[2:])
        return VERSION_NUMBER + commands[command] + enqueue
    else:
        return VERSION_NUMBER + commands[command] + input_strip[2:]


def check_enqueue_validity(text):
    # TF can add a question bank here to make sure questions are from valid sources
    def is_question_num_valid(q_num):
        return True
    while len(text.strip()) == 0 or not is_question_num_valid(text):
        text = input("Please submit a valid request (question number -- time estimate [optional] -- question notes [optional]):")

    return text

def receive():
    global username
    while True:

        try:
            message = client.recv(1024).decode('ascii')
            # print("size of transfer buffer: " + str(sys.getsizeof(message)))
            # only for login and create names functions
            if message[1] == commands['ENTER']:
                if message[2:]:
                    print(message[2:])
                m = login_message()
                client.send(m.encode('ascii'))

            # deleting the account. Break out of while loop
            elif message[1] == commands['DELETE']:
                if message[2:]:
                    print(message[2:])
                client.close()
                return

            # poll for input
            elif message[1] == commands['DISPLAY']:
                if message[2:]: print(message[2:])
                inp = input(":")
                m = parse_arg(inp)
                client.send(m.encode('ascii'))


            # I assume when receiving chats from other users, message should be directly printed here. Not sure if it will be this easy in practice.
            # a new color can be toggled for received chats by serverside.
            else:
                if message[2:]:
                    print(message[2:])


        except Exception as e:
            print("An error occured!")
            print(e)
            client.close()
            break


# write thread function. When a user is connected, they can send messages
def write():
    while True:
        inp = input()
        m = send_text(inp)
        if m[2:] == 'end':
            client.send(m.encode('ascii'))
            return
        client.send(m.encode('ascii'))


# start the client
receive_thread = threading.Thread(target=receive)
receive_thread.start()
