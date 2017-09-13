from os.path import join, isfile
import re
from random import choice, shuffle
from asyncio import gather
from datetime import datetime
from time import mktime
from os import remove, listdir

from bs4 import BeautifulSoup
from clint.textui import colored
from feedparser import parse
from newspaper import Article, Config
from requests import get
from PIL import Image

from django.db import IntegrityError
from django.conf import settings
from django.utils.encoding import smart_text

from .models import Post, Category, Links
from .summarizer.main import summarize


def load_user_agents(uafile=join(settings.BASE_DIR, 'user_agents.txt')):
    uas = []
    with open(uafile, 'r') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1-1])
    shuffle(uas)
    return uas


HEADERS = {
    "Connection" : "close",
    'User-Agent': choice(load_user_agents())
}
PROXIES_LIST = ['5.2.72.57:3128']
SSL_PROXIES = []
PROXIES = {
    'http': choice(PROXIES_LIST),
    'https': ''#random.choice(SSL_PROXIES),
}
NEWSPAPER_CONFIG = Config()
NEWSPAPER_CONFIG.browser_user_agent = HEADERS['User-Agent']
NEWSPAPER_CONFIG.skip_bad_cleaner = True
EXTS = ['png', 'jpg', 'gif', 'jpeg']
MINIMUM_IMAGE = 800


async def link_collector(what, source, initial, link_type, base_link):
    try:
        if source.status_code == 200:
            tree = BeautifulSoup(source.text, 'html.parser')

            a = tree.find_all('a')
            if not a is None:
                for l in a:
                    link = l.get('href')
                    if not link is None:
                        if (not "?" in link) & (not "Special" in link):
                            if any([w for w in what if w in link]):
                                try:
                                    if not 'https://' in link:
                                        link = "{0}{1}".format(base_link, link)
                                        entry = Links.objects.create(url=link, status_parsed=0)
                                    else:
                                        entry = Links.objects.create(url=link, status_parsed=0)
                                    entry.save()
                                    print(colored.green("Saved link."))
                                except IntegrityError:
                                    pass
    except Exception as err:
        print(colored.red("Failed at collector: {0}".format(err)))


filters = ["Wikipedia", "List", "Edit", "Printable", "link", "Information", 
    "page", "Category", "Portal", "Privacy", "User", "Upload", "Recent", "Load", 
    "account", "Help", "About", "Support", "University", "Chronicles", "Support", 
    "encouraged", "–", "Indonesia", "Scotland", "Bridge", "Stadium", "Station", "USA", "timeline",
    "tsunami", "flight", "language", "Club", "Java", "Pakubuwana", "Operation", "India", 
    "earthquake", "United", "Netherlands", "Germany", "French", "France", "Agreement", 
    "East", "West", "South", "North", "prosecutor", "Council", "representative", 
    "National", "Croatia", "Hungary", "Poland", "Russia", "novel", "United Kingdom", "Urdu",
    "story", "movie", "China", "Chinese", "Prize", "College", "Europe", "century", "Spanish",
    "Italian", "Romania", "Original", "song", "Philippines", "Pakistan", "Asia", "Japan",
    "Pornography", "women", "Culture", "Child", "Coalition", "Entertainment", "film",
    "Association", "America", "Canada", "Mexico", "UK", "Picture", "Company",
    "production", "Irish", "Republic", "Treaty", "system", "Sultanate", "County",
    "Kingdom", "Shah", "Dynasty", "Dynasty", "Regency", "Lake", "Island", "Islands", "Archipelago", 
    "each", "Peninsula", "What's", "Sea", "Jakarta", "Center", "Analysis", "News", "Daily", 
    "Review", "Fruit", "Olympics", "play", "Championship", "Player", "Award", "Template", "poem",
    "Repatriation", "Worrying", "Sky", "Weird", "Star", "Watch", "Tale", "Dream", "Named", 
    "Test", "Fun", "Springfield", "Fish", "Burns", "Badly", "Falls", "Car", "Bart", "Series",
    "Planet", "Two", "Homer", "Studios", "Simpsons", "Marge", "Loves", "The"]


async def get_names(base_link, i):
    if not 'https://' in i.url:
        link = base_link + i.url
    else:
        link = i.url
    if 'en' in link:
        print(colored.yellow(link))

        s = get(link, headers=HEADERS)

        if s.status_code == 200:
            tree = BeautifulSoup(s.text, 'html.parser')

            a = tree.find_all('a')

            for el in a:
                title = el.get('title')
                if not title is None:
                    if not any(f.lower() in str(title.lower()) for f in filters):
                        try:
                            spl = title.split(" ")
                            if len(spl) >= 2:
                                nw = []
                                for word in spl:
                                    if word[0].isupper():
                                        nw.append(word)
                                if len(nw) >= 2:
                                    t = " ".join(nw)
                                    try:
                                        if len(title) > 1:
                                            a = Category.objects.create(title=title)
                                            print(colored.green("Saved celeb {}".format(title)))
                                    except IntegrityError:
                                        pass
                                    except Exception as err:
                                        print(colored.red(err))
                        except:
                            pass


