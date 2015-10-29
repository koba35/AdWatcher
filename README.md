This module is designed for easy tracking of ads - it looks appropriate sites for new ads, and if there is a suitable ad, sends a push message (using the service pushall.ru) to user. Currently implemented sites are avito and irr, but you can easily extend the functionality to another sites.

As a basic framework this module uses Grab, to work with the database - SQLAlchemy and alembic, to automatically run spiders - apscheduler. Also it uses pytesseract for recognition of phone numbers on Avito.

To get started you need to register on the website [pushall.ru] (https://pushall.ru) and enter the obtained data(id and key) to the file config.py, also you can adjust the scanning time intervals (option JOB_INTERVALS)

Available spiders are configured to search real estate in Moscow, for other uses you should:

Reconfigure option initial_urls to the link that displays a list of the required announcements.
If you want to collect specific values, you need to rewrite the parameters ad_fields and ad_detail_fields; ad_fields is responsible for the field on the search page; if it will return url field script will load  page and search fields specified in ad_detail_fields. Format options - tuple of lists, the list must be the field 'field' - the name of the field and the 'xpath' - XPath-path to the desired value. You can also pass the name of the function key in the 'callback' - the value of the field will be processed in this function, and the key 'optional' for fields that may have no value.

Also in the database exists table spamers, which is used to collect phones from unscrupulous sellers. If the phone is listed in the ad is in db - ad will be ignored. The collection and recording of telephone numbers is the user's responsibility.

When using non-Russian IP avito will not issue a phone number, in this case, you will need to use a proxy. The script is better to run through supervisor.