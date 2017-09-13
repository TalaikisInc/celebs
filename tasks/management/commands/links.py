from asyncio import get_event_loop

from django.core.management.base import BaseCommand

from tasks.tasks import get_links, parse_celeb_names, check_names


class Command(BaseCommand):
    help = 'Celebrities parser.'

    def handle(self, *args, **options):
        what = ["actors", "", "models", "personalities", "celebrities", "comedians", "dancers", "Cebrity",
            "singers", "musicians", "writers", "wrestlers", "boxers", "actresses"]
        main_link = "https://en.wikipedia.org/wiki/Lists_of_celebrities"
        base_link = "https://en.wikipedia.org"
        iterations = 2

        loop = get_event_loop()

        get_links(loop=loop, what=what, main_link=main_link, base_link=base_link, iterations=iterations)
        parse_celeb_names(loop=loop, base_link=base_link)
        check_names()

        loop.close()

        self.stdout.write(self.style.SUCCESS('Successfully done parsing jobs'))
