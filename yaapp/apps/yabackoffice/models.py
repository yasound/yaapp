from yabase.models import Radio

class BackofficeRadio(Radio):
    class Meta:
        proxy = True

    @property
    def song_count(self):
        playlist, _created = self.get_or_create_default_playlist()
        return playlist.songinstance_set.all().count()
