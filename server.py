"""

"Multiplayer game - Enter the number closest to the average" server.py file

This script is responsible for the server. It can only be run on one terminal. 
The next launch of it will result in the error "Only one usage of each socket address 
(protocol / network address / port) is normally permitted".

The server side is responsible for the state of the game, player support, storing the 
results, and appropriate response to errors. The server displays on the terminal the 
appropriate activities that it performs in relation to individual players

This script requires 'socket', 'time', 'threading', 'array' modules

This file contains the following functions:

    * checkconnectionwithclient
    * handleclient
    * informclient
    * handleroundwithclient
    * checkresults
    * closeconnectionwithclients
    * handlenewconnection

"""

from socket import *
import time
import threading
from array import *
import logging

print("[STARTING] Server is starting....")
serversocket = socket(AF_INET, SOCK_STREAM) # create an INET, STREAMing socket
serversocket.bind(('localhost', 8000)) # bind the socket to a local host, and to port 8000
serversocket.listen(5) # become a server socket
print("[LISTENING] Server is listening on port 8000")

''' Variables and collections used in server.py '''
numberofrounds = 1 # A Variable which counts number of rounds
numberoftours = 1 # A Variable which counts number of tours
numberofplayers = 0 # A Variable which counts number of tours
maximalvalue = 0 # A variable that is the threshold that players must reach in order to complete the tour
hasguessed = 0 # A variable which increments if connected player have guessed
clientaddresses = [] # List containging lists of (clientsocket, clientaddress, names)
scores = [] # A List containing scores of connected players in the rounds
points = [] # A List containing points of connected players
names = [] # A List containing names of connected players
absentplayers = [["name"],[0]] # A List containing the names of disconnected users and their points
roundfinished = False # A Flag used for multi-threading
stopconnectingnewplayers = False # A Flag used for multi-threading
reconnected = False # A Flag used for multi-threading
tourfinished = False # A Flag used for multi-threading

def checkconnectionwithclient(clientsocket, numberofplayer):
    ''' This function checks whether the client with given clientsocket is online or offline, and reacts appropriately to the exceptions

    Parameters
    ----------
    clientsocket: 
        The socket of the player whose connectivity is being checked
    numberofplayer: 
        The index of the player whose connectivity is being checked
    
    Returns
    -------
    numberofplayers:
        How many players are currently connected to the server
    '''
    global hasguessed
    global numberofplayers
    global playersdisconnected
    message = str(numberofplayers)
    try:
        clientsocket.send(message.encode('ascii'))
        data = clientsocket.recv(1024)
    except ConnectionAbortedError or ConnectionError or ConnectionRefusedError:
        playersdisconnected -= 1
        print("Connection error with player: " + str(clientsocket))
        print("Received false data")
        numberofplayers -= 1
        absentplayers[0].append(names[numberofplayer])
        absentplayers[1].append(points[numberofplayer])
        names.pop(numberofplayer)
        clientaddresses.pop(numberofplayer)
        scores.pop(numberofplayer)
        points.pop(numberofplayer)
        if(numberofplayer == numberofplayers):
            return
        checkconnectionwithclient(clientaddresses[numberofplayer][0], numberofplayer)
        time.sleep(1)
        handleroundwithclient(clientaddresses[numberofplayer][0],clientaddresses[numberofplayer][1],numberofplayer)
        return
    if len(data) == 0:
        playersdisconnected -= 1
        print("Connection error with player: " + str(clientsocket))
        print("Received false data")
        numberofplayers -= 1
        absentplayers[0].append(names[numberofplayer])
        absentplayers[1].append(points[numberofplayer])
        names.pop(numberofplayer)
        clientaddresses.pop(numberofplayer)
        scores.pop(numberofplayer)
        points.pop(numberofplayer)
        if(numberofplayer == numberofplayers):
            return   
        checkconnectionwithclient(clientaddresses[numberofplayer][0], numberofplayer)
        time.sleep(1)
        handleroundwithclient(clientaddresses[numberofplayer][0],clientaddresses[numberofplayer][1],numberofplayer)
    return numberofplayers

