import logging
import tkinter as tk
from tkinter import messagebox

import click
import requests
import yaml
from bs4 import BeautifulSoup
from peewee import *

# Logger setup
logging.basicConfig(filename='tags_counter.log', filemode='w', level=logging.INFO)

# DB
db = SqliteDatabase('tags.db')


class BaseModel(Model):
    class Meta:
        database = db


class Tag(BaseModel):
    url = CharField(unique=True)
    count = DecimalField(default=None)


# simple utility function to create tables
def create_tables():
    with db:
        db.create_tables([Tag])


# HELPERS
def get_full_url(url):
    logging.info("Open aliases yml...")
    with open("aliases.yaml", 'r') as aliases_file:
        try:
            logging.info("Load aliases...")
            aliases = yaml.safe_load(aliases_file)
            full_url = aliases[url]
            logging.info("Found alias")
        except yaml.YAMLError:
            logging.error("Can't parse yml")
            full_url = url
        except KeyError:
            logging.info("Can't find alias")
            full_url = url

    if not full_url.lower().startswith("http"):
        full_url = "https://" + full_url
        logging.info("Add https to url...")

    return full_url


def get_tags_num(url):
    url = get_full_url(url)

    try:
        logging.info("Get html page...")
        response = requests.get(url)
        logging.info("Write html page to file...")
        file = open('./response.html', 'wb')
        file.write(response.content)
        file.close()
        t = open('./response.html')
        logging.info("Parse html page...")
        soup = BeautifulSoup(t, "html.parser")
        tags_num = len(soup.find_all())
        t.close()

    except requests.exceptions.InvalidURL:
        logging.error("Invalid url")
        return None
    except requests.exceptions.ConnectionError:
        logging.error("Connection error")
        return None

    logging.info("Save to DB...")
    with db.atomic():
        try:
            Tag.create(
                url=url,
                count=tags_num)
        except IntegrityError:
            Tag.update(
                url=url,
                count=tags_num)

    return tags_num


def get_tags_num_from_db(url):
    url = get_full_url(url)

    logging.info("Load from DB...")
    try:
        tag = Tag.get(url=url)
        return tag.count
    except Tag.DoesNotExist:
        logging.error("Can't load from DB...")
        return None


# gui
master = tk.Tk()

canvas = tk.Canvas(master, width=400, height=300)
canvas.pack()

label1 = tk.Label(master, text='Calculate number of HTML tags')
label1.config(font=('helvetica', 14))
canvas.create_window(200, 25, window=label1)

label2 = tk.Label(master, text='Enter your URL:')
label2.config(font=('helvetica', 10))
canvas.create_window(200, 100, window=label2)

# entry box
url_entry = tk.Entry(master)
canvas.create_window(200, 140, window=url_entry)


def on_calculate_click():
    url = url_entry.get()

    tags_num = get_tags_num_from_db(url)
    if tags_num is not None:
        result_label['text'] = 'Result from db: ' + str(tags_num)
        return

    tags_num = get_tags_num(url)
    if tags_num is None:
        messagebox.showinfo("Error", "Invalid URL")
        return

    result_label['text'] = 'Result: ' + str(tags_num)


# buttons
get_button = tk.Button(text='Calculate tags', command=on_calculate_click)
canvas.create_window(200, 180, window=get_button)

# result label
result_label = tk.Label(master, text='')
canvas.create_window(200, 240, window=result_label)


# CLI
def _get(url):
    tags_num = get_tags_num(url)

    if tags_num is None:
        print('Error: Check URL and internet connection')
        return

    print('Result: ', tags_num)
    pass


def _view(url):
    tags_num = get_tags_num_from_db(url)

    if tags_num is None:
        print('Error: URL is not found in DB')
        return

    print('Result from DB: ', tags_num)
    pass


@click.command()
@click.option('--get', '-g', help='get list of tags')
@click.option('--view', '-v', help='view data from db')
def main(get, view):
    if get is not None:
        _get(get)
    elif view is not None:
        _view(view)
    else:
        master.mainloop()


if __name__ == "__main__":
    create_tables()
    main()
