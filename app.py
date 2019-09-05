import json
import logging
import tkinter as tk
from collections import defaultdict
from datetime import datetime
from tkinter import messagebox

import click
import requests
import tldextract
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
    domain_name = CharField()
    tags = TextField()
    updatedAt = DateTimeField()


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

        results = defaultdict(int)
        for tag in soup.findAll():
            results[tag.name] = len(soup.findAll(tag.name))

        t.close()

    except requests.exceptions.InvalidURL:
        logging.error("Invalid url")
        return None
    except requests.exceptions.ConnectionError:
        logging.error("Connection error")
        return None

    logging.info("Save to DB...")
    with db.atomic():
        dumps = str(json.dumps(results))
        extract = tldextract.extract(url)
        name = str(extract.domain)
        try:
            tag = Tag.create(
                url=url,
                domain_name=name,
                tags=dumps,
                updatedAt=datetime.now()
            )
        except IntegrityError:
            tag = Tag.update(
                url=url,
                domain_name=name,
                tags=dumps,
                updatedAt=datetime.now()
            )

    result = parse_dict_to_string(results)

    return result


def parse_dict_to_string(results):
    result = ''
    for elem in sorted(results.items(), key=lambda x: x[1], reverse=True):
        result += elem[0] + ":\t" + str(elem[1]) + "\n"
    return result


def get_tags_num_from_db(url):
    url = get_full_url(url)

    logging.info("Load from DB...")
    try:
        tag = Tag.get(url=url)
        tags = json.loads(tag.tags.encode())

        result = parse_dict_to_string(tags)

        return result

    except Tag.DoesNotExist:
        logging.error("Can't load from DB...")
        return None


# gui
master = tk.Tk()

canvas = tk.Canvas(master, width=400, height=800)
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

    tag_result = get_tags_num_from_db(url)
    if tag_result is not None:
        result_label['text'] = 'Result from db: \n ' + tag_result
        return

    tag_result = get_tags_num(url)
    if tag_result is None:
        messagebox.showinfo("Error", "Invalid URL")
        return

    result_label['text'] = 'Result: ' + tag_result


# buttons
get_button = tk.Button(text='Calculate tags', command=on_calculate_click)
canvas.create_window(200, 180, window=get_button)

# result label
result_label = tk.Label(master, text='')
canvas.create_window(200, 540, window=result_label)


# CLI
def _get(url):
    tags_result = get_tags_num(url)

    if tags_result is None:
        print('Error: Check URL and internet connection')
        return

    print('Result:\n', tags_result)
    pass


def _view(url):
    tags_result = get_tags_num_from_db(url)

    if tags_result is None:
        print('Error: URL is not found in DB')
        return

    print('Result from DB:\n', str(tags_result))
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
