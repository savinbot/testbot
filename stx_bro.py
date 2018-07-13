# -*- coding: utf-8 -*-

import datetime
import re
import uuid
import logging
import ssl

from aiohttp import web

import telebot
import utils

from pysmart.smart_api import PySmart
from pymongodb.pymongodb import MongoDB
from memcached.memcached import Memcache
from const import *
from vedisdb import dbworker, config
# from secret import API_TOKEN, WEBHOOK_URL_BASE, WEBHOOK_URL_PATH, WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV, WEBHOOK_LISTEN, \
#     WEBHOOK_PORT, Generator, CIPHER_KEY

from secret import TOKEN, Generator, CIPHER_KEY

# # For webhook.
# logger = telebot.logger
# telebot.logger.setLevel(logging.INFO)
#
# bot = telebot.TeleBot(API_TOKEN)
#
# app = web.Application()
#
#
# # Process webhook calls
# async def handle(request):
#     if request.match_info.get('token') == bot.token:
#         request_body_dict = await request.json()
#         update = telebot.types.Update.de_json(request_body_dict)
#         bot.process_new_updates([update])
#         return web.Response()
#     else:
#         return web.Response(status=403)
#
# app.router.add_post('/{token}/', handle)


# For polling.
bot = telebot.TeleBot(TOKEN)


# Smartholdem API on python
pysmart_api = PySmart()

# Password and partner link generator
generator = Generator()

# # #
pymongodb = MongoDB()

# # #
memcache = Memcache()


# Greeting message
@bot.message_handler(commands=['start'])  # event handler (commands)
def send_welcome(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username

    # Create or update record in database (user's data)
    user_document = pymongodb.find_one_and_update({'user_id': user_id},
                                                  {'first_name': first_name, 'last_name': last_name,
                                                   'username': username}, 'users', '$set')
    pymongodb.finish()

    # Get user's object id
    obj_id = user_document['_id']

    try:
        user_document = pymongodb.find_one_by_id(obj_id, 'users')

        try:
            eval(user_document['date_of_registration'])
        except TypeError:
            pass

    except KeyError:
        #  Generate account for new user
        passphrase = generator.mix()
        address = pysmart_api.create_account(passphrase=passphrase)

        # Encrypt passphrase.
        passphrase = utils.encrypt_string(passphrase, CIPHER_KEY)

        # Generate partner link.
        partner_link = utils.generate_partner_link(user_id)

        # Get affiliate str and insert it into db.
        try:
            affiliate_link = utils.get_affiliate_symbols(message.text)
        except IndexError:
            affiliate_link = None

        # Insert user's data in db
        pymongodb.find_one_and_update_by_id(obj_id, {'date_of_registration': datetime.datetime.now(),
                                                     'address': address, 'passphrase': passphrase, 'balance': 0,
                                                     'timestamp': 0, 'tx_count': 0, 'sum_of_coins': 0,
                                                     'partner_link': partner_link, 'affiliate_link': affiliate_link},
                                            'users', '$set')
        pymongodb.finish()

    # Send bot message.
    bot.send_message(chat_id, text="Select a language in the list. (about input field.)", reply_markup=MARKUP_LANG)

    # Set user's state into db.
    dbworker.set_state(message.chat.id, config.States.S_USE_CHOOSE_LANG.value, config.db_state)


# Func which send menu message , need to exit form other funcs.
@bot.message_handler(commands=['menu'])
def menu_message(message):
    chat_id = message.chat.id

    # Get and set language
    language = dbworker.get_current_state(chat_id, config.db_language)
    _ = utils.set_language(language)

    # Send bot message.
    bot.send_message(chat_id, text=_(MENU_MESSAGE), reply_markup=bot_markup[language]['menu'])

    # Set new user's state.
    dbworker.set_state(message.chat.id, config.States.S_USE_MENU.value, config.db_state)


@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_USE_CHOOSE_LANG.value)
def choose_lang(message):
    first_name = message.from_user.first_name
    message_text = message.text
    chat_id = message.chat.id

    # Check on lang by user's choice.
    if message.text == '🇺🇸 English' or message.text == '🇷🇺 Русский':
        if message_text == '🇺🇸 English':
            # Set lang in db.
            dbworker.set_state(chat_id, 'en', config.db_language)

        elif message_text == '🇷🇺 Русский':
            # Set lang in db.
            dbworker.set_state(chat_id, 'ru', config.db_language)

        # Get and set language.
        language = dbworker.get_current_state(chat_id, config.db_language)
        _ = utils.set_language(language)

        # Send welcome messages.
        bot.send_message(chat_id, text=(_(WELCOME).format(first_name)), parse_mode="HTML",
                         reply_markup=bot_markup[language]['menu'])
        bot.send_message(chat_id, text=_(FEEDBACK), reply_markup=bot_markup[language]['select_currency'])

        # Set new user's state.
        dbworker.set_state(message.chat.id, config.States.S_USE_MENU.value, config.db_state)


