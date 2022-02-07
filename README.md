# Multiplayer game (enter the number closest to the average)

## Design

Client-Server design

The client's side is responsible for sending numbers from the given range, proper 
handling of incorrect input, and entering a username on connection.

The server side is responsible for the state of the game, player support, storing the 
results, and appropriate response to errors. The server displays on the terminal the 
appropriate activities that it performs in relation to individual players

## Dependiencies

This script requires following libraries to be installed: 
- socket
- time
- threading
- array' modules
