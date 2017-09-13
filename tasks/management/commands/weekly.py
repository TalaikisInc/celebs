from django.core.management.base import BaseCommand

from tasks.tasks import clean_images_from_db, clean_images_from_folder


class Command(BaseCommand):
    help = 'Weekly tasks.'

    def handle(self, *args, **options):
        clean_images_from_db()
        clean_images_from_folder()

        self.stdout.write(self.style.SUCCESS('Successfully done parsing jobs'))