# Menu (contains 4 items: wallet, exchange, about, settings)
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_USE_MENU.value)
def menu(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # WALLET
    if message.text.startswith("💼") is True:
        # user_id = message.from_user.id
        # chat_id = message.chat.id

        user_document = pymongodb.find_one({"user_id": user_id}, 'users')
        pymongodb.finish()

        obj_id = user_document['_id']
        address = user_document["address"]
        old_balance = user_document["balance"]
        # language = user_document["lang"]
        new_balance = pysmart_api.get_balance(address=address)

        # Get language.
        language = dbworker.get_current_state(chat_id, config.db_language)

        # Get difference of balances.
        try:
            result = utils.difference_of_values(old_balance, new_balance)
        except TypeError:
            result = 0

        if result != old_balance and result != 0:
            if result > 0:
                # Setting tx count
                tx_count = 0
                tx_count += 1

                balance, inc_sum_of_coins = result, result

                # Incrementing user's data values in db
                pymongodb.find_one_and_update_by_id(obj_id, {"balance": balance, 'sum_of_coins': inc_sum_of_coins,
                                                             'tx_count': tx_count}, 'users', "$inc")
                pymongodb.finish()

            elif result < 0:
                # Setting tx count
                tx_count = 0
                tx_count += 1

                balance, inc_sum_of_coins = result, abs(result)

                # Incrementing user's data values in db
                pymongodb.find_one_and_update_by_id(obj_id, {"balance": balance, 'sum_of_coins': inc_sum_of_coins,
                                                             'tx_count': tx_count}, 'users', "$inc")
                pymongodb.finish()

        # Variables for timestamp func
        date_of_registration = user_document["date_of_registration"]
        date_of_tx = datetime.datetime.now()

        # Calculate difference between date_of_tx and date of registration to set timestamp
        # (timestamp is all time period of the all tx's (days))
        timestamp = utils.timestamp(date_of_tx, date_of_registration)
        pymongodb.find_one_and_update_by_id(obj_id, {"timestamp": timestamp}, 'users', "$set")
        pymongodb.finish()

        # check updated user's data
        user_document = pymongodb.find_one_by_id(obj_id, 'users')
        pymongodb.finish()

        # Get data
        balance = (user_document["balance"] / (10 ** 8))
        sum_of_coins = (user_document["sum_of_coins"] / (10 ** 8))
        tx_count = user_document["tx_count"]
        timestamp = user_document["timestamp"]

        # If user's don't choose currency in manual - set default currency based user's lang choice
        try:
            currency = user_document["currency"]
        except KeyError:
            currency = CURRENCY_DICT[language]

            pymongodb.find_one_and_update_by_id(obj_id, {"currency": currency}, 'users', "$set")
            pymongodb.finish()

        # Get rate only if balance > 0
        equivalent = 0

        if balance > 0:
            # Get STX rate
            rate = utils.get_rate(currency)     # закомментировать и вынести функцию гет рейт в отдельный скрипт.
            equivalent = balance * float(rate)
            equivalent = "{0:.2f}".format(equivalent)

        # Get path and translate.
        path = utils.get_path()

        trans_lang = gettext.translation('base', localedir=path, languages=[language])
        trans_lang.install()

        _ = trans_lang.gettext

        # Format message
        wallet_text = _(WALLET_TEXT).format(balance, timestamp, str(tx_count), str(sum_of_coins), currency, equivalent)

        # Sending message
        bot.send_message(chat_id=chat_id, text=wallet_text, reply_markup=bot_markup[language]['inline_wallet_menu'])

    # EXCHANGE
    elif message.text.startswith("📊") is True:
        # Get data from db.
        user_document = pymongodb.find_one({"user_id": user_id}, 'users')
        pymongodb.finish()

        language = user_document["lang"]

        # Get path and translate message.
        path = utils.get_path()

        trans_lang = gettext.translation('base', localedir=path, languages=[language])
        trans_lang.install()

        _ = trans_lang.gettext

        # Send message
        bot.send_message(chat_id=chat_id, text=EXCHANGE, reply_markup=bot_markup[language]['exchange'])

    # ABOUT SERVICE
    elif message.text.startswith("🚀") is True:
        # # About service
        # Get lang, path and translate bot message.
        user_document = pymongodb.find_one({"user_id": user_id}, 'users')
        pymongodb.finish()

        language = user_document["lang"]

        path = utils.get_path()

        trans_lang = gettext.translation('base', localedir=path, languages=[language])
        trans_lang.install()

        _ = trans_lang.gettext

        # Send message
        bot.send_message(chat_id=chat_id, text=_(ABOUT_SERVICE), reply_markup=bot_markup[language]['service_menu'])

    # SETTINGS
    elif message.text.find("🛠️") is 0:
        # Settings
        # Get lang, path and translate bot message.
        user_document = pymongodb.find_one({"user_id": user_id}, 'users')
        pymongodb.finish()

        language = user_document["lang"]

        path = utils.get_path()

        trans_lang = gettext.translation('base', localedir=path, languages=[language])
        trans_lang.install()

        _ = trans_lang.gettext

        bot.send_message(chat_id=chat_id, text=_(SETTINGS), reply_markup=bot_markup[language]['inl_settings'])


# Callback handler
# стирать данные при нажатии на какую либо из инлайн кнопок
@bot.callback_query_handler(func=lambda call: True)
def call_back_handler(call):
    payment_method = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id

    # Get user's data from db.
    user_document = pymongodb.find_one({"user_id": user_id}, 'users')
    pymongodb.finish()

    obj_id = user_document['_id']
    address = user_document['address']
    partner_link = user_document['partner_link']
    language = user_document['lang']
    currency = user_document['currency']

    # Разобраться , что это за хрень :D
    try:
        exchange = user_document['exchange']
    except KeyError:
        exchange = 'CoinMarketCap'

    # Дописать что тут проиходит!!!!
    mrkp_inl_rate = markup_inline_rate(currency)

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # # Wallet section
    if call.data == 'deposit':
        # Print deposit message and user's address
        bot.send_message(chat_id, text=_(DEPOSIT))
        bot.send_message(chat_id, text=address, reply_markup=bot_markup[language]['menu'])

    elif call.data == 'withdrawal':
        # Set user's choice into db.
        pymongodb.find_one_and_update_by_id(obj_id, {"_choice": payment_method}, 'users', "$set")
        pymongodb.finish()

        # check user's balance (if balance is None - throw exception)
        try:
            balance = float(pysmart_api.get_balance(address=address)) / 100_000_000
        except TypeError:
            balance = 0

        # Check balance. If < 10 block withdrawal , else withdrawal coins.
        if balance < 10:
            bot.send_message(chat_id, (_(WITHDRAWAL).format(balance)), reply_markup=bot_markup[language]['menu'])
        else:
            # Check contacts dict. Clear or not.
            try:
                recipient_id = user_document['contact']
            except KeyError:
                recipient_id = None
                bot.send_message(chat_id=chat_id, text=_(CLEAR_CONTACT_LIST))

            # Check contacts dict. Clear or not.
            if recipient_id is not None:
                # Send bot message.
                bot.send_message(chat_id, text=_(CHOOSE_CONTACT), reply_markup=bot_markup[language]['yes_no'])

                # Set new user's state.
                dbworker.set_state(chat_id, config.States.S_USE_ADDRESS_FROM_CONTACTS.value, config.db_state)

            else:
                # Send bot message.
                bot.send_message(chat_id, text=_(INPUT_RECIPIENT_ID), reply_markup=bot_markup[language]['yes_no'])

                # Set new user's state.
                dbworker.set_state(chat_id, config.States.S_GET_RECIPIENT_ID.value, config.db_state)

    # Safe method for send own coins (data not save in database)
    elif call.data == 'send':
        # Set user's choice into db.
        pymongodb.find_one_and_update_by_id(obj_id, {"_choice": payment_method}, 'users', "$set")
        pymongodb.finish()

        # Check contacts dict. Clear or not.
        try:
            recipient_id = user_document['contact']
        except KeyError:
            recipient_id = None
            bot.send_message(chat_id=chat_id, text=_(CLEAR_CONTACT_LIST))

        # Check contacts dict. Clear or not.
        if recipient_id is not None:
            # Send bot message.
            bot.send_message(chat_id, text=_(CHOOSE_CONTACT), reply_markup=bot_markup[language]['yes_no'])

            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_USE_ADDRESS_FROM_CONTACTS.value, config.db_state)

        else:
            # Send bot message.
            bot.send_message(chat_id, text=_(INPUT_RECIPIENT_ID), reply_markup=bot_markup[language]['yes_no'])

            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_GET_RECIPIENT_ID.value, config.db_state)

    # # EXCHANGE SECTION.
    # Check on inl button my announcements.
    elif call.data == 'my_announcements':
        # Get list of ads from db.
        ad_document = pymongodb.find({"user_id": user_id}, 'ads')
        pymongodb.finish()

        # If user have ads.
        if ad_document:
            # Eject abbreviation from payment methods.
            updated_ad_document = utils.update_ad_payment_method(ad_document)
            # Make ads list and create markup.
            ads_list = utils.make_ads_list(updated_ad_document)
            markup = utils.generate_my_ads_inl_menu(ads_list)

            # Show ads list and additional buttons.
            bot.edit_message_text(text=_(MY_ANNOUNCEMENTS), chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup)

        else:
            bot.send_message(chat_id=chat_id, text=ZERO_ADS, reply_markup=bot_markup[language]['inl_add_ad'])

    # Check on inl button back to exchange.
    elif call.data == 'back_to_ex':
        bot.edit_message_text(text=_(EXCHANGE), chat_id=chat_id, message_id=message_id,
                              reply_markup=bot_markup[language]['exchange'])

    # Check on inl button add announcement.
    elif call.data == 'add_ad':
        # Get list of ads from db.
        ad_document = pymongodb.find({"user_id": user_id}, 'ads')
        pymongodb.finish()

        # Make ads list.
        ads_list = utils.make_ads_list(ad_document)

        # If user's ads not 4.
        if len(ads_list) != 4:
            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_CHOSE_AD_TYPE.value, config.db_state)

            # [CORRECT] Вынести в отдельную функцию в утилиты.
            # Get exception if user's ads list is clear.
            try:
                ad_type_id = ad_document[0]['ad_type_id']
            except IndexError:
                ad_type_id = None
            except KeyError:
                ad_type_id = None

            ad_type_list = []

            # [CORRECT] В перспективе вынести значения в списке в константы и использовать цикл for.
            # Buy id.
            if ad_type_id == 1:
                ad_type_list = [WANT_BUY, CANCEL]

            # Sell id.
            elif ad_type_id == 0:
                ad_type_list = [WANT_SELL, CANCEL]

            # Clear list of user's ads.
            elif ad_type_id is None:
                ad_type_list = [WANT_BUY, WANT_SELL, CANCEL]

            # Generate markup.
            ad_type_markup = utils.create_menu(ad_type_list)

            # Send bot message.
            bot.send_message(chat_id, text=AD_TYPE, reply_markup=ad_type_markup)

        # If user's ads 4 , return error (max limit of ads exceeded) , send user to main menu.
        else:
            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

            # Send bot message.
            bot.send_message(chat_id=chat_id, text=ERROR_MAX_ADS, reply_markup=bot_markup[language]['menu'])

    # Check on button "editing ad".
    elif re.match(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', call.data) is not None:
        # Get user's ad's uuid and find it into ad's db.
        ad_document = pymongodb.find_one({'user_id': user_id, 'uuid': call.data}, 'ads')
        pymongodb.finish()

        payment_method = ad_document['ad_payment_method']
        uuid_ = ad_document['uuid']

        if payment_method == 'FIAT':
            ad_payment_method = ad_document['ad_fiat_payment_method']
            ad_price = ad_document['ad_price'] + ' ' + ad_document['ad_fiat_payment_currency']

        else:
            ad_payment_method = ad_document['ad_payment_method']
            ad_price = ad_document['ad_price'] + ' ' + utils.eject_abbreviation(ad_document['ad_payment_method'])

        ad_type = ad_document['ad_type']
        ad_limits = ad_document['ad_limits']
        ad_amount = ad_document['ad_amount']
        ad_status = ad_document['ad_status']

        # Formatting limit values.
        limits_list = ad_limits.split('-')

        try:
            min_sum = limits_list[0] + ' ' + utils.eject_abbreviation(ad_payment_method)
            max_sum = limits_list[1] + ' ' + utils.eject_abbreviation(ad_payment_method)
        except TypeError:
            min_sum = limits_list[0] + ' ' + ad_document['ad_fiat_payment_currency']
            max_sum = limits_list[1] + ' ' + ad_document['ad_fiat_payment_currency']

        # Try get conditions, requisites and formatting message.
        try:
            ad_requisites = ad_document['ad_requisites']
        except KeyError:
            ad_requisites = None

        try:
            ad_conditions = ad_document['ad_conditions']
        except KeyError:
            ad_conditions = None

        if ad_conditions is not None and ad_requisites is not None:
            ad_description = AD_DESCRIPTION_WITH_CONDITIONS_AND_REQUISITES.format(ad_type, ad_payment_method, ad_price,
                                                                                  min_sum, max_sum, ad_amount,
                                                                                  ad_status, ad_requisites,
                                                                                  ad_conditions)

        elif ad_conditions is not None:
            ad_description = AD_DESCRIPTION_WITH_CONDITIONS.format(ad_type, ad_payment_method, ad_price, min_sum,
                                                                   max_sum, ad_amount, ad_status, ad_conditions)

        elif ad_requisites is not None:
            ad_description = AD_DESCRIPTION_WITH_REQUISITES.format(ad_type, ad_payment_method, ad_price, min_sum,
                                                                   max_sum, ad_amount, ad_status, ad_requisites)

        else:
            ad_description = AD_DESCRIPTION.format(ad_type, ad_payment_method, ad_price, min_sum, max_sum, ad_amount,
                                                   ad_status)

        # Generate inline markup.
        edit_btns_list = [[STH_RATE, 'ad_sth_rate#' + uuid_], [CONDITIONS, 'ad_conditions#' + uuid_],
                          [REQUISITES, 'ad_requisites#' + uuid_], [LIMITS, 'ad_limits#' + uuid_],
                          [AMOUNT, 'ad_amount#' + uuid_], [ad_status, 'ad_status'],
                          ['◀️ Назад', 'my_announcements'], ['❎ Удалить', 'delete#' + uuid_]]

        markup = utils.create_inline_ad_edit_menu(edit_btns_list)

        # Send bot message.
        bot.edit_message_text(text=_(ad_description), chat_id=chat_id, message_id=message_id,
                              reply_markup=markup, parse_mode="HTML")

    # SECTION "EDITING AD"
    # Change ad price.
    elif re.match(r'ad_sth_rate#\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', call.data) is not None:
        # Get uuid from call data and set into db.
        uuid_ = payment_method.split('#')
        dbworker.set_state(chat_id, uuid_[1], config.db_uuid)

        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_CHOOSE_FEE_OR_PRICE.value, config.db_state)

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(RATE_STX_FEE), reply_markup=bot_markup[language]['back'])

    # Change ad amount.
    elif re.match(r'ad_amount#\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', call.data) is not None:
        uuid_ = payment_method.split('#')
        dbworker.set_state(chat_id, uuid_[1], config.db_uuid)

        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_SET_AMOUNT.value, config.db_state)

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(EX_AMOUNT), reply_markup=bot_markup[language]['back'])

    # Change ad limits.
    elif re.match(r'ad_limits#\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', call.data) is not None:
        # Eject uuid from str and set into db.
        uuid_ = payment_method.split('#')
        dbworker.set_state(chat_id, uuid_[1], config.db_uuid)

        # Get currency and set into db.
        ad_document = pymongodb.find_one({'uuid': uuid_}, 'ads')

        try:
            currency = ad_document['ad_fiat_payment_currency']
        except KeyError:
            currency = ad_document['ad_payment_method']

        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_SET_LIMITS.value, config.db_state)

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(AD_LIMITS).format(currency), reply_markup=bot_markup[language]['back'])

    # Change ad conditions.
    elif re.match(r'ad_conditions#\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', call.data) is not None:
        uuid_ = payment_method.split('#')
        dbworker.set_state(chat_id, uuid_[1], config.db_uuid)

        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_SET_CONDITIONS.value, config.db_state)

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(AD_CONDITIONS), reply_markup=bot_markup[language]['back'])

    # Change ad requisites.
    elif re.match(r'ad_requisites#\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', call.data) is not None:
        uuid_ = payment_method.split('#')
        dbworker.set_state(chat_id, uuid_[1], config.db_uuid)

        # Get user's ad's uuid and find it into ad's db.
        ad_document = pymongodb.find_one({'user_id': user_id, 'uuid': uuid_[1]}, 'ads')
        pymongodb.finish()

        ad_payment_method = ad_document['ad_payment_method']

        # Set ad payment method into db.
        dbworker.set_state(chat_id, ad_payment_method, config.db_payment_method)

        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_SET_REQUISITES.value, config.db_state)

        # Check on payment method (Fiat or crypto).
        if ad_payment_method == 'FIAT':
            # Bot send message.
            bot.send_message(chat_id=chat_id, text=_(AD_REQUISITES), reply_markup=bot_markup[language]['back'])

        else:
            # Send bot message.
            bot.send_message(chat_id=chat_id, text=_(AD_REQUISITES_CRYPTO).format(ad_payment_method),
                             reply_markup=bot_markup[language]['back'])

    # Delete ad.
    elif re.match(r'delete#\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', call.data) is not None:
        # Get uuid and delete ad from db.
        uuid_ = payment_method.split('#')
        pymongodb.delete_one({'uuid': uuid_[1]}, 'ads')

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(DONE), reply_markup=bot_markup[language]['menu'])

    # If user want to buy or sell coins.
    elif call.data == 'BUY' or call.data == 'SELL' or call.data == 'back_to_crypto_fiat_list':
        if payment_method == 'back_to_crypto_fiat_list':
            ad_type = dbworker.get_current_state(chat_id, config.db_ex_choice)

        else:
            ad_type = payment_method

        crypto_ads_sum = pymongodb.count_with_filter({'ad_type': ad_type, 'ad_status': 'ON', 'ad_crypto': 'crypto'},
                                                     'ads')
        fiat_ads_sum = pymongodb.count_with_filter({'ad_type': ad_type, 'ad_status': 'ON',
                                                    'ad_payment_method': 'FIAT'}, 'ads')
        pymongodb.finish()

        if crypto_ads_sum != 0 or fiat_ads_sum != 0:
            dbworker.set_state(chat_id, ad_type, config.db_ex_choice)

            markup = utils.generate_inl_menu(['Отмена', 'back_to_exchange_menu'], crypto=crypto_ads_sum,
                                             fiat=fiat_ads_sum)

            bot.edit_message_text(text=_(CHOOSE_PAYMENT_METHOD_SELL), chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup[0])

        else:
            bot.send_message(chat_id=chat_id, text=_(NONE_ADS), reply_markup=bot_markup[language]['menu'])

    # Back to exchange menu.
    elif call.data == 'back_to_exchange_menu':
        # Send message
        bot.edit_message_text(text=_(EXCHANGE), chat_id=chat_id, message_id=message_id,
                              reply_markup=bot_markup[language]['exchange'])

    # If user want to buy or sell coins by crypto or fiat.
    elif call.data == 'crypto' or call.data == 'fiat':
        # Get ad type.
        ad_type = dbworker.get_current_state(chat_id, config.db_ex_choice)

        # Check on what payment method user choose (crypto or fiat).
        current_ads_count = None
        new_ads_count = None

        if payment_method == 'crypto':
            # Get ads count by current user's ad type choice.
            current_ads_count = dbworker.get_current_state('current_crypto_ads_count', config.db_data_cache)

            # Get ads count from db.
            new_ads_count = pymongodb.count_with_filter({'ad_type': ad_type, "ad_crypto": "crypto"}, 'ads')

        elif payment_method == 'fiat':
            # Get ads count by current user's ad type choice.
            current_ads_count = dbworker.get_current_state('current_fiat_ads_count', config.db_data_cache)

            # Get ads count from db.
            new_ads_count = pymongodb.count_with_filter({'ad_type': ad_type, "ad_payment_method": "FIAT"}, 'ads')

        # Check on clear db or there is a difference between old ads count and new.
        if current_ads_count == '1' or int(current_ads_count) != new_ads_count:
            payment_methods = None
            payment_method_name = None
            flag = None

            if payment_method == 'crypto':
                payment_methods = ['Bitcoin (BTC)', 'Ethereum (ETH)', 'Dogecoin (DOGE)']
                payment_method_name = 'ad_payment_method'
                # bot_message_text =

                # Get ads count.
                new_ads_count = pymongodb.count_with_filter({'ad_type': ad_type, "ad_crypto": "crypto"}, 'ads')

                # Set new ads count into db.
                dbworker.set_state('current_crypto_ads_count', new_ads_count, config.db_data_cache)

            elif payment_method == 'fiat':
                payment_methods = PAYMENT_CURRENCY_LIST
                payment_method_name = 'ad_fiat_payment_currency'
                flag = 'currency'
                # bot_message_text =

                # Get ads count.
                new_ads_count = pymongodb.count_with_filter({'ad_type': ad_type, "ad_payment_method": "FIAT"}, 'ads')

                # Set new ads count into db.
                dbworker.set_state('current_fiat_ads_count', new_ads_count, config.db_data_cache)

            # Get list of all ads.
            list_of_ads = []

            for payment_method in payment_methods:
                list_of_ads.append({payment_method: pymongodb.find({'ad_type': ad_type,
                                                                    payment_method_name: payment_method}, 'ads')})
            # Formatting list of all ads.
            formatted_list_of_ads = utils.format_list(list_of_ads)

            # Making list of ads such as ([btc, min_price, ads_count], etc) for generating inline markups.
            final_list = []

            # Сюда заряжать все функции.
            while formatted_list_of_ads:
                # Find same ads.
                same_ads_list = utils.get_same_ads(formatted_list_of_ads, payment_methods)

                # Find min price and set ad with min price into final list.
                final_list.append(utils.find_min_price(same_ads_list))

                # # Remove duplicates from main list with all ads.
                formatted_list_of_ads = utils.remove_duplicate_ads(formatted_list_of_ads, same_ads_list[0][0])

            # Set key name.
            key_name = None

            if call.data == 'crypto':
                key_name = 'crypto_ads0'

            elif call.data == 'fiat':
                key_name = 'fiat_ads0'

            # Serialized data and set it into db.
            json_obj = utils.serialize_json(final_list)
            dbworker.set_state(key_name, json_obj, config.db_data_cache)

            # Gen markup.
            markup = utils.create_inline_menu(final_list, flag=flag)

            # Send bot message.
            bot.edit_message_text(text=_(CHOOSE_CRYPTO_PAYMENT_METHOD_SELL), chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup)

        # Get data from cache.
        elif int(current_ads_count) == new_ads_count:
            data_name = None
            flag = None

            if payment_method == 'crypto':
                data_name = 'crypto_ads0'
                flag = None
            elif payment_method == 'fiat':
                data_name = 'fiat_ads0'
                flag = 'currency'

            # Deserialized data and get it from db.
            json_obj = dbworker.get_current_state(data_name, config.db_data_cache)
            final_list = utils.deserialize_json(json_obj)

            # Gen markup.
            markup = utils.create_inline_menu(final_list, flag=flag)

            # Send bot message.
            bot.edit_message_text(text=_(CHOOSE_CRYPTO_PAYMENT_METHOD_SELL), chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup)

    # If user want to buy or sell coins by fiat.
    elif call.data in PAYMENT_CURRENCY_LIST:
        # Get ad type.
        ad_type = dbworker.get_current_state(chat_id, config.db_ex_choice)

        currency = payment_method   # Вообще хз как это работает...

        # Get ads count by current user's ad type choice.
        current_ads_count = dbworker.get_current_state(('current_currency_ads_count_' + currency), config.db_data_cache)

        # Set currency of user's choice into db. Need for next step.
        dbworker.set_state(chat_id, currency, config.db_ex_choice_currency)

        # Get ads count from db.
        new_ads_count = pymongodb.count_with_filter({'ad_type': ad_type, "ad_fiat_payment_currency": currency}, 'ads')

        # Check on clear db or there is a difference between old ads count and new.
        if current_ads_count == '1' or int(current_ads_count) != new_ads_count:

            # Currency ads count.
            ads_count = pymongodb.count_with_filter({'ad_type': ad_type, "ad_fiat_payment_currency": currency}, 'ads')

            # Set new currency ads count.
            dbworker.set_state(('current_currency_ads_count_' + currency), ads_count, config.db_data_cache)

            # Get list of all ads.
            list_of_ads = []

            list_of_ads.append({payment_method: pymongodb.find({'ad_type': ad_type,
                                                                'ad_fiat_payment_currency': payment_method}, 'ads')})

            # Formatting list of all ads.
            formatted_list_of_ads = utils.format_list(list_of_ads, flag='fiat_payment')

            # Making list of ads such as ([btc, min_price, ads_count], etc) for generating inline markups.
            final_list = []

            while formatted_list_of_ads:
                # Find same ads.
                same_ads_list = utils.get_same_ads(formatted_list_of_ads, FIAT_PAYMENT_METHODS_LIST)

                count = len(same_ads_list)

                for same_ads in same_ads_list:
                    same_ads[2] = count

                # Find min price and set ad with min price into final list.
                final_list.append(utils.find_min_price(same_ads_list))

                # # Remove duplicates from main list with all ads.
                formatted_list_of_ads = utils.remove_duplicate_ads(formatted_list_of_ads, same_ads_list[0][0])

            # Prepare payment methods and create markups.
            markup = None

            if len(final_list) < 10:
                # Serialized data and set it into db.
                key_name = ('currency_ads_' + currency)

                json_obj = utils.serialize_json(final_list)
                dbworker.set_state(key_name, json_obj, config.db_data_cache)

                # # Gen markup.
                markup = utils.create_inline_menu(final_list, flag=payment_method)

            elif len(final_list) > 10:
                sorted_list_of_ads = utils.sort_list_items(final_list)
                split_list = []

                # Splitting list , limit = 10 ads.
                while sorted_list_of_ads:
                    split_list.append(sorted_list_of_ads[:10])
                    del sorted_list_of_ads[:10]

                markup = utils.create_ads_markup_with_pagination(split_list, currency=currency, flag=1)

                # Pagination
                key_name = ('currency_ads_' + currency)

                # В следующем шаге добавлять курренси в бд скорее всего нет смысла.
                dbworker.set_state(chat_id, currency, config.db_ex_choice_currency)     # for pagination.

                # Serialized data and set it into db.
                json_obj = utils.serialize_json(split_list)
                dbworker.set_state(key_name, json_obj, config.db_data_cache)
                memcache.del_data(str(chat_id))     # del mem cache.

            # Send bot message.
            bot.edit_message_text(text=_(CHOOSE_CURRENCY), chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup)

        # Get data from cache.
        elif int(current_ads_count) == new_ads_count:
            data_name = ('currency_ads_' + currency)

            # Deserialized data and get it from db.
            json_obj = dbworker.get_current_state(data_name, config.db_data_cache)
            final_list = utils.deserialize_json(json_obj)

            # Check list len.
            try:
                markup = utils.create_ads_markup_with_pagination(final_list, currency=currency, flag=1)
                memcache.del_data(str(chat_id))
            except TypeError:
                markup = utils.create_inline_menu(final_list, flag=currency)

            # Send bot message.
            bot.edit_message_text(text=_(CHOOSE_CURRENCY), chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup)

    # If user want to buy/sell coins by Bitcoin.
    elif call.data in PAYMENT_METHODS_LIST or call.data in FIAT_PAYMENT_METHODS_LIST:
        ad_type = dbworker.get_current_state(chat_id, config.db_ex_choice)      # get ad type.
        payment_method = call.data

        # Check call data.
        currency = None
        current_ads_count = None
        new_ads_count = None
        key_name = None

        if payment_method in PAYMENT_METHODS_LIST:
            key_name = ('ads_' + payment_method)

            # Get ads count by current user's ad type choice.
            current_ads_count = dbworker.get_current_state(('current_ads_count_' + payment_method),
                                                           config.db_data_cache)

            # Get ads count from db.
            new_ads_count = pymongodb.count_with_filter({'ad_type': ad_type, 'ad_payment_method': payment_method},
                                                        'ads')

        elif payment_method in FIAT_PAYMENT_METHODS_LIST:
            # Get ads count by current user's ad type choice.
            currency = dbworker.get_current_state(chat_id, config.db_ex_choice_currency)
            key_name = ('ads_' + currency + '_' + payment_method)
            current_ads_count = dbworker.get_current_state(('current_ads_count_' + currency + '_' + payment_method),
                                                           config.db_data_cache)

            # Get ads count from db.
            new_ads_count = pymongodb.count_with_filter({'ad_type': ad_type, 'ad_fiat_payment_currency': currency,
                                                        'ad_fiat_payment_method': payment_method}, 'ads')

        # Check on clear db or there is a difference between old ads count and new.
        if current_ads_count == '1' or int(current_ads_count) != new_ads_count:
            # Check call data.
            ads = None

            if payment_method in PAYMENT_METHODS_LIST:
                ads_count = pymongodb.count_with_filter({'ad_type': ad_type, 'ad_payment_method': payment_method},
                                                        'ads')
                ads = pymongodb.find({'ad_type': ad_type, 'ad_payment_method': payment_method}, 'ads')

                # Set new currency ads count.
                dbworker.set_state(('current_ads_count_' + payment_method), ads_count, config.db_data_cache)

            elif payment_method in FIAT_PAYMENT_METHODS_LIST:
                ads_count = pymongodb.count_with_filter({'ad_type': ad_type, 'ad_fiat_payment_currency': currency,
                                                        'ad_fiat_payment_method': payment_method}, 'ads')

                ads = pymongodb.find({'ad_type': ad_type, 'ad_fiat_payment_currency': currency,
                                     'ad_fiat_payment_method': payment_method}, 'ads')

                # Set new currency ads count.
                dbworker.set_state(('current_ads_count_' + currency + '_' + payment_method), ads_count,
                                   config.db_data_cache)

            # Prepare ads and making markups.
            formatted_list_of_ads = utils.format_ads_list(ads)  # format list of ads.

            if len(formatted_list_of_ads) > 10:
                sorted_list_of_ads = utils.sort_list_items(formatted_list_of_ads)
                split_list = []

                # Splitting list , limit = 10 ads.
                while sorted_list_of_ads:
                    split_list.append(sorted_list_of_ads[:10])
                    del sorted_list_of_ads[:10]

                markup = utils.create_ads_markup_with_pagination(split_list, currency=currency)

                # Serialized data and set it into db.
                json_obj = utils.serialize_json(split_list)

                # Pagination
                try:
                    name_data = 'ads_' + currency + '_' + payment_method

                except TypeError:
                    name_data = 'ads_' + payment_method

                dbworker.set_state(chat_id, payment_method, config.db_ex_choice_payment_method)
                dbworker.set_state(name_data, split_list, config.db_data_cache)
                memcache.del_data(str(chat_id))

            else:
                # Prepare ads and making markups.
                sorted_list_of_ads = utils.sort_list_items(formatted_list_of_ads)         # sorted list of ads by price.
                markup = utils.create_ads_markup(sorted_list_of_ads, currency=currency)   # create inline markup.

                # Serialized data and set it into db.
                json_obj = utils.serialize_json(sorted_list_of_ads)

            dbworker.set_state(key_name, json_obj, config.db_data_cache)

            # Send bot message.
            bot.edit_message_text(text=_(CHOOSE_CURRENCY), chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup)

        # Get data from cache.
        elif int(current_ads_count) == new_ads_count:
            data_name = None

            if payment_method in PAYMENT_METHODS_LIST:
                data_name = ('ads_' + payment_method)

            elif payment_method in FIAT_PAYMENT_METHODS_LIST:
                data_name = ('ads_' + currency + '_' + payment_method)

            # Deserialized data and get it from db.
            json_obj = dbworker.get_current_state(data_name, config.db_data_cache)
            final_list = utils.deserialize_json(json_obj)

            # Gen markup.
            try:
                markup = utils.create_ads_markup(final_list, currency=currency)
            except TypeError:
                markup = utils.create_ads_markup_with_pagination(final_list, currency=currency)
                memcache.del_data(str(chat_id))

            # Set payment method into db.
            dbworker.set_state(chat_id, payment_method, config.db_ex_choice_payment_method)

            # Send bot message.
            bot.edit_message_text(text=_(CHOOSE_CURRENCY), chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup)

    # Payment methods pagination.
    elif re.match(r'next_block_payment_methods', call.data) or re.match(r'previous_block_payment_methods', call.data):
        value = None

        if re.match(r'next_block_payment_methods', call.data):
            value = 1

        elif re.match(r'previous_block_payment_methods', call.data):
            value = -1

        currency = dbworker.get_current_state(chat_id, config.db_ex_choice_currency)
        key_name = ('currency_ads_' + currency)

        # Get data and deserialized.
        json_obj = dbworker.get_current_state(key_name, config.db_data_cache)  # for pagination.
        split_list = utils.deserialize_json(json_obj)

        # Creating pagination and markup.
        current_page_dict = memcache.get(str(chat_id))

        try:
            current_page = current_page_dict['current_page_payment_methods']
            current_page += value

            if current_page > (len(split_list) - 1):
                current_page = 0

            elif current_page < 0:
                current_page = (len(split_list) - 1)

            memcache.set(str(chat_id), {'current_page_payment_methods': current_page})

        except TypeError:
            current_page = 0

            current_page += value

            if value < 0:
                current_page = (len(split_list) - 1)

            memcache.set(str(chat_id), {'current_page_payment_methods': current_page})

        markup = utils.create_ads_markup_with_pagination(split_list, currency=currency, index=current_page, flag=1)

        # Send bot message.
        bot.edit_message_text(text=_(CHOOSE_CURRENCY), chat_id=chat_id, message_id=message_id,
                              reply_markup=markup)

    # Ads pagination.
    elif re.match(r'next_block_\w{4,5}', call.data) or re.match(r'previous_block_\w{4,5}', call.data):
        value = None

        if re.match(r'next_block_\w{4,5}', call.data):
            value = 1

        elif re.match(r'previous_block_\w{4,5}', call.data):
            value = -1

        # Eject payment method from call data.
        ejected_payment_method = utils.eject_payment_method(call.data)

        # Get currency and payment method.
        name_data = None
        payment_method = dbworker.get_current_state(chat_id, config.db_ex_choice_payment_method)

        # Check payment method.
        if ejected_payment_method == 'fiat':
            currency = dbworker.get_current_state(chat_id, config.db_ex_choice_currency)

            # Get blocks of ads.
            name_data = 'ads_' + currency + '_' + payment_method

        elif ejected_payment_method == 'crypto':
            currency = None
            name_data = 'ads_' + payment_method

        # Get ads blocks from db.
        ads_blocks = dbworker.get_current_state(name_data, config.db_data_cache)

        # Deserialize data.
        split_list = utils.deserialize_json(ads_blocks)

        # Creating pagination and markup.
        current_page_dict = memcache.get(str(chat_id))

        try:
            current_page = current_page_dict['current_page']
            current_page += value

            if current_page > (len(split_list) - 1):
                current_page = 0

            elif current_page < 0:
                current_page = (len(split_list) - 1)

            memcache.set(str(chat_id), {'current_page': current_page})

        except TypeError:
            current_page = 0

            current_page += value

            if value < 0:
                current_page = (len(split_list) - 1)

            memcache.set(str(chat_id), {'current_page': current_page})

        markup = utils.create_ads_markup_with_pagination(split_list, currency=currency, index=current_page)

        # Send bot message.
        bot.edit_message_text(text=_(CHOOSE_CURRENCY), chat_id=chat_id, message_id=message_id,
                              reply_markup=markup)

    # View template.
    elif re.match(r'view_\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', call.data) is not None:
        username = call.from_user.username

        # Расширить функцию split в модуле utils.
        split_list = (call.data).split('_')
        uuid_ = split_list[1]

        # Get data from db.
        ad_document = pymongodb.find_one({'uuid': uuid_}, 'ads')
        ad_type = ad_document['ad_type']

        try:
            ad_payment_method = ad_document['ad_fiat_payment_method']
        except KeyError:
            ad_payment_method = ad_document['ad_payment_method']

        ad_requisites = ad_document['ad_requisites']
        ad_conditions = ad_document['ad_conditions']

        # Format ad text and generate markup.
        ad_text = VIEW_SELL.format(ad_type, ad_payment_method, ('@' + username), ad_requisites, ad_conditions)
        markup = utils.create_inline_menu2(ad_payment_method)

        # Send bot message.
        bot.edit_message_text(text=_(ad_text), chat_id=chat_id, message_id=message_id,
                              reply_markup=markup)

    # # SETTINGS SECTION.
    # Check on inline button language.
    elif call.data == 'lang':
        bot.edit_message_text(text=_(LANG), chat_id=chat_id, message_id=message_id,
                              reply_markup=MARKUP_INLINE_LANG_CHOICE)

    # Back to settings
    elif call.data == 'back_to_settings' or call.data == 'back_sett':
        bot.edit_message_text(text=_(SETTINGS), chat_id=chat_id, message_id=message_id,
                              reply_markup=bot_markup[language]['inl_settings'])

    # Choose lang
    elif call.data == 'en' or call.data == 'ru':
        language = dbworker.get_current_state(chat_id, config.db_language)

        if re.match(language, call.data) is None:
            # Update and insert lang value in db.
            dbworker.set_state(chat_id, call.data, config.db_language)

            # Set lang.
            _ = utils.set_language(call.data)

            # Edit message.
            bot.edit_message_text(text=_(LANG), chat_id=chat_id, message_id=message_id,
                                  reply_markup=MARKUP_INLINE_LANG_CHOICE)
            bot.send_message(chat_id, text=_(DONE), reply_markup=bot_markup[payment_method]['menu'])

    # Check on inline button in settings , named Rate of STX
    elif call.data == 'rate':
        bot.edit_message_text(text=(_(RATE).format(currency, exchange)), chat_id=chat_id,
                              message_id=message_id, reply_markup=mrkp_inl_rate)

    # Check on inline buttons such as currency name.
    elif call.data in EXCHANGES:
        pymongodb.find_one_and_update_by_id(obj_id, {"exchange": payment_method}, 'users', "$set")

        if payment_method != exchange:
            bot.edit_message_text(text=(_(RATE).format(currency, payment_method)), chat_id=chat_id,
                                  message_id=message_id, reply_markup=mrkp_inl_rate)

    # Check on inline button named select currency , which pressed in feedback message or in settings
    elif call.data == 'select_currency_f' or call.data == 'select_currency_s':
        if call.data[-1] == 'f':
            markup = MARKUP_INLINE_CURRENCIES_F
        else:
            markup = MARKUP_INLINE_CURRENCIES_S

        bot.edit_message_text(text=_(CURRENCY).format(currency), chat_id=chat_id, message_id=message_id,
                              reply_markup=markup)

    # Check on inline button back to feedback, which redirect user to feedback message.
    elif call.data == 'back_feed':
        bot.edit_message_text(text=_(FEEDBACK), chat_id=chat_id, message_id=message_id,
                              reply_markup=bot_markup[language]['select_currency'])

    # Check call data on inline buttons such as btc, eth etc (In feedback and settings)
    elif call.data in CURRENCY_LIST_SUM:
        if len(payment_method) > 3:
            currency = payment_method[:-2]
            text = _(SETTINGS)
            markup = MARKUP_INLINE_SETTINGS
        else:
            currency = payment_method
            text = _(FEEDBACK)
            markup = MARKUP__INLINE_SEL_CURRENCY

        pymongodb.find_one_and_update_by_id(obj_id, {"currency": currency}, 'users', "$set")
        pymongodb.finish()

        bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id,
                              reply_markup=markup)

    elif call.data == 'address':
        bot.send_message(chat_id=chat_id, text=_(CONTACTS), reply_markup=bot_markup[language]['cancel'])

        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_ADD_FAVORITE_ADDRESS.value, config.db_state)

    # # About service section.
    # Talks
    elif call.data == "talks":
        bot.edit_message_text(text=_(COMMUNICATION), chat_id=chat_id, message_id=message_id,
                              reply_markup=bot_markup[language]['talks'])

    # Back to service menu
    elif call.data == "back_to_service":
        bot.edit_message_text(text=_(ABOUT_SERVICE), chat_id=chat_id, message_id=message_id,
                              reply_markup=bot_markup[language]['service_menu'])

    elif call.data == "partners":
        partner_link = "telegram.me/STX_BRO_BOT?start=" + partner_link

        bot.edit_message_text(text=_(PARTNERS).format(partner_link), chat_id=chat_id,
                              message_id=message_id, reply_markup=bot_markup[language]['back_to_service'])


