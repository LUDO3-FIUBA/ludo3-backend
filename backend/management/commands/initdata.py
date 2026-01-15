from django.core.management import BaseCommand, call_command
from backend.models import User # if you have a custom user
from backend.models.auth_identity import AuthIdentity


class Command(BaseCommand):
    help = "DEV COMMAND: Fill databasse with a set of data for testing purposes"

    def handle(self, *args, **options):
        call_command('loaddata', 'seeds')
        # Fix the passwords of fixtures
        for user in User.objects.all():
            user.set_password(user.password)
            user.save()

        for user in User.objects.all():
            if not AuthIdentity.objects.filter(user=user).exists():
                AuthIdentity.objects.create(
                    user=user,
                    provider='local',
                    provider_user_id=user.dni or str(user.pk),
                    email=user.email,
                )
