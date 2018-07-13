# -*- coding: utf-8 -*-

import re
import requests
import sys
import os
import json
import gettext

from cryptography.fernet import Fernet
from telebot import types

from pysmart.smart_api import PySmart
from secret import generator


# smart API
smart_api = PySmart()


def set_language(language):
    path = get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    return _


# func which encrypt sring.
def encrypt_string(string_, cipher_key):
    # Encode string.
    encode_string_ = string_.encode('utf-8')

    # Make obj and encrypt string.
    cipher = Fernet(cipher_key)
    encrypted_string = cipher.encrypt(encode_string_)

    return encrypted_string


def decrypt_string(string_, cipher_key):
    # Decrypt string.
    cipher = Fernet(cipher_key)
    decrypted_string = cipher.decrypt(string_)

    # Decode string.
    decoded_string = decrypted_string.decode('utf-8')

    return decoded_string


# # #!!!!!! ДОБАВИТЬ ЕЩЕ ПРОВЕРКУ НА СПЕЦИАЛЬНАЫЕ СИМВОЛЫ В РЕГУЛЯРКАХ!!!!!!
# func which check on valid recepient id
# # # Почитать подробнее про re.LOCALE и re.UNICODE и вообще про локал.
def check_recipient_id(recipient_id):
    pattern = re.compile(r'S[a-zA-z0-9]{33}')
    result = re.search(pattern, recipient_id)
    len_rec_id = len(recipient_id)

    if len_rec_id != 34 or result is None:
        return False


# func which check on valid amount
def check_amount(amount):
    if amount.isdigit() is False or int(amount) < 10 or int(amount) > 100_000:
        result = False

        if result is False:
            try:
                amount = float(amount)

                if amount < 10 or amount > 100_000:
                    return False

            except ValueError:
                return False


# func which check on valid passphrase
def check_passphrase(passphrase):
    try:
        pattern = re.compile(r'[а-яА-Я]')
        result = re.search(pattern, passphrase).group()

        if result is not None:
            return False
    except AttributeError:
        if len(passphrase) < 6:
            return False


# func which delete tab symbols in the begin/end of the string.
def delete_tab_symbols(string_):
    string_ = re.sub("^\s+|\n|\r|\s+$", '', string_)

    return string_


# func that calculate all time period of the all tx's for user (days)
def timestamp(date_now, register_date):
    # проверить требуется ли приведение типов к строке
    days_sum = date_now - register_date
    return str(days_sum.days)


# func which calculates the difference of values (work with int or float values)
def difference_of_values(old_value, new_value):
    if old_value == new_value:
        return new_value
    else:
        result = int(old_value) - int(new_value)

        return result * (-1)


# Get STX (Smartholdem) rate.
def get_rate(currency):
    try:
        response = requests.get('https://api.coinmarketcap.com/v1/ticker/eos/')

        # Get data
        data = response.json()

        sth_price = data[0]['price_' + currency.lower()]

        return sth_price
    except KeyError:
        response = requests.get('https://api.coinmarketcap.com/v1/ticker/eos/' + '?convert=' + currency)

        data = response.json()
        sth_price = data[0]['price_' + currency.lower()]

        return sth_price


# Func which generate and return partner link
# telegram.me/STX_BRO_BOT?start= /// Добавить это в секции сервис
def generate_partner_link(user_id):
    digits_mix = generator.shuffle_digits(range_=2)
    s_b_mix = generator.shuffle_s_and_b(range_=2)
    partner_link = str(user_id) + digits_mix + s_b_mix.lower() + "Affiliate"

    return partner_link


# Get affiliate symbols
def get_affiliate_symbols(affiliate_link):
    symbols = affiliate_link.split()

    return symbols[1]


# Get path to the directory with project + locales
def get_path():
    path = sys.argv[0]
    path = os.path.join(os.path.dirname(path), 'locales')

    return path


# Funk which check value named (fee or price) and return value + value name.
# [CORRECT] Доработать минимальные значения.
# [BUG] Не работают целые числа.
def get_fee_or_price(value):
    # Check on value is digit and value len < 4.
    if value.isdigit() is True and len(value) < 4:
        val = 'price'

        return value, val

    else:
        try:
            # Check on float value (without %) and value len < 7.
            if float(value) and len(value) < 7:
                val = 'price'

                return value, val
        except ValueError:
            # Check on digit value with % in the end of str.
            pattern = re.compile(r'[0-8][%]')

            try:
                value = re.match(pattern, value).group()

                split_list = value.split('%')
                val = 'fee'

                return split_list[0], val

            except AttributeError:
                # If value is float and have % in the end of str.
                pattern = re.compile(r'[0-7]\.[0-9]{1,2}[%]')

                # Check on more than 2 digits after '0'.
                try:
                    result = re.match(pattern, value).group()
                except AttributeError:
                    return False

                split_list = result.split('%')
                val = 'fee'

                return split_list[0], val


