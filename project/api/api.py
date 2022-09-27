
import logging
import requests

from flask import Flask
from datetime import datetime
from bs4 import BeautifulSoup

from project.db.access_database import AccessDataBase


DOMAIN = 'https://www.lucernefestival.ch'
URL = f'{DOMAIN}/en/tickets/program'
EVENT_CLASS = "event-list"
PRICES_CLASS = "prices"
TITLE_CLASS = "event-title"
IMAGE_CLASS = "event-image-link"

SEC = 00
YEAR = 2022

def extract_artists(title):
    if not title:
        return []

    txt = ' '.join(title.split())
    artists = txt.split(' | ')
    artists.pop(0)
    return artists

def extract_dt_venue(el):
    if not el:
        return None, ''

    txt = ' '.join(el[0].parent.text.split())

    date, time, venue = txt.replace('Date and Venue', '').split(' | ')
    date = date.split('.')
    day = date[0].split(' ')[-1]
    month = date[1]
    time = time.split('.')
    hour = time[0]
    min = time[1].split(' /')[0]
    dt_str = f'{day}/{month}/{YEAR} {hour}:{min}:{SEC}'
    dt_obj = datetime.strptime(dt_str, "%d/%m/%Y %H:%M:%S")

    return dt_obj, venue

def extract_works(el):
    if not el:
        return []

    txt = ' '.join(el[0].parent.text.split())
    return txt.replace('Program', '').split(' | ')

def extract_price(el):
    if not el:
        return 0

    txt = ' '.join(el[0].text.split())
    price = txt.split(' ')[-1]
    try:
        price = int(price)
    except ValueError as e:
        price = 0
    return price

def init_app(app: Flask):
    @app.route('/')
    def init_database():
        dbobj = AccessDataBase(True)
        all_events = dbobj.get_events()
        data = {
            'all_events_counts': len(all_events),
            'all_events': all_events,
        }
        logging.info(f'DATABASE_INITIALISED WITH:  {data}')
        return data


    @app.route('/crawl_events/', methods=['POST'])
    def crawl_events():
        resp = requests.get(URL)
        soup = None
        events = []
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "lxml")
            events_elements = soup.select(f'ul[class^={EVENT_CLASS}]')
            for litag in events_elements[0].find_all('li'):
                event = {}

                title_element = litag.find_all("p", {"class": TITLE_CLASS})
                event['title'] = ' '.join(title_element[0].text.split())
                event['artists'] = extract_artists(event['title'])

                dt_venue_el = litag.find_all("strong", string="Date and Venue")
                dt, venue = extract_dt_venue(dt_venue_el)
                event['datetime'] = dt
                event['venue'] = venue

                program_el = litag.find_all("strong", string="Program")
                works = extract_works(program_el)
                event['works'] = works

                image_el = litag.find_all("a", {"class": IMAGE_CLASS}, href=True)
                href = image_el[0]['href']
                event['image_link'] = f'{DOMAIN}{href}'

                prices_el = litag.find_all("div", {"class": PRICES_CLASS})
                event['starting_price'] = extract_price(prices_el)

                events.append(event)

        dbobj = AccessDataBase()
        for event in events:
            dbobj.insert_event_in_db(event)

        data = { 'total_events_set_in_db': len(events) }
        logging.info(f'TOTAL_EVENTS_SET_IN_DATABASE:  {data}')
        return data


    @app.route('/get_events_in_db/')
    def get_events():
        dbobj = AccessDataBase()
        all_events = dbobj.get_events()
        data = {
            'all_events_counts': len(all_events),
            'all_events': all_events,
        }
        logging.info(f'SUCCESSFULLY GET EVENTS:  {data}')
        return data
