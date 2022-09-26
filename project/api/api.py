from datetime import datetime
from math import ceil

from flask import Flask, request, render_template, redirect

from project.db.access_database import AccessDataBase

import logging
import requests
from bs4 import BeautifulSoup

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
    def home():
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
            logging.info(f'PPPPPPPPPPPPP {events}')
        return redirect('/messages/1/')

    @app.route('/messages/<int:page_id>/', methods=['GET'])
    def get_messages(page_id):
        dbobj = AccessDataBase()
        kwargs = {
            'message_length_by_3': ceil(dbobj.get_message_length()/3),
            'messages': dbobj.get_messages(page_id),
            'title': 'Home | CRUD'
        }
        if kwargs['messages']: return render_template('home.jinja2', **kwargs)
        else: return render_template('error.jinja2', title='CRUD | NOT FOUND'), 404

    # @app.route('/message/create/', methods=['GET', 'POST'])
    # def insert_message():
    #     try:
    #         dbobj = AccessDataBase()
    #         if request.method == 'POST':
    #             message_json = {}
    #             message_json['message_title'] = request.form['title'].strip().\
    #                 replace('<', '').replace('>', '').replace('\'', '\'\'')
    #             message_json['author_name'] = request.form['author'].strip().\
    #                 replace('<', '').replace('>', '').replace('\'', '\'\'')
    #             message_json['message_text'] = request.form['message'].strip().\
    #                 replace('<', '').replace('>', '').replace('\'', '\'\'')
    #             if any(len(field)==0 for field in message_json.values()):
    #                 warning = 'It must not have field blank'
    #                 return render_template('create.jinja2', warning=warning, title='CREATE | CRUD')
    #             if dbobj.get_message_by_condition(['message_title', message_json['message_title']]):
    #                 warning = 'Already exist message called ' + message_json['message_title']
    #                 return render_template('create.jinja2', warning=warning, title='CREATE | CRUD')
    #             if len(message_json['message_title'])>30:
    #                 warning = 'Title must not have more than 30 character'
    #                 return render_template('create.jinja2', warning=warning, title='CREATE | CRUD')
    #             if len(message_json['author_name'])>30:
    #                 warning = 'Author must not have more than 30 character'
    #                 return render_template('create.jinja2', warning=warning, title='CREATE | CRUD')
    #             if len(message_json['message_text'])>200:
    #                 warning = 'Message must not have more than 200 character'
    #                 return render_template('create.jinja2', warning=warning, title='CREATE | CRUD')
    #             message_json['creation_date'] = str(datetime.now().date())

    #             dbobj.insert_message(message_json)
    #             created_now = dbobj.get_messages()[-1][0]
    #             return redirect(f'/message/{created_now}')
    #         else:
    #             return render_template('create.jinja2', title='CREATE | CRUD')
    #     except:
    #         return render_template('error.jinja2', title='SERVER ERROR | CRUD', warning='SERVER ERROR'), 500

    # @app.route('/message/update/<int:message_id>/', methods=['GET', 'POST'])
    # def update_message(message_id):
    #     try:
    #         dbobj = AccessDataBase()
    #         db_info = dbobj.get_message_by_condition(['message_id', message_id])
    #         message = [item for item in db_info]
    #         message[4] = '/'.join(str(message[4]).split('-')[::-1])

    #         if request.method == 'POST':
    #             message_json = {}
    #             message_json['message_title'] = request.form['title'].strip().\
    #                 replace('<', '').replace('>', '').replace('\'', '\'\'')
    #             message_json['author_name'] = request.form['author'].strip().\
    #                 replace('<', '').replace('>', '').replace('\'', '\'\'')
    #             message_json['message_text'] = request.form['message'].strip().\
    #                 replace('<', '').replace('>', '').replace('\'', '\'\'')

    #             if  all(len(field)==0 for field in message_json.values()):
    #                 warning = 'One of them must be filled in'
    #                 return render_template('update.jinja2', message=message, warning=warning)
    #             if dbobj.get_message_by_condition(['message_title', message_json['message_title']]):
    #                 warning = 'Already exist message called ' + message_json['message_title']
    #                 return render_template('update.jinja2', message=message, warning=warning)
    #             if message_json['message_title']:
    #                 if len(message_json['message_title'])>30:
    #                     warning = 'Title must not have more than 30 character'
    #                     return render_template('update.jinja2', message=message, warning=warning)
    #                 args = ['message_title', message_json['message_title']]
    #                 dbobj.update_message(message_id, args)
    #             if message_json['author_name']:
    #                 if len(message_json['author_name'])>30:
    #                     warning = 'Author must not have more than 30 character'
    #                     return render_template('update.jinja2', message=message, warning=warning)
    #                 args = ['author_name', message_json['author_name']]
    #                 dbobj.update_message(message_id, args)
    #             if message_json['message_text']:
    #                 if len(message_json['message_text'])>200:
    #                     warning = 'Message must not have more than 200 character'
    #                     return render_template('update.jinja2', message=message, warning=warning)
    #                 args = ['message_text', message_json['message_text']]
    #                 dbobj.update_message(message_id, args)
    #             return redirect(f'/message/{message_id}/')
    #         else:
    #             return render_template('update.jinja2', message=message, title=f'UPDATE | {message[1]}') if message \
    #                 else render_template('error.jinja2', title='NOT FOUND | CRUD', warning='NOT FOUND'), 404
    #     except:
    #         return render_template('error.jinja2', title='SERVER ERROR | CRUD', warning='SERVER ERROR'), 500

    # @app.route('/message/<int:message_id>/', methods=['GET', 'POST'])
    # def access_message(message_id):
    #     dbobj = AccessDataBase()
    #     db_info = dbobj.get_message_by_condition(['message_id', message_id])
    #     message = [item for item in db_info]
    #     message[4] = '/'.join(str(message[4]).split('-')[::-1])
    #     return render_template('see.jinja2', message=message, title=f'SEE | {message[1]}')


    # @app.route('/message/remove/<int:message_id>/', methods=['POST'])
    # def delete_message(message_id):
    #     dbobj = AccessDataBase()
    #     dbobj.remove_message(message_id)
    #     return redirect('/messages/1/')


    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.jinja2', title='CRUD | NOT FOUND', warning=error), 404


    @app.errorhandler(500)
    def server_error(error):
        return render_template('error.jinja2', title='CRUD | NOT FOUND', warning=error), 500