# # # Settings section
# Add a favorite address for fast access on the withdraw stage.
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_ADD_FAVORITE_ADDRESS.value)
def add_favorite_address(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Get recipient id and remove tabs symbols.
    address = utils.delete_tab_symbols(message.text)

    # Check on valid recipient id.
    result = utils.check_recipient_id(address)

    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # Check result (if result not False -> add favorite address to db)
    if result is False:

        if message.text.find("❌") is 0:
            bot.send_message(chat_id, text=_(CHANGED_MIND), reply_markup=bot_markup[language]['menu'])

            # Set new user's state.
            dbworker.set_state(message.chat.id, config.States.S_USE_MENU.value, config.db_state)

        elif message.text == "/menu":
            bot.send_message(chat_id, text=_(CANCELED), reply_markup=bot_markup[language]['menu'])

        else:
            bot.send_message(chat_id, text=_(INCORRECT_DATA), reply_markup=bot_markup[language]['cancel'])

            # Set new user's state.
            dbworker.set_state(message.chat.id, config.States.S_ADD_FAVORITE_ADDRESS.value, config.db_state)

    else:
        # Set favorite address to db
        pymongodb.find_one_and_update({'user_id': user_id}, {'contact': address}, 'users', '$set')
        pymongodb.finish()

        bot.send_message(chat_id=chat_id, text=_(DONE), reply_markup=bot_markup[language]['menu'])

        # Set new user's state.
        dbworker.set_state(message.chat.id, config.States.S_USE_MENU.value, config.db_state)


# # # Wallet section
# Func which get answer on user's question "use address from contact list or not?"
# [???] Под вопросом как работает конструкция try except где есть affiliate link
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_USE_ADDRESS_FROM_CONTACTS.value)
def use_address_from_contacts(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # Check on user's answer "Yes"
    # [CORRECT] Сделать сначала проверку на наличие адреса в контакта , а уже если адрес есть то спросить
    # у юзверя хочет ли он использовать адрес из списка контактов.
    if message.text.startswith("👌"):
        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(INPUT_AMOUNT), reply_markup=bot_markup[language]['cancel'])

        # Set new user's state.
        dbworker.set_state(message.chat.id, config.States.S_GET_AMOUNT.value, config.db_state)

    # Check on user's answer "No"
    elif message.text.startswith("⛔"):
        bot.send_message(chat_id=chat_id, text=_(INPUT_RECIPIENT_ID), reply_markup=bot_markup[language]['cancel'])

        # Set new user's state.
        dbworker.set_state(message.chat.id, config.States.S_GET_RECIPIENT_ID.value, config.db_state)

    # Check on user's answer "Changed mind"
    elif message.text.find("❌") is 0:
        bot.send_message(chat_id, text=_(CHANGED_MIND), reply_markup=bot_markup[language]['menu'])

        # Set new user's state.
        dbworker.set_state(message.chat.id, config.States.S_USE_MENU.value, config.db_state)


