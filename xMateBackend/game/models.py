from django.db import models
from django.conf import settings
from django.utils.timezone import now

# Create your models here.
class Game(models.Model):
    STATUS_CHOICE = [
        ('pending','Pending'),
        ('in_progress','In_Progess'),
        ('completed','Completed'),
    ]
    player_1 = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='game_as_player1',on_delete=models.CASCADE)
    player_2 = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='game_as_player2', on_delete=models.CASCADE)
    moves = models.JSONField(default=list)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="game_won",null=True,blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20,choices=STATUS_CHOICE,default='pending')
    created_at = models.DateTimeField(now)
    updated_at = models.DateTimeField(auto_now=True)
    

    def end_game(self,winner=None):
        self.status = 'completed'
        self.winner = winner
        self.save()

        if winner:
            winner.Update_stats(win=True)
            loser = self.player_1 if winner == self.player_2 else self.player_2
            loser.Update_stats(loss=True)
            
        else :
            self.player_1.Update_stats(draw=True)
            self.player_2.Update_stats(draw=True)