def handleclient(clientsocket, clientaddress, numberofplayer):
    ''' This function connects the client with server and gathers information about the user's nickname

    Parameters
    ----------
    clientsocket: 
        The socket of the player whose connectivity is being checked
    clientaddress: 
        The address of the player whose connectivity is being checked
    numberofplayer: 
        The index of the player whose connectivity is being checked
    
    Returns
    -------
    Nothing
    '''
    messagereceived = clientsocket.recv(1024)
    print("Connected player with ip: " + str(clientaddress))
    names.append(messagereceived.decode('ascii'))
    clientaddresses[numberofplayer][2] = messagereceived.decode('ascii')
    if (messagereceived in absentplayers[0]) == True:
        index = absentplayers[0].index(messagereceived)
        points[numberofplayers] = absentplayers[1][index]
        absentplayers[0].pop(index)
        absentplayers[1].pop(index)
    message = "Connection was successful, please wait for other players\n"
    clientsocket.send(message.encode('ascii'))

def informclient(clientsocket, numberofplayer):
    ''' This function informs clients about the readiness of other players 

    Parameters
    ----------
    clientsocket: 
        The socket of the player whose connectivity is being checked
    numberofplayer: 
        The index of the player whose connectivity is being checked
    
    Returns
    -------
    Nothing
    '''
    message = "All players have joined the game, please wait\n"
    clientsocket.send(message.encode('ascii'))

def handleroundwithclient(clientsocket, clientaddress, numberofplayer):
    ''' This function operates the game while waiting for the player's reaction in the form of a guessed number (it checks whether the player pressed CTRL+C, which results in sudden disconnection)
    If four players are not connected, the server will wait for the primary players to rejoin

    Parameters
    ----------
    clientsocket: 
        The socket of the player whose connectivity is being checked
    clientaddress: 
        The address of the player whose connectivity is being checked
    numberofplayer: 
        The index of the player whose connectivity is being checked
    
    Returns
    -------
    Nothing
    '''
    global hasguessed
    global numberofplayers
    global roundfinished
    message = "\n\nStarting the round number: " + str(numberofrounds) + ", your current score is: " + str(points[numberofplayer])
    clientsocket.send(message.encode('ascii'))
    guess = clientsocket.recv(1024)
    guesstostring = str(guess.decode('ascii'))
    if len(guess) == 0:
        print("There were problem with connection and gathering information about player's input")
        if numberofplayers == 4: # If there were only 4 players in the game we have to reconnect player to keep the game going
            absentplayers[0].append(names[numberofplayer])
            absentplayers[1].append(points[numberofplayer])
            names.pop(numberofplayer) 
            roundfinished = True # We need to set the flag which allows to continue the background thread (handlenewconnection()) which is responsible for adding new users
            while True:
                if reconnected == True: # Once a thread added a user, continue
                    break
            numberofplayers -= 1
            clientaddresses[numberofplayer] = clientaddresses[numberofplayers] # Replace primary user information
            copy = names[numberofplayers-1]
            for i in reversed(range(numberofplayer,numberofplayers-1)):
                    names[i+1] = names[i]
            names[numberofplayer] = copy
            clientaddresses.pop(numberofplayers)
            scores.pop(numberofplayers)
            points.pop(numberofplayers)
            clientsocket = clientaddresses[numberofplayer][0]
            clientaddress = clientaddresses[numberofplayer][1]
            time.sleep(1)
            checkconnectionwithclient(clientsocket, numberofplayer)
            time.sleep(1)
            handleroundwithclient(clientsocket,clientaddress,numberofplayer) # Call the same function again, giving the player an opportunity to guess the numbers again
            time.sleep(1)
            roundfinished = False
            return
        if numberofplayers > 4: # If there were more then 4 players we don't need to connect the player at this point, the game may continue without him/her
            checkconnectionwithclient(clientsocket, numberofplayer)
            print("Lost connection with: " + str(clientsocket))
            return
    else:
        numbertoint = int(guesstostring.split(' ')[1]) # Split the guesstostring up to get the number and convert it to int
        hasguessed += 1 # Increment the variable which makes sure that all players have guessed
        scores[numberofplayer] = numbertoint # store the value in scores