# Func which ejecting abbreviation from string and return it or return False.
def eject_abbreviation(string_):
    pattern = re.compile(r'[A-Z]{3,4}')

    try:
        result = re.search(pattern, string_).group()
    except AttributeError:
        return False

    return result


# Func which create markup menu from list of values.
def create_menu(list_of_values, *args):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

    menu_items = []

    [menu_items.append(types.KeyboardButton(value)) for value in list_of_values]

    [menu_items.append(arg) for arg in args if args]

    markup.add(*menu_items)

    return markup


# Func which create inline menu from list of texts and ad's uuid. (Need to create ads inline menu).
# [ADD] Дописать генератор списка.
def generate_my_ads_inl_menu(ads_list):
    markup = types.InlineKeyboardMarkup()

    row = []

    row.append(types.InlineKeyboardButton('🌕 Начать торговлю', callback_data='start_trade'))
    markup.row(*row)

    row = []

    [row.append(types.InlineKeyboardButton(ad[0], callback_data=ad[1]))
     for ad in ads_list]

    [markup.row(ad) for ad in row]

    row = []

    row.append(types.InlineKeyboardButton('◀️ Назад', callback_data='back_to_ex'))
    row.append(types.InlineKeyboardButton('📝 Добавить объявление', callback_data='add_ad'))

    markup.row(*row)

    return markup


# Func which creating buy sell inline menu.
# [ADD] Проверять на значение None в одном из ключей.
def generate_inl_menu(list_, dict_=None, **kwargs):
    markup = types.InlineKeyboardMarkup()

    row = []
    non_zero_values = []

    if dict_ is not None:
        for key in dict_.keys():

            text = '✅️️ ' + key + ' ({})'.format(dict_.get(key))
            row.append(types.InlineKeyboardButton(text=text, callback_data=key))

    else:
        for kwarg in kwargs.keys():
            value = kwargs.get(kwarg)

            if value != 0:
                non_zero_values.append(kwarg)
                text = kwarg + ' ({})'.format(kwargs.get(kwarg))
                row.append(types.InlineKeyboardButton(text=text, callback_data=kwarg))

    [markup.row(ad) for ad in row]

    row = []

    row.append(types.InlineKeyboardButton(list_[0], callback_data=list_[1]))

    markup.row(*row)

    return markup, non_zero_values


# Func which make ads list from mongo's db document data.
def make_ads_list(ad_document):

    list_of_ads = []

    # Add ads data from db obj to list.
    for item in ad_document:
        payment_method = item['ad_payment_method']

        # Fiat ad.
        if payment_method == 'FIAT':
            ad_type = item['ad_type']
            ad_amount = item['ad_amount'] + ' ' + 'STH'
            ad_price = item['ad_price'] + ' ' + item['ad_fiat_payment_currency']
            ad_fiat_payment_method = item['ad_fiat_payment_method']
            ad_status = item['ad_status']
            ad_uuid = item['uuid']

            ad_text = '{0} | {1} | {2} ({3}) | [{4}]  💫 '\
                .format(ad_type, ad_amount, ad_price, ad_fiat_payment_method, ad_status)

            list_of_ads.append([ad_text, ad_uuid])

        else:
            # Crypto ad.
            ad_type = item['ad_type']
            ad_amount = item['ad_amount'] + ' ' + 'STH'
            ad_price = item['ad_price'] + ' ' + item['ad_payment_method']
            ad_status = item['ad_status']
            ad_uuid = item['uuid']

            ad_text = '{0} | {1} | {2} | [{3}] 💫 '.format(ad_type, ad_amount, ad_price, ad_status)

            list_of_ads.append([ad_text, ad_uuid])

    return list_of_ads


# Func which remove duplicates payment methods such as btc, eth, doge, fiat.
def remove_duplicate_payment_methods(ads_document):
    # Payment methods list.
    payment_method_list = ['Bitcoin (BTC)', 'Ethereum (ETH)', 'Dogecoin (DOGE)', 'FIAT']

    current_payment_methods = []

    # Append payment methods in new list.
    [current_payment_methods.append(ad['ad_payment_method']) for ad in ads_document]

    # Delete duplicate methods from original list.
    [payment_method_list.remove(method) for method in current_payment_methods]

    return payment_method_list


