from django.db import models
from django.conf import settings
from django.utils.timezone import now
import uuid

# Create your models here.
class Game(models.Model):
    STATUS_CHOICE = [
        ('pending','Pending'),
        ('in_progress','In_Progess'),
        ('completed','Completed'),
    ]
    PLAYER_2_JOINING_STATUS = [
        ('player_2_not_joined','Player_2_Not_Joined'),
        ('player_2_joined','Player_2_Joined')
    ]
    game_id = models.UUIDField(default=uuid.uuid4,editable=False,unique=True,name="game_id")
    player_1 = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='game_as_player1',null=True,on_delete=models.CASCADE)
    player_2 = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='game_as_player2',null=True,on_delete=models.CASCADE)
    moves = models.JSONField(default=list)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="game_won",null=True,blank=True, on_delete=models.SET_NULL)
    game_draw = models.BooleanField(default=False)
    player_2_status = models.CharField(max_length=30,choices=PLAYER_2_JOINING_STATUS,default='player_2_not_joined')
    game_status = models.CharField(max_length=20,choices=STATUS_CHOICE,default='pending')
    created_at = models.DateTimeField(now)
    updated_at = models.DateTimeField(auto_now=True)
    

    def end_game(self,winner=None):
        self.game_status = 'completed'
        self.winner = winner
        self.save()

        if winner:
            winner.Update_stats(win=True)
            loser = self.player_1 if winner == self.player_2 else self.player_2
            loser.Update_stats(loss=True)
            
        else :
            self.player_1.Update_stats(draw=True)
            self.player_2.Update_stats(draw=True)