from asyncio import get_event_loop

from django.core.management.base import BaseCommand

from tasks.tasks import get_stories, reset


class Command(BaseCommand):
    help = 'Celebrities parser.'

    def handle(self, *args, **options):
        loop = get_event_loop()

        get_stories(loop=loop)
        reset()

        loop.close()

        self.stdout.write(self.style.SUCCESS('Successfully done parsing jobs'))