# # # WALLET SECTION
# Func which get recipient address from user.
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_GET_RECIPIENT_ID.value)
def get_recipient_id(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Get recipient id and remove tabs symbols.
    recipient_id = utils.delete_tab_symbols(message.text)

    # Check on valid recipient_id.
    result = utils.check_recipient_id(recipient_id)

    # Get document and language.
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']
    obj_id = user_document['_id']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # Check result
    if result is False:
        if message.text.find("❌") is 0:
            # Send bot message.
            bot.send_message(chat_id, text=_(CHANGED_MIND), reply_markup=bot_markup[language]['menu'])

            # Set new user's state.
            dbworker.set_state(message.chat.id, config.States.S_USE_MENU.value, config.db_state)

        elif message.text == "/menu":
            # Send bot message.
            bot.send_message(chat_id, text=_(CANCELED), reply_markup=bot_markup[language]['menu'])

        else:
            # Send bot message.
            bot.send_message(chat_id, text=_(INCORRECT_DATA), reply_markup=bot_markup[language]['cancel'])

            # Set new user's state.
            dbworker.set_state(message.chat.id, config.States.S_GET_RECIPIENT_ID.value, config.db_state)

    # If result is valid.
    else:
        # Set recipient_id into db.
        pymongodb.find_one_and_update_by_id(obj_id, {"_recipient_id": recipient_id}, 'users', "$set")
        pymongodb.finish()

        # Send bot message.
        bot.send_message(chat_id, text=_(INPUT_AMOUNT), reply_markup=bot_markup[language]['cancel'])

        # Set new user's state.
        dbworker.set_state(message.chat.id, config.States.S_GET_AMOUNT.value, config.db_state)


# Func which get amount of coins for sending from user , not save in bd
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_GET_AMOUNT.value)
def get_amount(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Get amount and remove tabs symbols.
    amount = utils.delete_tab_symbols(message.text)

    # Check on valid amount.
    result = utils.check_amount(amount)

    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']
    obj_id = user_document['_id']
    choice = user_document['_choice']

    # Decrypt passphrase.
    passphrase = utils.decrypt_string(user_document['passphrase'], CIPHER_KEY)

    # Try to get _rec_id. If error it means that user used rec_id from contact list.
    try:
        recipient_id = user_document['_recipient_id']
    except KeyError:
        recipient_id = user_document['contact']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # Check result of checking amount func
    if result is False:

        if message.text.find("❌") is 0:
            # Send bot message.
            bot.send_message(chat_id, text=_(CHANGED_MIND), reply_markup=bot_markup[language]['menu'])

            # Set new user's state.
            dbworker.set_state(message.chat.id, config.States.S_USE_MENU.value, config.db_state)

        elif message.text == "/menu":
            # Send bot message.
            bot.send_message(chat_id, text=_(CANCELED), reply_markup=bot_markup[language]['menu'])

        else:
            bot.send_message(chat_id, text=_(INCORRECT_DATA), reply_markup=bot_markup[language]['cancel'])

            # Set new user's state.
            dbworker.set_state(message.chat.id, config.States.S_GET_AMOUNT.value, config.db_state)

    else:
        amount = int(amount) * 100_000_000

        # Check choice for next step.
        if choice == 'withdrawal':
            # Send coins.
            withdrawal_coins(recipient_id, amount, passphrase, chat_id, user_id)

        elif choice == 'send':
            # Set amount into db.
            pymongodb.find_one_and_update_by_id(obj_id, {'_amount': amount}, 'users')
            pymongodb.finish()

            # Send bot message.
            bot.send_message(chat_id, text=_(INPUT_PAS), reply_markup=bot_markup[language]['cancel'])

            # Set new user's state.
            dbworker.set_state(message.chat.id, config.States.S_GET_PAS.value, config.db_state)


# Func which send tx (func of withdrawal item)
def withdrawal_coins(recipient_id, amount, passphrase, chat_id, user_id):
    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # Send tx and get result.
    tx_res = pysmart_api.send_tx(recipient_id, amount, passphrase)

    # Check result
    if tx_res is True:
        tx_count = 0
        tx_count += 1

        # Upsert user's data in db
        pymongodb.find_one_and_update({'user_id': user_id}, {'sum_of_coins': int(amount),
                                                             'tx_count': tx_count}, 'users', '$inc')
        pymongodb.finish()

        # Send bot message.
        bot.send_message(chat_id, text=_(SUCCESS_TX), reply_markup=bot_markup[language]['menu'])

        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

    else:
        # Send bot messages.
        bot.send_message(chat_id, text=_(INCORRECT_DATA))
        bot.send_message(chat_id, text=_(INPUT_RECIPIENT_ID), reply_markup=bot_markup[language]['cancel'])

        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_GET_RECIPIENT_ID.value, config.db_state)


