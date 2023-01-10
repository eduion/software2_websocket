#simple websockets brocaster
import asyncio
import websockets
import json
clients = [] #to store all connected cleints
players = []
click = []
state = [[0 for i in range(5)] for j in range(5)]

#handler for socket message activities
async def handler(websocket, path):
	#print(path) #path is not used currently
    if websocket not in clients:
        clients.append(websocket) #append new cleint to the array
    async for message in websocket:
        global players
        global state
        global click
        msg = message.split('###')
        print(msg,'received from client') #print to console
        if msg[0]=="play":
            if len(players)>=2:
                click.append(websocket)
                await websocket.send("已經有人在對戰!")
            else:
                players.append(websocket)
                n = len(players)
                n = str(n)
                await broadcast_click(n+"###prepare")
        elif msg[0] == "number":
            n = len(players)
            n = str(n)
            if len(players)>=2:
                await websocket.send("已經有人在對戰!")
            else:
                await broadcast(n)
        elif msg[0] == "land":
            left = players[0]
            msg[1] = str(msg[1])
            row = int(msg[1][1])
            column = int(msg[1][0])
            if websocket == left:
                state[row][column] = state[row][column] + 1
                r = msg[1][1]
                c = msg[1][0]
                point = str(state[row][column])
                await color(r+"###"+c+"###"+point+"###"+"notify")
            else:
                state[row][column] = state[row][column] - 1
                r = msg[1][1]
                c = msg[1][0]
                point = str(state[row][column])
                await color(r+"###"+c+"###"+point+"###"+"notify")
        elif msg[0] == "stop":
            count_l = 0
            count_r = 0
            winner = 0
            for i in range(len(state)):
                for j in range(len(state)):
                    if state[i][j]>0:
                        count_l = count_l + 1
                    elif state[i][j]<0:
                        count_r = count_r + 1
            if count_l<count_r:
                winner = 1
            elif count_l == count_r:
                winner = 2
            count_l = str(count_l)
            count_r = str(count_r)
            winner = str(winner)
            await color(count_l+"###"+count_r+"###"+winner+"###"+"end")
        elif msg[0] == "out":
            players = []
            n = len(players)
            n = str(n)
            state = [[0 for i in range(5)] for j in range(5)]
            await broadcast_click(n+"###prepare")
async def broadcast_click(msg):
    m = msg.split("###")
    await broadcast(m[0])
    print(msg,'show_number')
    for websock in click:
        try:
            await websock.send(msg) #send message to each client
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected. Do cleanup")
            clients.remove(websock)
async def broadcast(msg):
    print(msg,'show_number')
    for websock in clients:
        if websock not in click:
            try:
                await websock.send(msg) #send message to each client
            except websockets.exceptions.ConnectionClosed:
                print("Client disconnected. Do cleanup")
                clients.remove(websock)
        
async def color(msg):
    print(msg,'color')
    for websock in players:
        try:
            await websock.send(msg) #send message to each client
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected. Do cleanup")
            clients.remove(websock)

#starts the service and run forever
loop = asyncio.new_event_loop() #get an event loop
asyncio.set_event_loop(loop) #set the event loop to asyncio
loop.run_until_complete(
	websockets.serve(handler,'localhost', 8989) #setup the websocket service and handler
	) #hook to localhost:4545
loop.run_forever() #keep it running