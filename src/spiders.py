__author__ = 'koba'

import datetime
import re
import base64

from grab.spider import Spider, Task

from .utils import get_avito_phone_number, get_avito_date, get_irr_date
from .models import Core, Spamer


class InvalidAdException(Exception):
    pass


class AdSpider(Spider):
    list_adverts_xpath = None
    ad_fields = None
    ad_detail_fields = None

    def __init__(self, **kwargs):
        self.session = kwargs.pop('session')
        self.dates = []
        self.ads = []
        super(AdSpider, self).__init__(**kwargs)

    def prepare(self):

        instance = self.session.query(Core).filter_by(name=self.__class__.__name__).first()
        if not instance:
            start_date = datetime.datetime.now() - datetime.timedelta(hours=1)
            instance = Core(name=self.__class__.__name__, last_visit=start_date)
            self.session.add(instance)

        self.instance = instance
        self.spamers = [spam.phone for spam in self.session.query(Spamer).all()]

    def task_initial(self, grab, task):

        for elem in grab.doc.select(self.list_adverts_xpath):
            try:
                context = self.clean_ad(elem)
                if 'url' in context:
                    yield Task('detail_advert', url=context['url'], context=context)

            except InvalidAdException:
                pass

    def clean_ad(self, elem):
        context = {}

        for fields in self.ad_fields:
            field = fields['field']
            try:
                context[field] = elem.select(fields['xpath'])[0].text()
            except (KeyError, IndexError):
                context[field] = ''
            if 'callback' in fields:
                context[field] = getattr(self, fields['callback'])(context[field])
            if not (context[field] or 'optional' in fields):
                raise InvalidAdException

        return context

    def task_detail_advert(self, grab, task):
        try:
            data = self.clean_ad_detail(grab, task.context)
            self.process_data(data)
        except InvalidAdException:
            pass

    def clean_ad_detail(self, grab, context):
        data = {}
        for fields in self.ad_detail_fields:
            field = fields['field']

            data[field] = grab.doc.select(fields['xpath'])[0].text()
            if 'callback' in fields:
                data[field] = getattr(self, fields['callback'])(data[field])
            if not (data[field] or 'optional' in fields):
                raise InvalidAdException

        context.update(data)
        return context

    def clean_price(self, string):
        return re.sub(r'[^\d]', '', string)

    def clean_date(self, string):
        date = self.get_formatted_date(string)

        if date <= self.instance.last_visit:
            raise InvalidAdException

        self.dates.append(date)
        return string

    def process_data(self, data):
        pass

    def get_formatted_date(self, string):
        return string

    def shutdown(self):
        if self.dates:
            self.instance.last_visit = max(self.dates)


class AvitoSpider(AdSpider):
    initial_urls = ['https://www.avito.ru/moskva/kvartiry/sdam?pmax=30000&pmin=10000&user=1&view=list']
    base_url = 'https://www.avito.ru'
    list_adverts_xpath = '//div[@class="catalog-list clearfix"]/div/div'
    ad_fields = (
        {'field': 'url', 'xpath': 'div[@class="title"]//a/@href'},
        {'field': 'id', 'xpath': 'div[@class="title"]//a/@id'},
        {'field': 'date', 'xpath': 'div[@class="title"]//span[@class="date"]', 'callback': 'clean_date'},
        {'field': 'price', 'xpath': 'div[@class="price"]/p', 'callback': 'clean_price'},
    )
    ad_detail_fields = (
        {'field': 'address', 'xpath': '//span[@id="toggle_map"]'},
        {'field': 'summary', 'xpath': '//h1[@itemprop="name"]'},
        {'field': 'descr', 'xpath': '//div[@id="desc_text"]', 'optional': True},
        {'field': 'name', 'xpath': '//div/strong[@itemprop="name"]', 'optional': True}
    )

    def get_formatted_date(self, string):
        return get_avito_date(string)

    def process_data(self, data):
        ad = {
            'url': self.base_url + data['url'],
            'title': '{}, {} руб'.format(data['address'], data['price']),
            'text': '{}\n{}\n{}\n{} {}'.format(data['summary'], data['date'], data['descr'], data['phone'],
                                               data['name'])
        }
        self.ads.append(ad)

    def clean_ad_detail(self, grab, context):
        data = super(AvitoSpider, self).clean_ad_detail(grab, context)

        phone = get_avito_phone_number(grab.doc.body, context['id'], context['url'])

        if len(phone) == 11:
            phone = phone[1:]

        if phone in self.spamers:
            raise InvalidAdException

        data['phone'] = phone
        return data


class IRRSpider(AdSpider):
    initial_urls = ['http://irr.ru/real-estate/rent/search/rooms=1/list=list/sort/date_sort:desc/']
    base_url = 'http://irr.ru/'
    list_adverts_xpath = '//div[@class="adds_cont clear productGrid"]/a'
    ad_fields = (
        {'field': 'url', 'xpath': '@href'},
        {'field': 'date', 'xpath': 'div//div[@class="productPostDate"]', 'callback': 'clean_date'},
        {'field': 'price', 'xpath': 'div//div[@class="productPrice"]', 'callback': 'clean_price'},
    )
    ad_detail_fields = (
        {'field': 'summary', 'xpath': '//h1[@class="productPageName"]'},
        {'field': 'name', 'xpath': '//div[@class="ownerPhoneMainHidden"]/button/@data-contact', 'optional': True},
        {'field': 'descr', 'xpath': '//div[@class="advertDescriptionText"]', 'optional': True},
        {'field': 'phone', 'xpath': '//div[@class="ownerPhoneMainHidden"]/button/@data-phone',
         'callback': 'clean_phone'}
    )

    def clean_phone(self, string):
        phone_string = str(base64.standard_b64decode(string))
        phone = re.sub(r'[^\d]', '', phone_string)

        if len(phone) == 11:
            phone = phone[1:]

        if phone in self.spamers:
            raise InvalidAdException

        return phone_string

    def get_formatted_date(self, string):
        return get_irr_date(string)

    def process_data(self, data):
        ad = {
            'url': self.base_url + data['url'],
            'title': '{} руб'.format(data['price']),
            'text': '{}\n{}\n{}\n{} {}'.format(data['summary'], data['date'], data['descr'], data['phone'],
                                               data['name'])
        }
        self.ads.append(ad)

