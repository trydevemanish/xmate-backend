from django.db import models

# Create your models here.
class User(models.Model):
    name = models.TextField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.TextField(min=8,max_length=23)
    total_game_played = models.PositiveIntegerField(default=0)
    total_game_win = models.PositiveIntegerField(default=0)
    total_game_losses = models.PositiveIntegerField(default=0)
    total_game_draw = models.PositiveIntegerField(default=0)
    total_points = models.PositiveIntegerField(default=0)

    # this method will help to update the score of the user 
    def Update_stats(self,win=False,loss=False,draw=False):
        self.total_game_played += 1
        if win:
            self.total_game_win += 1
            self.total_points += 10
        elif loss:   
            self.total_game_losses += 1
        elif draw:
            self.total_game_draw += 1
            self.total_points += 5
        self.save()
