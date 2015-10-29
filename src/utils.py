__author__ = 'koba'
import logging
import datetime
import re
import base64
import pytesseract
import time
from io import BytesIO

import pycurl
from PIL import Image
from grab import Grab
from urllib.parse import urlencode
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from .config import PUSH_ID, PUSH_KEY, DB_URL

item_phone_pattern = re.compile('avito.item.phone =.*?</script>')
item_phone_strip_noise = re.compile(r"\\'")
avito_pattern = re.compile('[0-9a-f]+')
strip_image = re.compile(r'{"image64":"data:image/png;base64,(.*)"}')

MONTHS = (
    'января',
    'февраля',
    'марта',
    'апреля',
    'мая',
    'июня',
    'июля',
    'августа',
    'сентября',
    'октября',
    'ноября',
    'декабря'
)


def get_avito_phone_url(body, id):
    text = item_phone_pattern.search(str(body)).group(0)
    splits = item_phone_strip_noise.split(text)
    item_phone = splits[1]
    split = re.findall(avito_pattern, item_phone)
    key = ''.join(split) if int(id) % 2 else ''.join(split[::-1])
    res = ''.join([key[x:x + 1] for x in range(0, len(key)) if not x % 3])
    return 'http://www.avito.ru/items/phone/{}?pkey={}'.format(id, res)


def get_avito_phone_image(url,ref_url):
    g = Grab()
    g.setup(headers={'X-Requested-With': 'XMLHttpRequest', 'Referer': ref_url}, url=url)
    g.request()

    m = strip_image.search(str(g.doc.body))
    image = Image.open(BytesIO(base64.b64decode(m.group(1))))
    return image


def get_avito_phone_number(body, id, ref_url):
    try:
        url = get_avito_phone_url(body, id)
        im = get_avito_phone_image(url,ref_url)

        im = im.resize((im.size[0] * 4, im.size[1] * 4), Image.ANTIALIAS)
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, im)

        phone = re.sub(r'[^\d]', '', pytesseract.image_to_string(bg))
    except AttributeError:
        phone = ''
    return phone


def get_avito_date(date):
    dates = date.split(' ')

    today = datetime.date.today()
    current_year = today.strftime('%Y ')

    if dates[0] == 'Сегодня':
        dates[0] = today.strftime('%d %m')
    elif dates[0] == 'Вчера':
        dates[0] = (today - datetime.timedelta(days=1)).strftime('%d %m')
    else:
        dates[1] = str(MONTHS.index(dates[1]) + 1)

    return datetime.datetime.strptime(current_year + ' '.join(dates), '%Y %d %m %H:%M')


def get_irr_date(date):
    dates = date.split(' ')
    today = datetime.date.today()
    current_year = today.strftime('%Y ')
    if dates[0] == 'Сегодня,':
        dates[0] = today.strftime('%d %m')
        return datetime.datetime.strptime(current_year + ' '.join(dates), '%Y %d %m %H:%M')

    else:
        dates[1] = str(MONTHS.index(dates[1]) + 1)
        return datetime.datetime.strptime(current_year + ' '.join(dates), '%Y %d %m')


def send_notifications(ads):
    post_data = {
        'type': 'self',
        'id': PUSH_ID,
        'key': PUSH_KEY
    }
    for ad in ads:
        c = pycurl.Curl()
        c.setopt(c.URL, 'https://pushall.ru/api.php')
        post_data.update(ad)
        postfields = urlencode(post_data)
        c.setopt(c.POSTFIELDS, postfields)
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(pycurl.SSL_VERIFYHOST, 0)
        c.perform()
        c.close()
        time.sleep(3)


def run(bots=(), debug=False):
    if not (PUSH_ID and PUSH_KEY):
        raise Exception('You need to define ID and Key of your pushall account')
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)

    for bot, options in bots:
        try:
            session = Session()
            options['session'] = session
            spider = bot(**options)
            spider.run()
            send_notifications(spider.ads)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

