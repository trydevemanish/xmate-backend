import json
import chess
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Game

board = chess.Board()

class GameComsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f"game_{self.game_id}"

        query_string = self.scope['query_string'].decode('utf-8')
        query_params = parse_qs(query_string)
        self.user = query_params.get('user', [None])[0] 
        print('usersname',self.user)
        print('game id',self.game_id)

        if not self.user:
            print('Closing the connection no username is provided')
            await self.close()
            return
        
        if not self.game_id:
            print('Closing the connection no game_id was provided')
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Broadcast the user's online status to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type' : 'user_status',
                'user': self.user,
                'status' : 'online'
            }
        )

        # fetch all the game move instance and broadcast it to the room group
        game = await sync_to_async(Game.objects.filter(game_id=self.game_id).first)()
        if not game:
            print('Closing the connection game id is invalid') 
            await self.close()
            return
        
        for move_uci in game.moves:
            move = chess.Move.from_uci(move_uci)
            board.push(move)

        print('board.fen()',board.fen())
        # print('board.turn',board.turn,'White' if board.turn else 'Black')

        # Broadcasting the fen move to all 
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type' : 'game_state',
                'fen'  :  board.fen(),
                'turn' :  'White' if board.turn else 'Black'
            }
        )
    

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'user'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user': self.user,
                    'status': 'offline'
                }
            )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self,text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        if action == 'online-status':
            # Broadcast online status to the group
            online = text_data_json.get('online', 'offline')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user': self.user,
                    'status': online
                }
            ) 

        elif action == 'make-move':
            move_passed = text_data_json.get('move_passed') #Example like this - e6e9
            print('move_passed downward of actions',move_passed)
            move_passed_converted_from_uci = chess.Move.from_uci(move_passed)
            # check is move is legal 
            if not board.is_legal( move_passed_converted_from_uci):
                # show a message to the frontend end that the move is not legal
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "game_event",
                        "event": "move_not_legal",
                        "message": f"${move_passed} not legal move"
                    }
                )

            if board.is_check():
                # show a message to the frontend end that the board is in check 
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "game_event",
                        "event": "check",
                        "message": f"Player {board.turn} is in check!"
                    }
                )

            if board.is_checkmate():
                # show a message to the frontend end that the board is in the checkmate position 
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "game_event",
                        "event": "checkmate",
                        "message": f"Checkmate! Player {not board.turn} wins!"
                    }
                )

            if board.is_stalemate():
                # show a message to the frontend end that the board is in the stalemate condition  
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "game_event",
                        "event": "stalemate",
                        "message": "Stalemate! The game is a draw."
                    }
                )

            print('trying to add the move to the board') 

            # if Everycheck pass then update the board with the move 
            board.push(move_passed_converted_from_uci)
            print('successfully added the move to the board')   

            # adding the move take time to the backend will sure take time so sending the message early that game updated 
            # Broadcast the game state to both player 
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type' : 'game_state',
                    'fen'  :  board.fen(),
                    'turn' :  'White' if board.turn else 'Black'
                }
            )

            # now add the move to the backend
            game = await sync_to_async(Game.objects.filter(game_id=self.game_id).first)()
            # game = Game.objects.filter(game_id=self.game_id)
            if not game:
                print('Game id is invalid, failed to find game instance')
                return 
            
            print('got the game_instance')

            # await sync_to_async()
            game.moves.append(move_passed)

            print('appended the move in the game_instance')
            await sync_to_async(game.save)()
            print('Move Added to the backend',move_passed)

    
    # to broadcast the online status of the user to the group
    async def user_status(self, event):
        # Send user status to WebSocket
        await self.send(text_data=json.dumps({
            'action': 'online-status',
            'user': event['user'],
            'status': event['status']
        }))

    # to broadcast the game event of the board to the group
    async def game_event(self, event):
        # Send user status to WebSocket
        await self.send(text_data=json.dumps({
            'action': 'game-event',
            'event': event['event'],
            'message': event['message']
        }))

    # to broadcast the game_state of the board to the group
    async def game_state(self,event):
        await self.send(text_data=json.dumps({
            'action': 'make-move',
            'fen'  :  board.fen(),
            'turn' :  'White' if board.turn else 'Black'
        }))


# things to acheive 


# Create a chess game instance - board
# When we connect to the socket   
#     -> fetch move from the game model 
#     -> find the fen string 
#     -> send this string to the all the people in the group in the websocket 



# when a player 1 makes a moves  
#     the move is send to the websocket 
#     check if the move is legal 
#     check if the game state is not in the check,checkmate,stalemate etc..else
#     if everything is right update the game state 
#     make a call to add the move to the game instance backend 
#     and send the fen string to the backend  


