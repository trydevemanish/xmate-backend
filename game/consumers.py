import json
import traceback
import chess
from .models import Game
from urllib.parse import parse_qs
from collections import defaultdict
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


import logging

logger = logging.getLogger(__name__)
boards = defaultdict(chess.Board)
user_connections = {}


@database_sync_to_async
def get_game_data(game_id):
    return Game.objects.filter(game_id=game_id).select_related('player_1', 'player_2').first()


class GameComsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.game_id = self.scope['url_route']['kwargs']['game_id']
            query_params = parse_qs(self.scope['query_string'].decode('utf-8'))
            self.user = query_params.get('user', [None])[0] 
            self.user_id = query_params.get('user_id', [None])[0] 

            if not self.user or not self.user_id:
                print('username and userid not present')
                await self.close()
                return
            
            # logger.info('paas the self.user and self.user_id test')

            self.room_group_name = f"game_{self.game_id}"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # logger.info('Creataed a room group')

            await self.accept()

            logger.info(f"WebSocket connection attempt: game_id={self.game_id}, user={self.user}, user_id={self.user_id}")
            

            if self.user_id in user_connections:
                print(f"Duplicate connection detected for user {self.user_id}. Closing old connection.")
                old_channel_name = user_connections[self.user_id]
                try:
                    await self.channel_layer.send(
                        old_channel_name,
                        {"type": "force_disconnect"}
                    )
                except Exception as e:
                    print(f"Failed to close old connection: {e}")
                    if self.user_id in user_connections:
                        del user_connections[self.user_id]
                        print('deleteing the prev user conn')
                        await self.close()
                        return

            
            user_connections[self.user_id] = self.channel_name

            # self.game = await sync_to_async(Game.objects.filter(game_id=self.game_id).select_related('player_1', 'player_2').first())()

            self.game = await get_game_data(self.game_id)

            if not self.game:
                print('Issue Occured while fetching game')
                self.close()
                return 
            

            if self.user_id != str(self.game.player_1.id) and self.user_id != str(self.game.player_2.id):
                print("Closing connection: User is not part of this game")
                await self.close()
                return
            

            if self.game_id not in boards:
                board = chess.Board()
                for move_uci in self.game.moves:
                    move = chess.Move.from_uci(move_uci)
                    if board.is_legal(move):
                        board.push(move)
                    else:
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                "type": "game_event",
                                "event": "move_not_legal",
                                "message": f"${move} is not a legal move - game distrupted: dismiss this game"
                            }
                        )
                        
                boards[self.game_id] = board
            else:
                board = boards[self.game_id]

            # logger.info('checking if the user is in the game')
            
            await self.update_player_status()

            # logger.info('updating user status')

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type' : 'game_state',
                    'fen'  :  board.fen(),
                    'turn' :  'White' if board.turn else 'Black',
                    'move' :  board.peek().uci() if len(board.move_stack) > 0 else ''
                }
            )

            # logger.info('Everythings works fine')
            
        
        except Exception as e:
            # logger.error(f"Error during connect(): {e}", exc_info=True)
            print(f"Error during WebSocket connection: {e}")
            traceback.print_exc()
            await self.close()
            return

    
    async def disconnect(self, close_code):
        # try:
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # logger.info(f"Disconnected from {self.room_group_name} with code {close_code}")

        if self.user_id in user_connections:
            del user_connections[self.user_id]

        # Update and broadcast player status
        await self.update_player_status()

        # except Exception as e:
        #     print(f"Error during WebSocket disconnection: {e}")
        #     await self.close()
        #     return




    async def receive(self,text_data):
        # try:
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        if action == 'make-move':
            try:

                # board instance from the dictaniory
                board = boards[self.game_id]
                move_passed = text_data_json.get('move_passed')
                print('move_passed downward of actions',move_passed)

                move_passed_converted_from_uci = chess.Move.from_uci(move_passed)

                
                if board.is_legal(move_passed_converted_from_uci):
                    board.push(move_passed_converted_from_uci)
                else:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "game_event",
                            "event": "move_not_legal",
                            "message": f"${move_passed} not legal move"
                        }
                    )

                
                # adding the move take time to the backend will sure take time so sending the message early that game updated 
                # Broadcast the game state to both player 
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type' :  'game_state',
                        'fen'  :   board.fen(),
                        'turn' :  'White' if board.turn else 'Black',
                        'move' :  board.peek().uci() if len(board.move_stack) > 0 else ''
                    }
                )
                    
                if board.is_check():
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "game_event",
                            "event": "check",
                            "message": f"Player {'White' if board.turn else 'Black'} is in check!"
                        }
                    )

                if board.is_checkmate():
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "game_event",
                            "event": "checkmate",
                            # "message": f"Checkmate! Player {not board.turn} wins!"
                            "message": f"Checkmate! Player {'Black' if board.turn else 'White'} wins!"
                        }
                    )

                if board.is_stalemate():
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "game_event",
                            "event": "stalemate",
                            "message": "Stalemate! The game is a draw."
                        }
                    )

                self.game.moves.append(move_passed)
                # await sync_to_async(self.game.moves.append(move_passed))()

                await sync_to_async(self.game.save)()

            except Exception as e:
                print(f"Issue Occured while Making move: {str(e)}")
                await self.close()
                return
            

        elif action == 'last-message':
            try:
                message = text_data_json.get('message')
                print('message from the websocket',message)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "pass_last_message",
                        "message": message
                    }
                )
            except Exception as e:
                print(f"Issue Occured while sending last msg: {str(e)}")
                await self.close()
                return
            
                
        # except Exception as e:
        #     print(f"Error during WebSocket Receive: {e}")
        #     await self.close()
        #     return





    async def update_player_status(self):
        # try:

        player1_id = str(self.game.player_1.id) if self.game.player_1 else None
        player2_id = str(self.game.player_2.id) if self.game.player_1 else None

        player_status = {
            'player1' : 'online' if player1_id in user_connections else 'offline',
            'player2' : 'online' if player2_id in user_connections else 'offline',
        }

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_status',
                'player_status': player_status
            }
        )


        # except Exception as e:
            # print(f"Error during WebSocket UpdatePlayer_status: {str(e)}")


    async def force_disconnect(self, event):
        await self.close()


    async def player_status(self, event):
        await self.send(text_data=json.dumps({
            'action': 'update-player-status',
            'player_status': event['player_status']
        }))

    async def game_event(self, event):
        await self.send(text_data=json.dumps({
            'action': 'game-event',
            'event': event['event'],
            'message': event['message']
        }))

    async def game_state(self,event):
        board = boards[self.game_id]

        await self.send(text_data=json.dumps({
            'action': 'make-move',
            'fen'  :  board.fen(),
            'turn' :  'White' if board.turn else 'Black',
            'move' :  board.peek().uci() if len(board.move_stack) > 0 else ''
        }))



# asked that is this the cuase because i have written "daphne" in my installed app 