# Func which get passphrase from user , not save in bd (func of send item)
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_GET_PAS.value)
def get_pas(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    passphrase = message.text

    # Check passphrase.
    check_result = utils.check_passphrase(passphrase)

    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']
    recipient_id = user_document['_recipient_id']
    amount = user_document['_amount']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # Check result
    if check_result is False:

        if passphrase.find("❌") is 0:
            bot.send_message(chat_id, text=_(CHANGED_MIND), reply_markup=bot_markup[language]['menu'])

            # Set new user's state.
            dbworker.set_state(message.chat.id, config.States.S_USE_MENU.value, config.db_state)

        elif message.text == "/menu":
            # Send bot message.
            bot.send_message(chat_id, text=_(CANCELED), reply_markup=bot_markup[language]['menu'])

        else:
            # Send bot message.
            bot.send_message(chat_id, text=_(INCORRECT_DATA), reply_markup=bot_markup[language]['cancel'])

            # Set new user's state.
            dbworker.set_state(message.chat.id, config.States.S_GET_PAS.value, config.db_state)

    else:
        # Remove tab symbols.
        passphrase_ = utils.delete_tab_symbols(passphrase)

        # Send tx.
        tx_res = pysmart_api.send_tx(recipient_id, amount, passphrase_)

        if tx_res is True:
            user_id = message.from_user.id
            tx_count = 0
            tx_count += 1

            # Upsert user's data in db
            pymongodb.find_one_and_update({'user_id': user_id}, {'sum_of_coins': int(amount),
                                                                 'tx_count': tx_count}, 'users', '$inc')
            pymongodb.finish()

            # Send bot message.
            bot.send_message(chat_id, text=_(SUCCESS_TX))
            bot.send_message(chat_id, text=_(ATTENTION), reply_markup=bot_markup[language]['menu'], parse_mode="HTML")

            # Set new user's state.
            dbworker.set_state(message.chat.id, config.States.S_USE_MENU.value, config.db_state)

        else:
            # Send bot message.
            bot.send_message(chat_id, text=_(INCORRECT_DATA))
            bot.send_message(chat_id, text=_(INPUT_RECIPIENT_ID), reply_markup=bot_markup[language]['cancel'])

            # Set new user's state.
            dbworker.set_state(message.chat.id, config.States.S_GET_RECIPIENT_ID.value, config.db_state)


# EXCHANGE SECTION.
# Adding announcements
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_CHOSE_AD_TYPE.value)
def choose_ad_type(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    ad_type = message.text

    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # Want to buy.
    if ad_type.find('📈') is 0 or ad_type.find('📉') is 0:

        if ad_type.find('📈') is 0:
            ad_type = 'BUY'

            # Set ad type into db (need for identifier ad in other next step funcs).
            dbworker.set_state(chat_id, ad_type, config.db_ad_type)

        elif ad_type.find('📉') is 0:
            ad_type = 'SELL'

            # Set ad type into db (need for identifier ad in other next step funcs).
            dbworker.set_state(chat_id, ad_type, config.db_ad_type)

        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_CHOOSE_PAYMENT_METHOD.value, config.db_state)

        # Find duplicates in payment methods list and remove if they have.
        ads_document = pymongodb.find({'user_id': user_id}, 'ads')
        pymongodb.finish()

        # If user's have ads.
        if ads_document:
            # Remove duplicates in payment methods list,
            payment_method_list = utils.remove_duplicate_payment_methods(ads_document)

            # Create markup.
            payment_method_markup = utils.create_menu(payment_method_list, '⬅️ Назад')

        # If user's don't have ads.
        else:
            original_payment_method_list = ['Bitcoin (BTC)', 'Ethereum (ETH)', 'Dogecoin (DOGE)', 'FIAT']

            # Create markup.
            payment_method_markup = utils.create_menu(original_payment_method_list, '⬅️ Назад')

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=PAYMENT_METHOD, reply_markup=payment_method_markup)

    # Changed mind.
    elif ad_type.find('❌') is 0:
        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(CHANGED_MIND), reply_markup=bot_markup[language]['menu'])

    # If choice is incorrect data.
    else:
        # Set new user's state.
        dbworker.set_state(message.chat.id, config.States.S_CHOSE_AD_TYPE.value, config.db_state)

        # Get list of ads from db.
        ad_document = pymongodb.find({"user_id": user_id}, 'ads')
        pymongodb.finish()

        # [CORRECT] Вынести в отдельную функцию в утилиты.
        # Get exception if user's ads list is clear.
        try:
            ad_type_id = ad_document[0]['ad_type_id']
        except IndexError:
            ad_type_id = None
        except KeyError:
            ad_type_id = None

        ad_type_list = []

        # [CORRECT] В перспективе вынести значения в списке в константы и использовать цикл for.
        # Buy id.
        if ad_type_id == 1:
            ad_type_list = [WANT_BUY, CANCEL]

        # Sell id.
        elif ad_type_id == 0:
            ad_type_list = [WANT_SELL, CANCEL]

        # Clear list of user's ads.
        elif ad_type_id is None:
            ad_type_list = [WANT_BUY, WANT_SELL, CANCEL]

        # Generate markup.
        ad_type_markup = utils.create_menu(ad_type_list)

        # Send bot message.
        bot.send_message(chat_id, text=_(INCORRECT_DATA), reply_markup=ad_type_markup)


