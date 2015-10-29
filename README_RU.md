Данный модуль предназначен для удобного отслеживания объявлений - он просматривает необходимые сайты на наличие новых объявлений, и, если есть подходящее, отправляет пуш сообщения (используя сервис pushall.ru) пользователю. В данный момент реализованы сайты avito и irr, но при необходимости можно легко расширить функционал и на другие.

В качестве основного фреймворка используется Grab, для работы с бд - SQLAlchemy и alembic, для автозапуска пауков - apscheduler. Так же используется pytesseract для распознавания номеров с авито.

Для начала работы нужно зарегистрироваться на сайте [pushall.ru](https://pushall.ru) и ввести полученные данные (id  и key) в файл config.py, так же можно настроить временные интервалы для сканирования(параметр JOB_INTERVALS)

Имеющиеся пауки настроены на поиск недвижимости в Москве, для других использований требуется:

Перенастроить параметр initial_urls так, чтобы по ссылке выводился список требуемых объявлений.
Если необходимо собирать специфические значения, нужно переписать параметры ad_fields и ad_detail_fields; ad_fields отвечает за поля на странице поиска; если он вернет поле url то загрузится страница, с которой будут собираться поля из ad_detail_fields. Формат параметров - кортеж из списков, в списке должны быть поля 'field' - название поля и 'xpath' - XPath-путь к искомому значению. Так же можно передать название функции в ключе 'callback' - значение поля будет обработано в этой функции, и ключ 'optional' для полей которые могут не иметь значений.

Так же в бд используется таблица spamers для сбора телефонов недобросовестных продавцов, если телефон указанный в объявлении есть в базе - объявление будет проигнорировано. Сбор и запись телефонов лежит на пользователе.

При использовании нерусских IP avito не будет выдавать номер телефона, в данном случае нужно будет использовать прокси. Сам скрипт лучше запускать через supervisor.