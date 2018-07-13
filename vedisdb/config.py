# -*- coding: utf-8 -*-

import os
import sys

from enum import Enum

# # Get path
path = sys.argv[0]
path = os.path.join(os.path.dirname(path), 'data')

# DB state.
db_state = path + '/db_state.vdb'

# DB lang.
db_language = path + '/db_language.vdb'

# DB's ads data.
db_ad_type = path + '/db_ad_type.vdb'
db_payment_method = path + '/db_payment_method.vdb'
db_fiat_payment_currency = path + '/db_fiat_payment_currency.vdb'
db_fiat_payment_method = path + '/db_fiat_payment_method.vdb'
db_fee_or_price = path + '/db_fee_or_price.vdb'
db_set_amount = path + '/db_amount.vdb'
db_limits = path + '/db_amount.vdb'

# DB's ads edit.
db_uuid = path + '/db_uuid.vdb'

# DB choice in exchange menu.
db_ex_choice = path + '/db_ex_choice.vdb'
db_ex_choice_currency = path + '/db_ex_choice_currency.vdb'
db_ex_choice_payment_method = path + '/db_ex_choice_payment_method.vdb'
db_ex_current_page = path + '/db_ex_current_page.vdb'

# DB cached data (output ads).
db_data_cache = path + '/db_data_cache.vdb'

# List of DBs.
dbs_list = [db_ad_type, db_ad_type, db_payment_method, db_fiat_payment_currency, db_fiat_payment_method,
            db_fee_or_price, db_set_amount, db_limits, db_uuid]


class States(Enum):
    # Users states values.
    S_USE_CHOOSE_LANG = "0"
    S_USE_MENU = "1"
    S_USE_ADDRESS_FROM_CONTACTS = "2"
    S_GET_AMOUNT = "3"
    S_GET_RECIPIENT_ID = "4"
    S_GET_PAS = "5"
    S_ADD_FAVORITE_ADDRESS = "6"
    S_CHOSE_AD_TYPE = "7"
    S_CHOOSE_PAYMENT_METHOD = "8"
    S_CHOOSE_FEE_OR_PRICE = "9"
    S_SET_AMOUNT = "10"
    S_SET_FIAT_PAYMENT_METHOD = "11"
    S_SET_PAYMENT_CURRENCY = "12"
    S_SET_LIMITS = "13"
    S_SET_CONDITIONS = "14"
    S_SET_REQUISITES = "15"
