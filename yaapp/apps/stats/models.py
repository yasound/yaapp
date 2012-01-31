from django.db import models

class RadioListeningStat(models.Model):
    radio = models.ForeignKey('yabase.Radio')
    date = models.DateTimeField(auto_now_add=True)
    overall_listening_time = models.FloatField()
    audience = models.IntegerField()
    favorites = models.IntegerField()
    likes = models.IntegerField()
    dislikes = models.IntegerField()
    
    def __unicode__(self):
        return 'stat for %s' % self.radio
    