def checkresults():
    ''' This function checks the results of the current round. The person who comes up with the number closest to the average wins 1 point. 
    If players guess the same number, they lose 1 point

    Parameters
    ----------
    Nothing
    
    Returns
    -------
    Nothing
    '''
    global points
    global scores
    sumofguesses = 0
    for i in range(0, len(scores)):
        sumofguesses += scores[i]

    closestscore = [0, 0, 0, 0]
    for i in range(0, len(closestscore)):
        closestscore[i] = abs(scores[i]-(sumofguesses)/len(closestscore))  # calculates the scores closest to the mean with absolute value

    minimialvalue = min(closestscore)
    whichelement = 0
    for i in range(0, len(closestscore)):
        if closestscore[i] == minimialvalue:
            whichelement = i

    scoreset = set(closestscore)
    numberofduplicates = len(closestscore) - len(scoreset)

    if (numberofduplicates != 0):  # Checking if there are duplicates in guessed numbers
        duplicates = []
        for i in range(0, len(closestscore)):
            for j in range(0, len(closestscore)):
                if (i != j and scores[i] == scores[j]):
                    duplicates.append(i)
                    if points[i] > 0:
                        points[i] -= 1 # Subtract 1 point
                    break
        if duplicates.count(whichelement) == 0:
            points[whichelement] += 1
    else:
        points[whichelement] += 1 # Add 1 point


def closeconnectionwithclients():
    ''' This function closes connection with all connected clients

    Parameters
    ----------
    Nothing
    
    Returns
    -------
    Nothing
    '''
    for i in range(0, numberofplayers):
        clientsocket = clientaddresses[i][0]
        print('Connection was closed with client ' + str(clientsocket)) # Write out with which client the connection was closed
        clientsocket.close()

def handlenewconnection():
    ''' This function deals with connections of new clients in the background, and in case of disconnection of any of the basic players 
    (when there are 4 players in the game and one of them disconnects) server reacts appropriately

    Parameters
    ----------
    Nothing
    
    Returns
    -------
    Nothing
    '''
    global numberofplayers
    global reconnected
    print("Establishing new connection with another players in the background")
    while True:
        while True: 
            time.sleep(1)
            if roundfinished == True: # Waiting for the round to finish so new clients can join the game without interrupting others
                break
        try:
            (clientsocket, clientaddress) = serversocket.accept()
            print("Connection received from: ", clientaddress)
            clientaddresses.append([0, 0, 0, 0])
            scores.append(0)
            points.append(0)
            messagereceived = clientsocket.recv(1024)
            print("Connected player with ip: " + str(clientaddress) + " in the background...")
            names.append(messagereceived.decode('ascii'))
            clientaddresses[numberofplayers][2] = messagereceived.decode('ascii')
            if (messagereceived in absentplayers[0]) == True:
                index = absentplayers[0].index(messagereceived)
                points[numberofplayers] = absentplayers[1][index]
                absentplayers[0].pop(index)
                absentplayers[1].pop(index)
            message = "Connection was successful, please wait for other players\n"
            clientsocket.send(message.encode('ascii'))
            informclient(clientsocket, numberofplayers)
            clientaddresses[numberofplayers][0] = clientsocket
            clientaddresses[numberofplayers][1] = clientaddress
            while True:
                if roundfinished == True:
                    break
            numberofplayers += 1
            reconnected = True
        except:
            print("There were problems while handling new connection")
            if(tourfinished == True):
                break