# Choose payment method (Doge or etc.)
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_CHOOSE_PAYMENT_METHOD.value)
def choose_payment_method(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    payment_method = message.text

    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # Payment methods list.
    payment_methods_list = ['Dogecoin (DOGE)', 'Bitcoin (BTC)', 'Ethereum (ETH)', 'FIAT']

    # Check on user's choice is in static payment method list.
    if payment_method in payment_methods_list:
        # Set payment method into db.
        dbworker.set_state(chat_id, payment_method, config.db_payment_method)

        # If user's choice of payment method is Fiat.
        if payment_method == 'FIAT':
            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_SET_PAYMENT_CURRENCY.value, config.db_state)

            # Create markup.
            currency_markup = utils.create_menu(PAYMENT_CURRENCY_LIST, '⬅️ Назад')

            # Send bot message.
            bot.send_message(chat_id=chat_id, text=_(CURRENCY_CHOICE), reply_markup=currency_markup)

        # If choice is not Fiat.
        else:
            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_CHOOSE_FEE_OR_PRICE.value, config.db_state)

            # Send bot message.
            bot.send_message(chat_id=chat_id, text=_(RATE_STX_FEE), reply_markup=bot_markup[language]['back'])

    # Back to choose ad type.
    elif payment_method.startswith('⬅') is True:
            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_CHOSE_AD_TYPE.value, config.db_state)

            # Get list of ads from db.
            ad_document = pymongodb.find({"user_id": user_id}, 'ads')
            pymongodb.finish()

            # [CORRECT] Вынести в отдельную функцию в утилиты.
            # Get exception if user's ads list is clear.
            try:
                ad_type_id = ad_document[0]['ad_type_id']
            except IndexError:
                ad_type_id = None
            except KeyError:
                ad_type_id = None

            ad_type_list = []

            # [CORRECT] В перспективе вынести значения в списке в константы и использовать цикл for.
            # Buy id.
            if ad_type_id == 1:
                ad_type_list = [WANT_BUY, CANCEL]

            # Sell id.
            elif ad_type_id == 0:
                ad_type_list = [WANT_SELL, CANCEL]

            # Clear list of user's ads.
            elif ad_type_id is None:
                ad_type_list = [WANT_BUY, WANT_SELL, CANCEL]

            # Generate markup.
            ad_type_markup = utils.create_menu(ad_type_list)

            # Send bot message.
            bot.send_message(chat_id, text=AD_TYPE, reply_markup=ad_type_markup)

    # If choice is incorrect data.
    else:
        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_CHOOSE_PAYMENT_METHOD.value, config.db_state)

        # Find duplicates in payment methods list and remove if they have.
        ads_document = pymongodb.find({'user_id': user_id}, 'ads')
        pymongodb.finish()

        # If user's have ads.
        if ads_document:
            # Remove duplicates in payment methods list,
            payment_method_list = utils.remove_duplicate_payment_methods(ads_document)

            # Create markup.
            payment_method_markup = utils.create_menu(payment_method_list, '⬅️ Назад')

        # If user's don't have ads.
        else:
            original_payment_method_list = ['Bitcoin (BTC)', 'Ethereum (ETH)', 'Dogecoin (DOGE)', 'Fiat']

            # Create markup.
            payment_method_markup = utils.create_menu(original_payment_method_list, '⬅️ Назад')

        # Send bot message.
        bot.send_message(chat_id, text=_(INCORRECT_DATA), reply_markup=payment_method_markup)


