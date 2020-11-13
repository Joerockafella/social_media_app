from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    name = 'profiles'

    #importing the signals file
    def ready(self):
        import profiles.signals 