def parse_celeb_names(loop, base_link):
    loop.run_until_complete(gather(*[get_names(base_link=base_link, i=i) \
        for i in Links.objects.all()], return_exceptions=True))


async def process_links(what, source, base_link):
    try:
        if 'https://' in source.url:
            s = get(source.url, proxies=PROXIES, headers=HEADERS)
            await link_collector(what=what, source=s, initial=source.url, link_type=0, base_link=base_link)
        else:
            link = "{0}{1}".format(base_link, source.url)
            s = get(link, proxies=PROXIES, headers=HEADERS)
            await link_collector(what=what, source=s, initial=source.url, link_type=0, base_link=base_link)
    except Exception as err:
        print(colored.red("Failed at parsing db links: {0}".format(err)))


def get_links(loop, what, main_link, base_link, iterations):
    #l = Links.objects.all().delete()
    if Links.objects.count() == 0:
        source = get(main_link, proxies=PROXIES, headers=HEADERS)
        if source.status_code == 200:
            tree = BeautifulSoup(source.text, 'html.parser')

            for l in tree.find_all('a'):
                link = l.get('href')
                try:
                    if not "?" in link:
                        if not "Special" in link:
                            if any([w for w in what if w in link]):
                                entry = Links.objects.create(url=link, status=0)
                                entry.save()
                                print(colored.green("Saved link {}.".format(link)))
                except IntegrityError:
                    pass
                except Exception as err:
                    print(colored.red("Failed at initial parse: {}".format(err)))
    else:
        for i in range(iterations):
            sources = Links.objects.filter(status=0)

            loop.run_until_complete(gather(*[process_links(what=what, source=source, base_link=base_link) \
                for source in sources], return_exceptions=True))


def check_names():
    celebs = Category.objects.all()
    i = 0
    for celeb in celebs:
        if any([w.lower() in str(celeb.title).lower() for w in filters]):
            celeb.delete()


def get_body_from_internet(url):
    try:
        article = Article(url, config=NEWSPAPER_CONFIG)
        article.download()
        article.parse()
    except Exception as err:
        print(colored.red("At get_body_from_internet {}".format(err)))

    return article


def replace_all(text, dic):
    """
    Replaces all occurrences in text by provided dictionary of replacements.
    """
    for i, j in list(dic.items()):
        text = text.replace(i, j)
    return text


def get_image_locs(url):
    try:
        image_name_, filename = None, None
        try:
            image_name_ = url.split('?', 1)[0]
        except:
            pass
        image_name_ = image_name_.rsplit('/', 1)[-1]

        if any(ext in image_name_ for ext in EXTS):
            replacements = {"%": "", ")": "", "]": "", "'": "", ",": "", "-": "", \
                "_": "", "=": ""}
            img = replace_all(image_name_, replacements)
            image_name = img.split(".")[-2][:100].replace(".", "") + "." + img.split(".")[-1]
            filename = join(settings.BASE_DIR, 'uploads', image_name)
    except Exception as err:
        print(colored.red("At get_image_locs {}".format(err)))

    return (image_name, filename)


def check_image_format(filename, image_name):
    try:
        img = None
        with Image.open(filename) as format_checker:
            width, height = format_checker.size
            if not format_checker.format is None:
                if width < MINIMUM_IMAGE or height < MINIMUM_IMAGE:
                    format_checker.close()
                    remove(filename)
                else:
                    format_checker.close()
                    img = "uploads/{}".format(image_name)
            else:
                format_checker.close()
                remove(filename)
    except Exception as err:
        print(colored.red("At check_image_format {}".format(err)))

    return img


def save_image(post_count, filename, source, image_name):
    try:
        img = None
        if post_count == 0:
            with open(filename, 'wb') as image:
                image.write(source.content)
                image.close()
                img = check_image_format(filename=filename, image_name=image_name)
        else:
            img = "uploads/{}".format(image_name)
    except Exception as err:
        print(colored.red("At save_image {}".format(err)))

    return img


def download_image(url):
    try:
        image_name, filename = None, None
        if len(url) > 0:
            source = get(url, headers=HEADERS)
            image_name, filename = get_image_locs(url=url)
            if not image_name is None:
                post_count = Post.objects.filter(image="uploads/{0}".format(\
                    image_name)).count()
                img = save_image(post_count=post_count, filename=filename, \
                    source=source, image_name=image_name)
            else:
                img = None
    except Exception as err:
        print(colored.red("At download_image {}".format(err)))

    return img