# Set currency for fiat payment method.
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_SET_PAYMENT_CURRENCY.value)
def set_fiat_payment_currency(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_choice = message.text

    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # Check user's choice.
    valid_currency = utils.check_fiat_payment_currency(user_choice)

    if valid_currency is not None:
        # Set valid payment currency.
        dbworker.set_state(chat_id, valid_currency, config.db_fiat_payment_currency)

        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_SET_FIAT_PAYMENT_METHOD.value, config.db_state)

        # Gen markup.
        fiat_payment_methods_markup = utils.create_menu(FIAT_PAYMENT_METHODS_LIST, '⬅️ Назад')

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(PAYMENT_METHOD), reply_markup=fiat_payment_methods_markup)

    # Back to ad payment method.
    elif user_choice.startswith('⬅') is True:
        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_CHOOSE_PAYMENT_METHOD.value, config.db_state)

        # Find duplicates in payment methods list and remove if they have.
        ads_document = pymongodb.find({'user_id': user_id}, 'ads')
        pymongodb.finish()

        # If user's have ads.
        if ads_document:
            # Remove duplicates in payment methods list,
            payment_method_list = utils.remove_duplicate_payment_methods(ads_document)

            # Create markup.
            payment_method_markup = utils.create_menu(payment_method_list, '⬅️ Назад')

        # If user's don't have ads.
        else:
            original_payment_method_list = ['Bitcoin (BTC)', 'Ethereum (ETH)', 'Dogecoin (DOGE)', 'FIAT']

            # Create markup.
            payment_method_markup = utils.create_menu(original_payment_method_list, '⬅️ Назад')

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=PAYMENT_METHOD, reply_markup=payment_method_markup)

    # Incorrect data.
    else:
        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_SET_PAYMENT_CURRENCY.value, config.db_state)

        # Create markup.
        currency_markup = utils.create_menu(PAYMENT_CURRENCY_LIST, '⬅️ Назад')

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(INCORRECT_DATA), reply_markup=currency_markup)


# Set fiat payment method.
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_SET_FIAT_PAYMENT_METHOD.value)
def set_fiat_payment_method(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    fiat_payment_method = message.text

    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # Back to set fiat payment currency.
    if fiat_payment_method.startswith('⬅') is True:
        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_SET_PAYMENT_CURRENCY.value, config.db_state)

        # Create markup.
        currency_markup = utils.create_menu(PAYMENT_CURRENCY_LIST, '⬅️ Назад')

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(CURRENCY_CHOICE), reply_markup=currency_markup)

    # If chosen fiat payment method is in list of all payment methods - add it into db.
    elif fiat_payment_method in FIAT_PAYMENT_METHODS_LIST:
        # Set fiat payment method into db.
        dbworker.set_state(chat_id, fiat_payment_method, config.db_fiat_payment_method)

        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_CHOOSE_FEE_OR_PRICE.value, config.db_state)

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=RATE_STX_FEE, reply_markup=bot_markup[language]['back'])

    # Incorrect data.
    else:
        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_SET_FIAT_PAYMENT_METHOD.value, config.db_state)

        # Gen markup.
        fiat_payment_methods_markup = utils.create_menu(FIAT_PAYMENT_METHODS_LIST, '⬅️ Назад')

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(INCORRECT_DATA), reply_markup=fiat_payment_methods_markup)


# Set fee or STX price.
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_CHOOSE_FEE_OR_PRICE.value)
def set_fee_or_price(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    fee_or_price = message.text

    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # Back.
    if fee_or_price.startswith('⬅') is True:
        # Try to get uuid.
        uuid_ = dbworker.get_current_state(chat_id, config.db_uuid)

        # If user come here from edit section.
        if uuid_ != '1':
            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

            # Del uuid from db.
            dbworker.delete(chat_id, config.db_uuid)

            # Send bot message.
            bot.send_message(chat_id=chat_id, text=_(CHANGED_MIND), reply_markup=bot_markup[language]['menu'])

        else:
            payment_method = dbworker.get_current_state(chat_id, config.db_payment_method)

            if payment_method == 'FIAT':
                dbworker.set_state(chat_id, config.States.S_SET_FIAT_PAYMENT_METHOD.value, config.db_state)

                # Gen fiat payment markup.
                fiat_payment_methods_markup = utils.create_menu(FIAT_PAYMENT_METHODS_LIST, '⬅️ Назад')

                # Send bot message.
                bot.send_message(chat_id=chat_id, text=_(PAYMENT_METHOD), reply_markup=fiat_payment_methods_markup)

            else:
                dbworker.set_state(chat_id, config.States.S_CHOOSE_PAYMENT_METHOD.value, config.db_state)

                # Gen crypto markup.
                # Find duplicates in payment methods list and remove if they have.
                ads_document = pymongodb.find({'user_id': user_id}, 'ads')
                pymongodb.finish()

                # If user's have ads.
                if ads_document:
                    # Remove duplicates in payment methods list,
                    payment_method_list = utils.remove_duplicate_payment_methods(ads_document)

                    # Create markup.
                    payment_method_markup = utils.create_menu(payment_method_list, '⬅️ Назад')

                # If user's don't have ads.
                else:
                    original_payment_method_list = ['Bitcoin (BTC)', 'Ethereum (ETH)', 'Dogecoin (DOGE)', 'Fiat']

                    # Create markup.
                    payment_method_markup = utils.create_menu(original_payment_method_list, '⬅️ Назад')

                # Send bot message.
                bot.send_message(chat_id=chat_id, text=_(PAYMENT_METHOD), reply_markup=payment_method_markup)

    elif fee_or_price.startswith("❌") is True:
        # Set new user's state.
        dbworker.set_state(message.chat.id, config.States.S_USE_MENU.value, config.db_state)

        # Del uuid from db.
        dbworker.delete(chat_id, config.db_uuid)

        # Send bot message.
        bot.send_message(chat_id, text=_(CHANGED_MIND), reply_markup=bot_markup[language]['menu'])

    else:
        result = utils.get_fee_or_price(fee_or_price)

        # Check result (fee or price).
        if result is False:
            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_CHOOSE_FEE_OR_PRICE.value, config.db_state)

            # Send bot message.
            bot.send_message(chat_id=chat_id, text=_(INCORRECT_DATA), reply_markup=bot_markup[language]['back'])

        elif result[1] is 'fee':
            # [ADD] Здесь добавить в сообщение от бота какая в итоге цена получится с учетом наценки.
            # [ADD] Высчитывать % и прибавлять его к текущему курсу.
            # [ADD] Добавить исключение , если цена еще не установлена (цена установится после первой сделки).

            uuid_ = dbworker.get_current_state(chat_id, config.db_uuid)

            # If user edit ad.
            if uuid_ != '1':
                # Set new ad price into db.
                pymongodb.find_one_and_update({'uuid': uuid_}, {'ad_price': result[0]}, 'ads', '$set')

                # Del uuid from db.
                dbworker.delete(chat_id, config.db_uuid)

                # Set new user's state.
                dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

                # Send bot message.
                bot.send_message(chat_id=chat_id, text=_(DONE), reply_markup=bot_markup[language]['menu'])

            else:
                # Set fee on db.
                dbworker.set_state(chat_id, result[0], config.db_fee_or_price)

                # Set user's state.
                dbworker.set_state(chat_id, config.States.S_SET_LIMITS.value, config.db_state)

                # Get currency for formatting message.
                ad_payment_method = dbworker.get_current_state(chat_id, config.db_payment_method)

                if ad_payment_method == 'FIAT':
                    currency = dbworker.get_current_state(chat_id, config.db_fiat_payment_currency)

                else:
                    currency = ad_payment_method

                # Send bot message.
                bot.send_message(chat_id=chat_id, text=_(AD_LIMITS).format(currency),
                                 reply_markup=bot_markup[language]['back'])

        elif result[1] is 'price':
            uuid_ = dbworker.get_current_state(chat_id, config.db_uuid)

            # If user edit ad.
            if uuid_ != '1':
                # Set new ad price into db.
                pymongodb.find_one_and_update({'uuid': uuid_}, {'ad_price': result[0]}, 'ads', '$set')

                # Del uuid from db.
                dbworker.delete(chat_id, config.db_uuid)

                # Set new user's state.
                dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

                # Send bot message.
                bot.send_message(chat_id=chat_id, text=_(DONE), reply_markup=bot_markup[language]['menu'])

            else:
                # Set price on db.
                dbworker.set_state(chat_id, result[0], config.db_fee_or_price)

                # Set user's state.
                dbworker.set_state(chat_id, config.States.S_SET_LIMITS.value, config.db_state)

                # Get currency for formatting message.
                ad_payment_method = dbworker.get_current_state(chat_id, config.db_payment_method)

                if ad_payment_method == 'FIAT':
                    currency = dbworker.get_current_state(chat_id, config.db_fiat_payment_currency)

                else:
                    currency = ad_payment_method

                # Send bot message.
                bot.send_message(chat_id=chat_id, text=_(AD_LIMITS).format(currency),
                                 reply_markup=bot_markup[language]['back'])


