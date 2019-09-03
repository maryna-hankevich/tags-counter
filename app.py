import tkinter as tk
from tkinter import messagebox

import click
import requests
from bs4 import BeautifulSoup
from peewee import *

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
def get_tags_num(url):
    try:
        response = requests.get(url)
        open('./response.html', 'wb').write(response.content)
        soup = BeautifulSoup(open('./response.html'), "html.parser")
        tags_num = len(soup.find_all())

    except requests.exceptions.InvalidURL:
        return None
    except requests.exceptions.ConnectionError:
        return None

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
    try:
        tag = Tag.get(url=url)
        return tag.count
    except Tag.DoesNotExist:
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
    if not url.lower().startswith("http"):
        messagebox.showinfo("Error", "URL should start from 'http'")
        return

    tags_num = get_tags_num(url)
    if tags_num is None:
        messagebox.showinfo("Error", "Invalid URL")
        return

    result_label['text'] = 'Result: ' + str(tags_num)


def on_get_from_db_click():
    url = url_entry.get()
    if not url.lower().startswith("http"):
        messagebox.showinfo("Error", "URL should start from 'http'")
        return

    tags_num = get_tags_num_from_db(url)
    if tags_num is None:
        result_label['text'] = 'Result not Found in DB'
    else:
        result_label['text'] = 'Result from DB: ' + str(tags_num)


# buttons
get_button = tk.Button(text='Calculate tags', command=on_calculate_click)
canvas.create_window(200, 180, window=get_button)
view_button = tk.Button(text='Get from DB', command=on_get_from_db_click)
canvas.create_window(200, 210, window=view_button)

# result label
result_label = tk.Label(master, text='')
canvas.create_window(200, 240, window=result_label)


# CLI
def _get(url):
    if not url.lower().startswith("http"):
        print("Error: URL should start from 'http'")
        return

    tags_num = get_tags_num(url)

    if tags_num is None:
        print('Error: Check URL and internet connection')
        return

    print('Result: ', tags_num)
    pass


def _view(url):
    if not url.lower().startswith("http"):
        print("Error: URL should start from 'http'")
        return

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