# Check user's fiat payment currency on valid.
def check_fiat_payment_currency(value):
    pattern = re.compile(r'RUB|USD|EUR')

    try:
        match = re.fullmatch(pattern, value).group()
    except AttributeError:
        return None

    return match


# Func which get dicts from lists, find re template from ad_payment method and update 'ad_payment_method'
# (ejecting abbreviation) and return updated list of ad's dict/s.
def update_ad_payment_method(list_of_dicts):
    if list_of_dicts:
        pattern = re.compile(r'[A-Z]{3,4}')

        for dict_ in list_of_dicts:
            payment_method = dict_.get('ad_payment_method')

            if payment_method != 'FIAT':
                try:
                    result = re.search(pattern, payment_method).group()

                    abbreviation = eject_abbreviation(result)
                    dict_['ad_payment_method'] = abbreviation
                except AttributeError:
                    return False

        return list_of_dicts


# Func which creating inline ad edit menu.
def create_inline_ad_edit_menu(list_of_buttons):
    markup = types.InlineKeyboardMarkup()

    row = []

    count = 0

    for btn in list_of_buttons:
        row.append(types.InlineKeyboardButton(btn[0], callback_data=str(btn[1])))

        count += 1

        if len(row) == 2:
            markup.row(*row)
            row = []

            del list_of_buttons[:(count - 2)]
            count = 0

    return markup


# Func which check on valid limits of user's message.
def check_limits(limits):
    if re.search(r'-', limits) is not None:
        limits = "".join(limits.split())
        limits_list = limits.split('-')

        # Check on valid limit values.
        for limit in limits_list:
            if limit.isdigit() is False:
                try:
                    float(limit)
                except ValueError:
                    return False

        # Check min max value.
        if float(limits_list[0]) > float(limits_list[1]):
            return '>'

    else:
        return False


# Func which checking crypto address on valid. If valid return address , else return None.
def check_crypto_address(payment_method, address):
    btc_pattern1 = re.compile(r'1\w{33}$')
    btc_pattern2 = re.compile(r'\w{42}$')
    eth_pattern = re.compile(r'0x\w{40}$')
    doge_pattern = re.compile(r'D\w{20,50}')    # [ADD] прочекать все таки адреса и найти точные длины.

    patterns_dict = {'BTC': [btc_pattern1, btc_pattern2], 'ETH': eth_pattern, 'DOGE': doge_pattern}

    patterns = [patterns_dict.get(key) for key in patterns_dict.keys() if key == payment_method]

    try:
        result = None

        for pattern in patterns[0]:
            match = re.match(pattern, address)

            if match is not None:
                result = match
    except TypeError:
        result = re.match(patterns[0], address)

    if result is not None:
        return result


# Func which get list of ads and return formatted list of ads.
def format_list(list_of_ads, flag=None):
    list_ = []

    for ad in list_of_ads:
        for key in ad.keys():
            values = ad.get(key)

            if values:
                for value in values:
                    if flag is not None:
                        list_.append([value['ad_fiat_payment_method'], value['ad_price'], len(values)])

                    else:
                        list_.append([key, value['ad_price'], len(values)])

    return list_


# Func which return duplicate ads by cycle.
def get_same_ads(list_of_ads, payment_methods):
    if len(list_of_ads) == 1:
        return list_of_ads

    else:
        list_of_same_ads = []

        for ad in list_of_ads:
            if ad[0] in payment_methods:
                try:
                    if ad[0] == list_of_same_ads[0][0]:
                        list_of_same_ads.append(ad)
                except IndexError:
                    list_of_same_ads.append(ad)

        return list_of_same_ads


# Func which get ads list and return one ad with min price.
def find_min_price(ads_list):
    price_list = []

    [price_list.append([ad[1]]) for ad in ads_list]

    min_price = min(price_list)

    return [ads_list[0][0], min_price[0], ads_list[0][2]]


# Func which remove duplicate ads from main list of all ads.
def remove_duplicate_ads(list_of_ads, payment_method):
    new_list = []

    [new_list.append(ad) for ad in list_of_ads if ad[0] != payment_method]

    return new_list