# Func which get limits from user message and set it into db.
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_SET_LIMITS.value)
def set_limits(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    limits = message.text

    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # Check limits on valid.
    result = utils.check_limits(limits)

    # If limits is valid.
    if result is None:
        # Try to get uuid.
        uuid_ = dbworker.get_current_state(chat_id, config.db_uuid)

        # It means that user want to edit also created ad , correctly want to edit limits.
        if uuid_ != '1':
            # Set ad limits into db.
            pymongodb.find_one_and_update({'uuid': uuid_}, {'ad_limits': limits}, 'ads', '$set')

            # Del uuid from db.
            dbworker.delete(chat_id, config.db_uuid)

            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

            # Send bot message.
            bot.send_message(chat_id=chat_id, text=_(DONE), reply_markup=bot_markup[language]['menu'])

        else:
            # Set valid value into db.
            dbworker.set_state(chat_id, limits, config.db_limits)

            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_SET_AMOUNT.value, config.db_state)

            # Send bot message.
            bot.send_message(chat_id=chat_id, text=_(EX_AMOUNT), reply_markup=bot_markup[language]['back'])

    # If min limit > max limit.
    elif result == '>':
        # Rerun set limits func.
        dbworker.set_state(chat_id, config.States.S_SET_LIMITS.value, config.db_state)

        bot.send_message(chat_id=chat_id, text=_(INCORRECT_LIMITS), reply_markup=bot_markup[language]['back'])

    elif limits.startswith('⬅') is True:
        # Try to get uuid.
        uuid_ = dbworker.get_current_state(chat_id, config.db_uuid)

        # If user come here from edit section.
        if uuid_ != '1':
            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

            # Del uuid from db.
            dbworker.delete(chat_id, config.db_uuid)

            # Send bot message.
            bot.send_message(chat_id=chat_id, text=_(CHANGED_MIND), reply_markup=bot_markup[language]['menu'])

        # If not from edit section.
        else:
            # Set new user's state.
            dbworker.set_state(message.chat.id, config.States.S_CHOOSE_FEE_OR_PRICE.value, config.db_state)

            # Send bot message.
            bot.send_message(chat_id, text=_(RATE_STX_FEE), reply_markup=bot_markup[language]['back'])

    # If input valid is incorrect.
    elif result is False:
        # Rerun set limits func.
        dbworker.set_state(chat_id, config.States.S_SET_LIMITS.value, config.db_state)

        bot.send_message(chat_id=chat_id, text=_(INCORRECT_DATA), reply_markup=bot_markup[language]['back'])


# Func which get input amount from user and set it into db.
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_SET_AMOUNT.value)
def set_amount(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    ad_amount = message.text
    username = message.from_user.username

    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    # Check amount.
    result = utils.check_amount(ad_amount)

    # Back
    if ad_amount.startswith('⬅') is True:
        # Try to get uuid.
        uuid_ = dbworker.get_current_state(chat_id, config.db_uuid)

        # If user come here from edit section.
        if uuid_ != '1':
            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

            # Del uuid from db.
            dbworker.delete(chat_id, config.db_uuid)

            # Send bot message.
            bot.send_message(chat_id=chat_id, text=_(CHANGED_MIND), reply_markup=bot_markup[language]['menu'])

        else:
            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_SET_LIMITS.value, config.db_state)

            # Get currency for formatting message.
            ad_payment_method = dbworker.get_current_state(chat_id, config.db_payment_method)

            if ad_payment_method == 'FIAT':
                currency = dbworker.get_current_state(chat_id, config.db_fiat_payment_currency)

            else:
                currency = ad_payment_method

            bot.send_message(chat_id=chat_id, text=_(AD_LIMITS).format(currency),
                             reply_markup=bot_markup[language]['back'])

    # Check result.
    elif result is False:
        # Set user's state.
        dbworker.set_state(chat_id, config.States.S_SET_AMOUNT.value, config.db_state)

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(INCORRECT_DATA), reply_markup=bot_markup[language]['back'])

    else:
        # If user edit ad amount. Else create ad.
        uuid_ = dbworker.get_current_state(chat_id, config.db_uuid)

        if uuid_ != '1':
            # Find ad amount and update.
            pymongodb.find_one_and_update({'uuid': uuid_}, {'ad_amount': ad_amount}, 'ads', '$set')

            # Del uuid from db.
            dbworker.delete(chat_id, config.db_uuid)

            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

            # Send bot message.
            bot.send_message(chat_id=chat_id, text=_(DONE), reply_markup=bot_markup[language]['menu'])

        else:
            # Generate uuid for ad.
            ad_uuid = uuid.uuid4()

            # Get user's ad data from db.
            ad_type = dbworker.get_current_state(chat_id, config.db_ad_type)
            ad_payment_method = dbworker.get_current_state(chat_id, config.db_payment_method)
            ad_price = dbworker.get_current_state(chat_id, config.db_fee_or_price)
            ad_status = 'OFF'
            ad_limits = dbworker.get_current_state(chat_id, config.db_limits)

            # Set ad type id.
            if ad_type == 'BUY':
                ad_type_id = 1

            elif ad_type == 'SELL':
                ad_type_id = 2

            else:
                ad_type_id = 3

            if ad_payment_method == 'FIAT':
                fiat_payment_currency = dbworker.get_current_state(chat_id, config.db_fiat_payment_currency)
                fiat_payment_method = dbworker.get_current_state(chat_id, config.db_fiat_payment_method)

                # Set exchange amount in db.
                pymongodb.insert_one({'user_id': user_id, 'uuid': str(ad_uuid), 'ad_type': ad_type,
                                      'ad_payment_method': ad_payment_method,
                                      'ad_fiat_payment_currency': fiat_payment_currency,
                                      'ad_fiat_payment_method': fiat_payment_method, 'ad_price': ad_price,
                                      'ad_amount': ad_amount, 'ad_status': ad_status, 'ad_type_id': ad_type_id,
                                      'ad_limits': ad_limits, 'username': username},  'ads')
                pymongodb.finish()

            else:
                # Set exchange amount in db.
                pymongodb.insert_one({'user_id': user_id, 'uuid': str(ad_uuid), 'ad_type': ad_type,
                                      'ad_payment_method': ad_payment_method, 'ad_price': ad_price,
                                      'ad_amount': ad_amount, 'ad_status': ad_status, 'ad_type_id': ad_type_id,
                                      'ad_limits': ad_limits, 'ad_crypto': 'crypto', 'username': username}, 'ads')
                pymongodb.finish()

            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

            # Delete ad payment method from db.
            for db in config.dbs_list:
                dbworker.delete(chat_id, db)

            # Send bot message.
            bot.send_message(chat_id=chat_id, text=SUCCESS_AD_CREATE, reply_markup=bot_markup[language]['menu'])
            bot.send_message(chat_id=chat_id, text=ADDITIONAL_INFO,
                             reply_markup=bot_markup[language]['inl_add_settings'])


# # Additional edit methods.
# Func which get user's message with user's ad conditions.
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_SET_CONDITIONS.value)
def set_conditions(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    conditions = message.text

    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    if conditions.startswith('⬅') is True:
        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(INCORRECT_DATA), reply_markup=bot_markup[language]['back'])

    else:
        # Get uuid from db.
        uuid_ = dbworker.get_current_state(chat_id, config.db_uuid)

        # Set conditions into db.
        pymongodb.find_one_and_update({'uuid': uuid_}, {'ad_conditions': conditions}, 'ads', '$set')

        # Set new user's state and delete uuid from db.
        dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)
        dbworker.delete(chat_id, config.db_uuid)

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(DONE), reply_markup=bot_markup[language]['menu'])


# # Additional edit methods.
# Func which get user's message with user's ad conditions.
@bot.message_handler(func=lambda message: dbworker.get_current_state(message.chat.id, config.db_state) == config.States.
                     S_SET_REQUISITES.value)
def set_requisites(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    requisites = message.text

    # Get document and language
    user_document = pymongodb.find_one({'user_id': user_id}, 'users')
    language = user_document['lang']

    # Get path and translate bot message.
    path = utils.get_path()

    trans_lang = gettext.translation('base', localedir=path, languages=[language])
    trans_lang.install()

    _ = trans_lang.gettext

    if requisites.startswith('⬅') is True:
        # Set new user's state.
        dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

        # Send bot message.
        bot.send_message(chat_id=chat_id, text=_(CHANGED_MIND), reply_markup=bot_markup[language]['menu'])

    else:
        # Get and delete uuid from db.
        uuid_ = dbworker.get_current_state(chat_id, config.db_uuid)

        # Get ad payment method.
        ad_payment_method = dbworker.get_current_state(chat_id, config.db_payment_method)

        # Check on payment method.
        if ad_payment_method == 'FIAT':
            # Set conditions into db.
            pymongodb.find_one_and_update({'uuid': uuid_}, {'ad_requisites': requisites}, 'ads', '$set')

            # Delete data from db.
            dbworker.delete(chat_id, config.db_uuid)
            dbworker.delete(chat_id, config.db_payment_method)

            # Set new user's state.
            dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

            # Send bot message.
            bot.send_message(chat_id=chat_id, text=_(DONE), reply_markup=bot_markup[language]['menu'])

        else:
            # Eject abbreviation , check address on valid.
            abbreviation = utils.eject_abbreviation(ad_payment_method)

            result = utils.check_crypto_address(abbreviation, requisites)

            # Check result.
            if result is not None:
                # Upsert requisites , delete data from vedis db, set new user's state, send bot message.
                pymongodb.find_one_and_update({'uuid': uuid_}, {'ad_requisites': requisites}, 'ads', '$set')

                dbworker.delete(chat_id, config.db_uuid)
                dbworker.delete(chat_id, config.db_payment_method)

                dbworker.set_state(chat_id, config.States.S_USE_MENU.value, config.db_state)

                bot.send_message(chat_id=chat_id, text=_(DONE), reply_markup=bot_markup[language]['menu'])

            # Incorrect data.
            else:
                # Send new user's state and send bot message.
                dbworker.set_state(chat_id, config.States.S_SET_REQUISITES.value, config.db_state)

                bot.send_message(chat_id=chat_id, text=_(INCORRECT_DATA), reply_markup=bot_markup[language]['back'])


# # Remove webhook, it fails sometimes the set if there is a previous webhook
# bot.remove_webhook()
#
# # Set webhook
# bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
#                 certificate=open(WEBHOOK_SSL_CERT, 'r'))
#
# # Build ssl context
# context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
# context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
#
# # Start aiohttp server
# web.run_app(
#     app,
#     host=WEBHOOK_LISTEN,
#     port=WEBHOOK_PORT,
#     ssl_context=context,
# )


def listener(messages):
    for m in messages:
        print(str(m))


bot.set_update_listener(listener)


bot.polling(none_stop=True)