''' The main loop servicing the game from the server side '''
while True:
    roundfinished = False
    tourfinished = False
    thread_1 = threading.Thread(target=handlenewconnection).start() # The thread that works in the background, connects the players to the server

    if numberofplayers < 4:
        print("Waiting for players...")
    else:
        print("All players are online and active")

    iterator = 0
    while numberofplayers < 4: # Loop that connects minimal number of players to start the game
        clientaddresses.append([0, 0, 0, 0])
        scores.append(0)
        points.append(0)
        (clientsocket, clientaddress) = serversocket.accept()
        clientaddresses[numberofplayers][0] = clientsocket
        clientaddresses[numberofplayers][1] = clientaddress
        print("Connection received from: ", clientaddress)
        numberofplayers += 1
        handleclient(clientsocket, clientaddress, iterator)
        iterator += 1
        print("Connection handled, returning to listenting on port 8000")
        print("Waiting for players...")

    for i in range(0, numberofplayers):
        clientsocket = clientaddresses[i][0]
        informclient(clientsocket, i) # Send message to clients: "All players have joined the game"
        time.sleep(0.01)

    while numberofplayers >= 4 and maximalvalue < 3: # Loop which starts new rounds
        roundfinished = False
        hasguessed = 0
        print("Starting round number: " + str(numberofrounds) + " with: " + str(numberofplayers) + " players")

        global playersdisconnected
        playersdisconnected = numberofplayers

        for i in range(0, numberofplayers):
            if i == playersdisconnected:
                break
            clientsocket = clientaddresses[i][0]
            clientaddress = clientaddresses[i][1]
            checkconnectionwithclient(clientsocket, i)
            time.sleep(1)
            handleroundwithclient(clientsocket, clientaddress, i)

        while True:
            time.sleep(1)
            if hasguessed == numberofplayers: # If all the players had managed to guess the average, calculate the points
                checkresults()
                break

        maximalvalue = max(points)

        if maximalvalue < 3:
            for i in range(0, numberofplayers):
                message = "All players have entered the random number, first joiner is starting a new round. Please wait..."
                clientaddresses[i][0].send(message.encode('ascii'))

        numberofrounds += 1
        roundfinished = True # Set flag to True, so new users can connect
        time.sleep(3)
    
    if maximalvalue == 3:
        print("In tour number: " + str(numberoftours))
        for i in range(0, numberofplayers):
            print("Player with username: " +
                  str(names[i]) + ", earned: [" + str(points[i]) + "] points")

        whichelement = 0
        result = ""
        for i in range(0, len(points)):
            if points[i] == maximalvalue:
                whichelement = i
                result = "Tour number: " + str(numberoftours) + " has won user with username: " + str(
                    names[whichelement]) + ", with [" + str(maximalvalue) + "] points." # Sending messages to players about winnings
        print(result)

        for i in range(0, numberofplayers):
            if i != whichelement: # Sending confirmation of the end of the round and congratulations to the winner
                message = "The tour has finished!  Your score is: " + str(points[i]) + ", you lacked " + str(abs(points[i]-points[whichelement]))+ " points to win"
            else:
                message = "The tour has finished!  Congratulations, you have won with score: " + str(points[i])
            clientaddresses[i][0].send(message.encode('ascii'))
            message = result
            clientaddresses[i][0].send(message.encode('ascii'))
        
        closeconnectionwithclients() # Closing connections with clients, allowing them to rejoin, or quit the game
        tourfinished = True
        time.sleep(1)
        serversocket.close()
        serversocket = socket(AF_INET, SOCK_STREAM) # create an INET, STREAMing socket
        serversocket.bind(('localhost', 8000)) # bind the socket to a local host, and to port 8000
        serversocket.listen(5) # become a server socket 

        print("Cleaning the counters and starting new round") # Setting base values of variables
        numberofrounds = 1 
        numberofplayers = 0
        maximalvalue = 0
        hasguessed = 0
        clientaddresses = []
        scores = []
        points = []
        names = []
        absentplayers = [["name"],[0]]
        numberoftours += 1  
        
        # Starting a new tour in while loop...