def get_date(data):
    try:
        date_now = datetime.fromtimestamp(mktime(data.published_parsed))
    except Exception as err:
        print(colored.red("[ERROR] At creation parsing date: {0}".format(err)))
        date_now = datetime.now()

    return date_now


def resize_image(file_name):
    try:
        file_path = join(settings.BASE_DIR, file_name)
        img = Image.open(file_path)
        w, h  = img.size
        factor = 1
        if w > 800:
            factor = 1/(w/800)
        if factor != 1:
            resized = img.resize((int(w*factor), int(h*factor)), Image.ANTIALIAS)
            resized.save(file_path)
            print(colored.green("Resized image."))
    except Exception as err:
        print(colored.red("At resize_image {}".format(err)))


def check_image_exist(image_name):
    """
    Checks if image exists in the uplods folder.
    """
    if not isfile(join(settings.BASE_DIR, image_name)):
        image_name = None

    return image_name


def posts_to_db(row):
    try:
        if not row['image_url'] is None:
            row['image_url'] = check_image_exist(image_name=row['image_url'])
            resize_image(file_name=row['image_url'])
            if (not row['image_url'] is None) & ('uploads' not in row['image_url']):
                row['image_url'] = 'uploads/' + row['image_url']
            if len(row['image_url'].split(".")[0]) == 0:
                row['image_url'] = None

        entry = Post.objects.create(title=smart_text(row['title']), url=row['url'],  \
            image=row['image_url'], content=smart_text(row['summary']), \
            date=row['date'], category=row["category"])

        entry.save()
        print(colored.green("Article saved to db."))
    except Exception as err:
        print(colored.red("[ERROR] At post to db: {0}".format(err)))


def content_creation(data, cat):
    try:
        row = {}

        row['category'] = cat
        row['title'] = data.title
        print(data.title)
        row['url'] = get(data.link, headers=HEADERS).url
        body = get_body_from_internet(url=row['url'])
        if len(body.top_image) > 0:
            row['image_url'] = download_image(url=body.top_image)
        else:
            row['image_url'] = None
        row['content'] = body.text
        if (not row['content'] is None) | (not row['content'] is ""):
            row['summary'] = summarize(words=row['content'], \
                num_of_sentences=2)
        else:
            row['summary'] = None
        row['date'] = get_date(data=data)

        if not row['summary'] is None:
            posts_to_db(row=row)
    except Exception as err:
        print(colored.red("At content_creation {}".format(err)))


def parse_item(posts, data, cat, i):
    try:
        post = posts.get(title=data.entries[i].title)
    except Exception as err:
        if len(data.entries[i].title) > 0:
            content_creation(data=data.entries[i], cat=cat)


async def get_story(cat, posts):
    try:
        feed = "https://news.google.com/news/feeds?cf=all&ned=us&hl=en&q={0}&output=rss".format(cat.title.replace(" ", "+"))
        print(feed)
        data = parse(feed)
        if data.bozo == 0:
            for i in range(0, len(data.entries)):
                parse_item(posts=posts, data=data, cat=cat, i=i)
        cat.parsed = True
        cat.save()
    except Exception as err:
        print(err)


def get_stories(loop):
    cats = Category.objects.filter(parsed=1)
    posts = Post.objects

    loop.run_until_complete(gather(*[get_story(cat=cat, posts=posts) \
        for cat in cats], return_exceptions=True))


def reset():
    cats = Category.objects.filter(parsed=0)

    if cats.count() == 0:
        for cat in cats:
            cat.parsed = 1
            cat.save()


def clean_images_from_db():
    path = join(settings.BASE_DIR, 'uploads')
    filenames = [f for f in listdir(path) if isfile(join(path, f))]
    posts = Post.objects.all()

    for post in posts:
        try:
            if "uploads/" in str(post.image):
                #remove "uploads/" (len 8) and check if file exists in folder
                if str(post.image)[8:] not in filenames:
                    print("Updating image {}".format(post.image))
                    post.image = None
                    post.save()
                    print(colored.green("Updated image as non-existent"))
        except Exception as err:
            print(colored.red("At check_img {}".format(err)))


def clean_images_from_folder():
    path = join(settings.BASE_DIR, 'uploads')
    filenames = [f for f in listdir(path) if isfile(join(path, f))]

    for f in filenames:
        try:
            post_count = Post.objects.filter(image='uploads/{0}'.format(f)).count()
            if post_count == 0:
                print("File not in db: {0}".format(f))
                filename = join(settings.BASE_DIR, 'uploads', f)
                remove(filename)
                print("Removed {0}".format(filename))
        except Exception as err:
            print(colored.red("At check_db_for_image {}".format(err)))