# Create inline menu of list of ads (btc, min_price, count).
# Using in output when user want to buy/sell coins by crypto/fiat.
def create_inline_menu(list_of_ads, flag=None, pagination=False):
    callback_data = 'back_to_crypto_fiat_list'

    markup = types.InlineKeyboardMarkup()

    row = []

    for ad in list_of_ads:

        if flag is None:
            abbreviation = eject_abbreviation(ad[0])
            ad_text = '{} {} ({})'.format(ad[0], (ad[1] + ' ' + abbreviation), ad[2])

        elif flag == 'currency':
            abbreviation = None

            currency_dict = {'RUB': 'руб.', 'USD': '$', 'EUR': '€'}

            for key in currency_dict.keys():
                if key == ad[0]:
                    abbreviation = currency_dict.get(key)

            ad_text = '{} {} ({})'.format(ad[0], (ad[1] + ' ' + abbreviation), ad[2])

        else:
            currency_dict = {'RUB': 'руб.', 'USD': '$', 'EUR': '€'}

            currency = currency_dict[flag]
            callback_data = 'fiat'

            ad_text = '{} {} ({})'.format(ad[0], (ad[1] + ' ' + currency), ad[2])

        row.append(types.InlineKeyboardButton(ad_text, callback_data=ad[0]))

    [markup.row(ad) for ad in row]

    row = []

    if pagination is False:
        row.append(types.InlineKeyboardButton('Назад', callback_data=callback_data))
    else:
        row.append(types.InlineKeyboardButton('⬅️', callback_data='previous_block_payment_methods'))
        row.append(types.InlineKeyboardButton('Назад', callback_data='fiat'))
        row.append(types.InlineKeyboardButton('➡️', callback_data='next_block_payment_methods'))

    markup.add(*row)

    return markup


# Func which format ads , such as bitcoin ads or etc.
def format_ads_list(items_list):
    formatted_list = []

    for item in items_list:
        price = item['ad_price']

        try:
            payment_method = item['ad_fiat_payment_method']
        except KeyError:
            payment_method = item['ad_payment_method']

        limits = item['ad_amount']
        username = item['username']
        uuid = item['uuid']

        formatted_list.append([payment_method, price, limits, username, uuid])

    return formatted_list


# Func which sorts ads by price in ascending order.
def sort_list_items(list_of_items, position=1):
    return sorted(list_of_items, key=lambda x: x[position])


# Func which create markup for ads , such as bitcoin ads or etc.
def create_ads_markup(list_of_ads, currency=None, pagination=False):
    markup = types.InlineKeyboardMarkup()

    currency_dict = {'RUB': 'руб.', 'USD': '$', 'EUR': '€'}
    callback_data = None

    row = []

    for ad in list_of_ads:
        try:
            abbreviation = currency_dict[currency]
            callback_data = currency
        except KeyError:
            abbreviation = eject_abbreviation(ad[0])
            callback_data = 'crypto'

        ad_text = '{} ({}) {}'.format((ad[1] + ' ' + abbreviation), ('Vol. ' + ad[2] + ' STH'), ('@' + ad[3]))

        row.append(types.InlineKeyboardButton(ad_text, callback_data=('view' + '_' + ad[4])))

    [markup.row(ad) for ad in row]

    row = []

    if pagination is False:
        row.append(types.InlineKeyboardButton('Назад', callback_data=callback_data))

    else:
        if callback_data == currency:
            callback_data = 'fiat'

        row.append(types.InlineKeyboardButton('⬅️', callback_data='previous_block' + '_' + callback_data))
        row.append(types.InlineKeyboardButton('Назад', callback_data=callback_data))
        row.append(types.InlineKeyboardButton('➡️', callback_data='next_block' + '_' + callback_data))

    markup.add(*row)

    return markup


# Create markup with pagination.
def create_ads_markup_with_pagination(list_of_ads, currency=None, index=0, flag=None):
    block = []

    [block.append(block_of_ads) for block_of_ads in list_of_ads[index]]

    # Check flag. Need for pagination.
    if flag is not None:
        markup = create_inline_menu(block, flag=currency, pagination=True)
    else:
        markup = create_ads_markup(block, currency=currency, pagination=True)

    return markup


# Func which serialize data into json.
def serialize_json(data):
    return json.dumps(data)


# Func which deserialize json to data.
def deserialize_json(data):
    return json.loads(data)


# Func which ejecting payment method from call.data (Need for pagination)
def eject_payment_method(data):
    payment_method = data.split('_')

    return payment_method[2]


# Create inline ad view menu.
def create_inline_menu2(callback_data):
    markup = types.InlineKeyboardMarkup()

    row = []

    row.append(types.InlineKeyboardButton('Назад', callback_data=callback_data))
    markup.add(*row)

    return markup