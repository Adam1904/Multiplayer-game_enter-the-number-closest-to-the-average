"""

"Multiplayer game - Enter the number closest to the average" client.py file

This script is responsible for the client. An unlimited number of players can 
actually join the game. At least four clients must be connected to the server 
for the game to start according to the task.

The client's side is responsible for sending numbers from the given range, proper 
handling of incorrect input, and entering a username on connection.

It also includes testing the connection with the server in the form of sending a 
b'Ping ' packet, and checking if there are four players connected in the game, 
before each round.

This script requires 'socket' module

"""

from socket import *

''' The main loop servicing the game from the client side '''
while True:

    print("Connecting to server....\n\n\n")
    clientsocket = socket(AF_INET, SOCK_STREAM)
    try: # Handling exceptions that may arise when connecting to the server
        clientsocket.connect(('localhost',8000))
        print("Connected to server on port 8000")
    except ConnectionRefusedError:
        print("Connection was refused. Exiting the game")
        exit(0)

    while True:
        try:
            message = input("Please enter your username: ")
        except ValueError:
            print("Invalid input, please try again.")
        except KeyboardInterrupt:
            print("Invalid input(Registered SIGINT from keyboard), please try again")
        except: # Other exceptions
            print("Invalid input, please try again...")
        if message:
            break
    clientsocket.send(message.encode('ascii'))
    response = clientsocket.recv(1023)  # Receiving the first message, making contact with server
    print(response.decode('ascii'))
    response = clientsocket.recv(1023) # Checking if all clients are connected, and they are ready to play the game
    print(response.decode('ascii'))


    isrunning = True # Flag for the loop handling tours of the game
    response = 0
    while isrunning: 
        response = clientsocket.recv(1023) # Checking connection with server
        response = int(response.decode('ascii'))
        if response < 4: # If there aren't 4 players break the loop and wait for all users
            break 

        clientsocket.send(b'PING') # Checking if player is connected
        response = clientsocket.recv(1023) # Gathering information from server about current round number
        print(response.decode('ascii'))

        numbertostring = ""
        numbertoint = -1
        while True and (numbertoint > 1000 or numbertoint < 0): # Handling user-generated exception
            try:
                guessednumber = input("Please enter random number from range [0,1000] (press CTRL+C to quit): ")
                numbertoint = int(guessednumber)
                numbertostring = "Guess: " + str(numbertoint)
            except ValueError:
                print("Invalid input, please try again.")
            except KeyboardInterrupt:
                print("\nRegistered SIGINT from keyboard. Closing the game")
                clientsocket.close()
                quit()
            if numbertoint > 1000 or numbertoint < 0:
                print("Wrong number, please try again....")

        clientsocket.send(numbertostring.encode('ascii')) # Send to server guessed number
        print("Waiting for the server...")

        while True: # Waiting until all of the players will end guessing the number
            response = clientsocket.recv(1024) # Printing server response about readiness
            response = str(response.decode('ascii'))
            print(response)
            if ("The tour has finished!" in response) == True: # The client will wait in a loop until he receives game status message from the server
                isrunning = False
            break


    response = clientsocket.recv(1024).decode('ascii') # Gathering information about player's scores and printing response
    print(response)
    response = clientsocket.recv(1024).decode('ascii') # Gathering information about the winner and printing response
    print(response)
    keepplaying = input("Do you want to keep playing? Please enter y/n: ")
    if keepplaying == 'n': # If the client does not enter 'n', the game will start again
        break
            
clientsocket.close() # if the player does not wish to continue, close the clientsocket
print("Game was closed")
