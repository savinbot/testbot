import gettext

from telebot import types
from utils import get_rate


_ = gettext.gettext

# # #

CURRENCY_DICT = {
    'ru': 'RUB',
    'eu': 'EUR',
    'en': 'USD',
}

# Names of currency inline buttons
CURRENCY_LIST = ['BTC', 'ETH', 'LTC', 'USD', 'EUR', 'RUB']  # in feed
CURRENCY_LIST_S = ['BTC_s', 'ETH_s', 'LTC_s', 'USD_s', 'EUR_s', 'RUB_s']    # in settings
CURRENCY_LIST_SUM = CURRENCY_LIST + CURRENCY_LIST_S

# Names of exchanges (used in Settings -> Rate STX)
EXCHANGES = ['CoinMarketCap']

# Payment currency list.
PAYMENT_CURRENCY_LIST = ['RUB', 'USD', 'EUR']

# Crypto payment list.
PAYMENT_METHODS_LIST = ['Bitcoin (BTC)', 'Ethereum (ETH)', 'Dogecoin (DOGE)']

# Fiat payment method list.
FIAT_PAYMENT_METHODS_LIST = ["Сбербанк", "Тинькофф", "QIWI", "Яндекс.Деньги", "Альфа-Банк", "ВТБ24", "РокетБанк",
                             "Русский стандарт", "WebMoney", "Кукуруза", "Advanced Cash", "Промсвязьбанк",
                             "Почта Банк", "Touch Банк", "Наличные в АТМ", "Авангард", "PAYEER",
                             "МТС-банк", "Газпромбанк", "Банк Москвы", "РНКБ", "Национальный банк", "Capitalist",
                             "Золотая корона", "Безнал (юр. лица)", "Уральский Банк (УБРиР)", "VISA", "Mastercard",
                             "С карты на карту", "Citibank", "LiqPay"]


# # # BOT MESSAGES

# RUSSIAN BOT MESSAGES

WELCOME = _("""
<b>Приветствую, {0}!</b> 

Это быстрый и бесплатный кошелек, а также сервис моментального обмена STX (Smartholdem).""")

FEEDBACK = _("""
Вы можете задать интересующие вопросы в @smartholdem""")

MENU_MESSAGE = _("""
⚠️ Внимание, ознакомьтесь! 

Вы оперируете деньгами, будьте внимательны. 

📲 Для обеспечения безопасности средств необходимо установить 'Two step verification' (2FA) в настройках Telegram и не передавать свой телефонный номер и любые секретные коды кому-либо (даже сотрудникам Telegram)!

Служба поддержки: https://community.smartholdem.io/categories""")

WALLET_TEXT = _("""
💼 Smartholdem кошелек

Баланс: {0} STH
Примерно: {5} {4}

За {1} дней вами проведено {2} успешных транзакций на общую сумму {3} STH.

🤝 Приглашено: 0 пользователей
💰 Заработано: 0 STH

Рейнтинг: (0)
""")

DEPOSIT = _("""
📥 Внести Smartholdem

Для пополнения STH с внешнего кошелька используйте многоразовый адерс ниже.

❕ Чтобы продать ваши STH следует пополнить личный кошелек по адресу ниже.

Средства поступают через 1 подтверждение сети.""")

WITHDRAWAL = _("""
👀 Неождиданно!

На вашем балансе недостаточно средств для вывода на внешний кошелек.

Мин. сумма: 10.1 STH.
Доступно: {0} STH""")


ATTENTION = _("""
⚠️<b>ВНИМАНИЕ</b>⚠️
В целях безопасности <b>обязательно удалите вручную вашу парольную фразу из переписки</b> с ботом!""")

INCORRECT_DATA = _("""
Введены некорректные данные. Попробуйте еще раз или используйте /menu, если хотите вернуться в главное меню.""")

SETTINGS = _("""
🛠 Настройки

Что Вы хотите изменить?

⚠️ Данные настройки установлены в соответствии с вашим изначальным выбором, но вы также можете их здесь изменить. """)

LANG = _("""
🌍 Язык

Выберите язык интерфейса. Смена языка не повлияет на отправленные ранее сообщения.""")

DONE = _("Сделано!")

CHANGED_MIND = _("Вы передумали.")

CANCELED = _("Отменено")

INPUT_RECIPIENT_ID = _("Введите адрес получателя:")

INPUT_AMOUNT = _("Введите количество монет для отправки (min 10 / max 100,000):")

INPUT_PAS = _("Введите вашу парольную фразу.")

SUCCESS_TX = _("Транзакция выполнена успешно.")

RATE = _("""
📊 Курс STX

Выберите источник актуального курса для пары STX/{}. Смена источника не повлияет на отправленные ранее сообщения.

Текущий источник: {}""")

CURRENCY = _("""
💵 Валюта

Выберите валюту. Этот фильтр влияет на отображение вашего баланса в кошельке.

Сейчас используется {}.""")

CONTACTS = _("""
💳 Адрес

Напишите адрес внешнего STX кошелька для быстрого доступа при выводе. """)

INPUT_ADDRESS_NAME = _("""
Введите имя для данного адреса.""")

YES = _("Да")

NO = _("Нет")

INPUT_CONTACT_NAME = _("Введите имя контакта из списка выше.")

CLEAR_CONTACT_LIST = _("""
📖 У вас не добавлен любимый адрес.

⚡ Чтобы добавить любимый адрес нажмите "Настройки" ➡️ "Адрес" ⚡""")

CHOOSE_CONTACT = _("Желаете использовать адрес из вашего списка контактов?")

ABOUT_SERVICE = _("""
🚀 О сервисе

Это место где можно хранить свои STX (Smartholdem), а также менять их на любую валюту через специальный обменный сервис.

У каждого есть возможность получать STX (Smartholdem) за привлечение новых участников с помощью партнеркской программы.""")

COMMUNICATION = _("""
👥 Общение

Свежие новости, инсайды и актуальные обсуждения в группах SMART BRO. Присоединяйтесь!""")


PARTNERS = _("""
👔 Партнерам

Приглашайте новых пользователей и получайте пассивный доход от комиссий бота! 💵 

Ваша комиссия от оборота: 2.5%

Например: ваш подписчик проводит сделку на сумму 1000 STX, а вы получаете 25 STX дивидендов. 

Партнерская программа бессрочна, не имеет лимита приглашений и начинает действовать моментально. 

Учтите, что для достижения хороших результатов необходимо внимательно подходить к поиску целевой аудитории и привлекать только тех, кто будет покупать, продавать, выводить STX и использовать миксер.

Используйте ссылку ниже для инвайта.

{}""")


# Exchange section.

EXCHANGE = _("""
📊 Купить/Продать STX

Здесь Вы совершаете сделки с людьми, а бот выступает как гарант.

Биржевой курс: {}""")

ZERO_ADS = _("""У вас еще нет ни одного объявления.""")

PAYMENT_METHOD_ERR = _("""
💸 Метод оплаты

⚠️ Сделки в данном разделе не проводятся автоматически , а только с участием эскроу.

В списке нет нужного вам метода оплаты? Скорее всего у вас уже есть такое объявление и его можно отредактировать.""")

PAYMENT_METHOD = _("""
💸 Метод оплаты

Выберите предпочитаемый метод оплаты.""")

RATE_STX_FEE = _("""
📊 Курс STX

На Localbitcoins: 1 STX = 8729.29 USD.

Установите курс STX для этого объявления. Вы можете ввести наценку в процентах или фиксированное значение. 

⚠️  Все возможные комиссии должны быть учтены в курсе объявления!  

Например: 0% или 8729.29""")

EX_AMOUNT = _("""Введите количество монет.""")

SUCCESS_AD_CREATE = _("""📰 Объявление создано!""")

ADDITIONAL_INFO = _("""
Вы можете добавить условия торговли к объявлению и другую информацию в дополнительных настройках.""")

MY_ANNOUNCEMENTS = _("""
📰 Мои объявления

Внизу отображается список ваших объявлений, где Вы продаете STX.

Биржевой курс: {}""")

ERROR_MAX_ADS = _("""
 🚫 Вы превысили максимальный лимит объявлений. Удалите неиспользуемые объявления.""")

ERROR_PAYMENT_METHOD = _("""
 🚫 Вы не можете иметь несколько объявлений с одиннаковым способом оплаты , выберите другой способ оплаты.""")

CURRENCY_CHOICE = _("""
Выберите предпочитаемую валюту.""")

AD_LIMITS = _("""
📐 Лимиты

Введите мин. и макс. сумму отклика в {}.
Например: 0.0001 - 1000000""")

INCORRECT_LIMITS = _("""
Неккоректный ввод!

Минимальная сумма отклика должна быть больше максимальной.""")

AD_DESCRIPTION = _("""
<b>📰 Мои объявления</b>

<b>Тип объявления:</b> {}
<b>Метод оплаты:</b> {}
<b>Цена STH:</b> {}
<b>Минимальная сумма:</b> {}
<b>Максимальная сумма:</b> {}
<b>Количество STH:</b> {}
<b>Статус:</b> {}

<b>Здесь вы можете изменить текущие условия торговли , детали объявления и другую информацию.</b>""")

AD_DESCRIPTION_WITH_CONDITIONS = _("""
<b>📰 Мои объявления</b>

<b>Тип объявления:</b> {}
<b>Метод оплаты:</b> {}
<b>Цена STH:</b> {}
<b>Минимальная сумма:</b> {}
<b>Максимальная сумма:</b> {}
<b>Количество STH:</b> {}
<b>Статус:</b> {}

<b>Условия торговли:</b>
{}

<b>Здесь вы можете изменить текущие условия торговли , детали объявления и другую информацию.</b>""")

AD_DESCRIPTION_WITH_REQUISITES = _("""
<b>📰 Мои объявления</b>

<b>Тип объявления:</b> {}
<b>Метод оплаты:</b> {}
<b>Цена STH:</b> {}
<b>Минимальная сумма:</b> {}
<b>Максимальная сумма:</b> {}
<b>Количество STH:</b> {}
<b>Статус:</b> {}

<b>Реквизиты для перевода:</b>
{}

<b>Здесь вы можете изменить текущие условия торговли , детали объявления и другую информацию.</b>""")

AD_DESCRIPTION_WITH_CONDITIONS_AND_REQUISITES = _("""
<b>📰 Мои объявления</b>

<b>Тип объявления:</b> {}
<b>Метод оплаты:</b> {}
<b>Цена STH:</b> {}
<b>Минимальная сумма:</b> {}
<b>Максимальная сумма:</b> {}
<b>Количество STH:</b> {}
<b>Статус:</b> {}

<b>Реквизиты для перевода:</b>
{}

<b>Условия торговли:</b>
{}

<b>Здесь вы можете изменить текущие условия торговли , детали объявления и другую информацию.</b>""")

AD_CONDITIONS = _("""
Напишите условия торговли, которые будут видны перед откликом.

⚠️  В объявлениях для электронных платежей недопускается осуществление территориальной привязки даже в случае дополнительных комиссий со стороны платежной системы. Все возможные комиссии должны быть учтены в курсе объявления.""")

AD_REQUISITES = _("""
Напишите реквизиты к объявлению.
Покупатель увидит этот текст уже после отклика.""")

AD_REQUISITES_CRYPTO = _("""
Введите адрес вашего {} кошелька.""")

CHOOSE_PAYMENT_METHOD_SELL = _("""
📉 Продать

Выберите удобный для Вас способ оплаты. Лучший курс и текущее количество заявок указаны рядом.

Биржевой курс: {} RUB
Баланс: 0 BTC""")

NONE_ADS = _("На данный момент нет доступных объявлений.")

CHOOSE_CRYPTO_PAYMENT_METHOD_SELL = _("""
📉 Продать

Выберите удобный для Вас способ оплаты в криптовалюте. Лучший курс и текущее количество заявок указаны рядом.

Биржевой курс: {} RUB
Баланс: 0 BTC""")

CHOOSE_FIAT_PAYMENT_METHOD_SELL = _("""
📉 Продать

Выберите удобный для Вас способ оплаты в криптовалюте. Лучший курс и текущее количество заявок указаны рядом.

Биржевой курс: {} RUB
Баланс: 0 BTC""")

CHOOSE_CURRENCY = _("""
Выберите валюту.

Выберите удобный для Вас способ оплаты в криптовалюте. Лучший курс и текущее количество заявок указаны рядом.""")

CHOOSE_PAYMENT_METHOD = _("""
Выберите способ оплаты.

Выберите удобный для Вас способ оплаты в криптовалюте. Лучший курс и текущее количество заявок указаны рядом.""")


# VIEW AD.
VIEW_BUY = _("""
📈 Купить (MoneyPolo)

За 561д. 20ч. @ALEXZXBTC провел 2298 успешных сделок на общую сумму 72.07848421 BTC.

Верификация: ✅ Документы
Рейтинг: ⭐️⭐️⭐️ (7996.05)
Отзывы: (3122)👍 (36)👎
Был в сети: 1ч. 29м.

Условия торговли:
MoneyPolo

Через это объявление можно купить BTC по курсу 7735.13 USD на сумму от 30 USD до 45.53 USD.
""")

VIEW_SELL = _("""
{} ({})

Контакты: {}
Рейтинг: 🏅 (124.1)
Отзывы: (38)👍 (0)👎

Реквизиты:
{}

Условия торговли:
{}

Эскроу: Эскроу1, Эскроу2""")

# Markup buttons.
WANT_BUY = _("📈 Вы хотите покупать STX")

WANT_SELL = _("📉 Вы хотите продавать STX")

CANCEL = _("❌ Отмена")

AD_TYPE = _("""Выберите тип объявления.""")

# Inline markup buttons.
# Ad editing buttons.
STH_RATE = _(" 📊 Цена STH")
CONDITIONS = _("📋 Условия")
REQUISITES = _("💳 Реквизиты")
LIMITS = _("📐 Лимиты")
AMOUNT = _(" 💎 Количество STH")
STATUS = _("{}")
BACK = _("Назад")

EDIT_BTNS_LIST = [[STH_RATE, 'ad_sth_rate'], [CONDITIONS, 'ad_conditions'], [REQUISITES, 'ad_requisites'],
                  [LIMITS, 'ad_limits'], [AMOUNT, 'ad_amount'], [BACK, 'back_to_ads_list']]


# # # BOT MARKUP

# Chose language
MARKUP_LANG = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
btn_en = types.KeyboardButton('🇺🇸 English')
btn_ru = types.KeyboardButton('🇷🇺 Русский')

MARKUP_LANG.add(btn_en, btn_ru)


# RUSSIAN

# # # Main menu
MARKUP_MENU = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

btn_wallet = types.KeyboardButton('💼 Кошелек')
btn_exchange_coins = types.KeyboardButton('📊 Обмен STH')
btn_about_service = types.KeyboardButton('🚀 О сервисе')
btn_settings = types.KeyboardButton('🛠️ Настройки')

MARKUP_MENU.add(btn_wallet, btn_exchange_coins, btn_about_service, btn_settings)


# Cancel button
CANCEL_MARKUP = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
cancel_btn = types.KeyboardButton('❌ Отмена')
CANCEL_MARKUP.add(cancel_btn)


# Markup Yes No Cancel
MARKUP_YES_NO = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
btn_yes = types.KeyboardButton('👌 Да')
btn_no = types.KeyboardButton('⛔ Нет')
MARKUP_YES_NO.add(btn_yes, btn_no, cancel_btn)


# Inline menu of wallet
MARKUP_INLINE_WALLET = types.InlineKeyboardMarkup()

btn_deposit = types.InlineKeyboardButton('📥 Внести', callback_data='deposit')
btn_withdrawal = types.InlineKeyboardButton('📤 Вывести', callback_data='withdrawal')
btn_send = types.InlineKeyboardButton('📨 Отправить', callback_data='send')

MARKUP_INLINE_WALLET.add(btn_deposit, btn_withdrawal, btn_send)


# Inline lang menu for user's choice
MARKUP_INLINE_LANG_CHOICE = types.InlineKeyboardMarkup(row_width=1)

btn_en = types.InlineKeyboardButton('🇺🇸 English', callback_data='en')
btn_ru = types.InlineKeyboardButton('🇷🇺 Русский', callback_data='ru')
btn_back = types.InlineKeyboardButton('⬅️Вернуться к настройкам', callback_data='back_to_settings')

MARKUP_INLINE_LANG_CHOICE.add(btn_en, btn_ru, btn_back)


# Inline back to settings
MARKUP_INLINE_BACK_TO_SET = types.InlineKeyboardMarkup(row_width=1)
btn_back_to_set = types.InlineKeyboardButton('⬅️Вернуться к настройкам', callback_data='back_to_settings')
MARKUP_INLINE_BACK_TO_SET.add(btn_back_to_set)


# Inline button select currency
MARKUP__INLINE_SEL_CURRENCY = types.InlineKeyboardMarkup(row_width=4)

btn_select_currency_f = types.InlineKeyboardButton('💵 Выбрать валюту', callback_data='select_currency_f')

MARKUP__INLINE_SEL_CURRENCY.add(btn_select_currency_f)


# # Inline menu of settings
MARKUP_INLINE_SETTINGS = types.InlineKeyboardMarkup(row_width=2)

btn_lang = types.InlineKeyboardButton('🌍 Язык', callback_data='lang')
btn_rate = types.InlineKeyboardButton('📊 Курс STX', callback_data='rate')
btn_address = types.InlineKeyboardButton('💳 Адрес', callback_data='address')
btn_select_currency_s = types.InlineKeyboardButton('💵 Выбрать валюту', callback_data='select_currency_s')

MARKUP_INLINE_SETTINGS.add(btn_lang, btn_rate, btn_address, btn_select_currency_s)


# !!
MARKUP_INLINE_CURRENCIES_F = types.InlineKeyboardMarkup(row_width=3)

btn_btc = types.InlineKeyboardButton('BTC', callback_data='BTC')
btn_eth = types.InlineKeyboardButton('ETH', callback_data='ETH')
btn_ltc = types.InlineKeyboardButton('LTC', callback_data='LTC')
btn_usd = types.InlineKeyboardButton('USD', callback_data='USD')
btn_eur = types.InlineKeyboardButton('EUR', callback_data='EUR')
btn_rub = types.InlineKeyboardButton('RUB', callback_data='RUB')
btn_back_feed = types.InlineKeyboardButton('⬅️Назад', callback_data='back_feed')

MARKUP_INLINE_CURRENCIES_F.add(btn_btc, btn_eth, btn_ltc, btn_usd, btn_eur, btn_rub, btn_back_feed)


# !!
MARKUP_INLINE_CURRENCIES_S = types.InlineKeyboardMarkup(row_width=3)

btn_btc_s = types.InlineKeyboardButton('BTC', callback_data='BTC_s')
btn_eth_s = types.InlineKeyboardButton('ETH', callback_data='ETH_s')
btn_ltc_s = types.InlineKeyboardButton('LTC', callback_data='LTC_s')
btn_usd_s = types.InlineKeyboardButton('USD', callback_data='USD_s')
btn_eur_s = types.InlineKeyboardButton('EUR', callback_data='EUR_s')
btn_rub_s = types.InlineKeyboardButton('RUB', callback_data='RUB_s')
btn_back_sett = types.InlineKeyboardButton('⬅️Назад', callback_data='back_sett')

MARKUP_INLINE_CURRENCIES_S.add(btn_btc_s, btn_eth_s, btn_ltc_s, btn_usd_s, btn_eur_s, btn_rub_s, btn_back_sett)


# # SERVICE SECTION

# About service menu
M_INLINE_SERVICE_MENU = types.InlineKeyboardMarkup(row_width=2)

btn_communication = types.InlineKeyboardButton('👥 Общение', callback_data="talks")
btn_support = types.InlineKeyboardButton('💬 Поддержка', callback_data="support", url='https://t.me/devbrain')
btn_partners = types.InlineKeyboardButton('👔 Партнерам', callback_data="partners")
btn_friends = types.InlineKeyboardButton('☕ Друзья', callback_data="friends")

M_INLINE_SERVICE_MENU.add(btn_communication, btn_support, btn_partners, btn_friends)


# Talks menu
M_INLINE_TALKS_MENU = types.InlineKeyboardMarkup(row_width=2)

btn_world = types.InlineKeyboardButton('🌍 World chat', callback_data="world_chat", url='https://t.me/devbrain')
btn_ru_chat = types.InlineKeyboardButton('🇷🇺 Рус. группа', callback_data="ru_chat", url='https://t.me/devbrain')
btn_smart_news = types.InlineKeyboardButton("☕ News channel", callback_data="news_channel", url='https://t.me/devbrain')
back_to_service = types.InlineKeyboardButton("⬅️ Назад", callback_data="back_to_service")

M_INLINE_TALKS_MENU.add(btn_world, btn_ru_chat, btn_smart_news, back_to_service)


# Back to about service
M_INLINE_BACK_TO_SERVICE = types.InlineKeyboardMarkup(row_width=1)
M_INLINE_BACK_TO_SERVICE.add(back_to_service)


# # # EXCHANGE SECTION
# # Inline markups.
# Exchange.
M_INLINE_EXCHANGE = types.InlineKeyboardMarkup(row_width=2)

buy = types.InlineKeyboardButton("📈 Купить", callback_data="SELL")
sell = types.InlineKeyboardButton("📉 Продать", callback_data="BUY")
my_announcements = types.InlineKeyboardButton("📔 Мои объявления", callback_data="my_announcements")

M_INLINE_EXCHANGE.add(buy, sell, my_announcements)


# My ads.
M_INLINE_ADD_AD = types.InlineKeyboardMarkup(row_width=1)
add_ad = types.InlineKeyboardButton("📝 Добавить объявление", callback_data="add_ad")
M_INLINE_ADD_AD.add(add_ad)


# # Simple markups.
# Add ad.
MARKUP_TYPE_AD = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

want_buy = types.KeyboardButton("📈 Вы хотите покупать STX")
want_sell = types.KeyboardButton("📉 Вы хотите продавать STX")

MARKUP_TYPE_AD.add(want_buy, want_sell, cancel_btn)

# Back.
MARKUP_BACK = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
back = types.KeyboardButton("⬅️ Назад")
MARKUP_BACK.add(back)

# Want buy sell.
MARKUP_PAYMENT_METHOD = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

btc_btn = types.KeyboardButton("Bitcoin (BTC)")
eth_btn = types.KeyboardButton("Ethereum (ETH)")
doge_btn = types.KeyboardButton("Dogecoin (DOGE)")
fiat_btn = types.KeyboardButton("Fiat")

MARKUP_PAYMENT_METHOD.add(doge_btn, btc_btn, eth_btn, fiat_btn, back)

# # Inline markups.
# Additional settings for ad.
MARKUP_INL_ADD_SETTINGS = types.InlineKeyboardMarkup(row_width=1)
add_settings_btn = types.InlineKeyboardButton('⚙️ Доп. настройки', callback_data='add_settings')
MARKUP_INL_ADD_SETTINGS.add(add_settings_btn)

# ENGLISH

# Main menu
MARKUP_MENU_EN = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

btn_wallet_en = types.KeyboardButton('💼 Wallet')
btn_exchange_coins_en = types.KeyboardButton('📊 Buy/Sell STX')
btn_about_service_en = types.KeyboardButton('🚀 About')
btn_settings_en = types.KeyboardButton('🛠️ Settings')

MARKUP_MENU_EN.add(btn_wallet_en, btn_exchange_coins_en, btn_about_service_en, btn_settings_en)


# Cancel button
CANCEL_ENG_MARKUP = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
cancel_btn_eng = types.KeyboardButton('❌ Cancel')
CANCEL_ENG_MARKUP.add(cancel_btn_eng)


# Markup Yes No Cancel
MARKUP_YES_NO_ENG = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
btn_yes_en = types.KeyboardButton('👌 Yes')
btn_no_en = types.KeyboardButton('⛔ No')
MARKUP_YES_NO_ENG.add(btn_yes_en, btn_no_en, cancel_btn_eng)


# # Inline menu of wallet
MARKUP_INLINE_WALLET_ENG = types.InlineKeyboardMarkup()

btn_deposit_en = types.InlineKeyboardButton('📥 Deposit', callback_data='deposit')
btn_withdrawal_en = types.InlineKeyboardButton('📤 Withdrawal', callback_data='withdrawal')
btn_send_en = types.InlineKeyboardButton('📨 Send', callback_data='send')

MARKUP_INLINE_WALLET_ENG.add(btn_deposit_en, btn_withdrawal_en, btn_send_en)


# Inline lang menu for user's choice
MARKUP_INLINE_LANG_CHOICE_ENG = types.InlineKeyboardMarkup(row_width=1)

btn_en_eng = types.InlineKeyboardButton('🇺🇸 English', callback_data='en')
btn_ru_eng = types.InlineKeyboardButton('🇷🇺 Русский', callback_data='ru')
btn_back_eng = types.InlineKeyboardButton('⬅️Back to settings', callback_data='back_to_settings')

MARKUP_INLINE_LANG_CHOICE_ENG.add(btn_en_eng, btn_ru_eng, btn_back_eng)


# Inline back to settings
MARKUP_INLINE_BACK_TO_SET = types.InlineKeyboardMarkup(row_width=1)
btn_back_to_set_eng = types.InlineKeyboardButton('⬅️Back to settings', callback_data='back_to_settings')
MARKUP_INLINE_BACK_TO_SET.add(btn_back_to_set_eng)


# Inline button select currency
MARKUP__INLINE_SEL_CURRENCY_ENG = types.InlineKeyboardMarkup(row_width=4)

btn_select_currency_f_eng = types.InlineKeyboardButton('💵 Select currency', callback_data='select_currency_f')

MARKUP__INLINE_SEL_CURRENCY_ENG.add(btn_select_currency_f_eng)


# Inline menu of settings
MARKUP_INLINE_SETTINGS_ENG = types.InlineKeyboardMarkup(row_width=2)

btn_lang_eng = types.InlineKeyboardButton('🌍 Language', callback_data='lang')
btn_rate_eng = types.InlineKeyboardButton('📊 Rate STX', callback_data='rate')
btn_address_eng = types.InlineKeyboardButton('💳 Address', callback_data='address')
btn_select_currency_s_eng = types.InlineKeyboardButton('💵 Select currency', callback_data='select_currency_s')

MARKUP_INLINE_SETTINGS_ENG.add(btn_lang_eng, btn_rate_eng, btn_address_eng, btn_select_currency_s_eng)


# !!
MARKUP_INLINE_CURRENCIES_F_ENG = types.InlineKeyboardMarkup(row_width=3)

btn_btc = types.InlineKeyboardButton('BTC', callback_data='BTC')
btn_eth = types.InlineKeyboardButton('ETH', callback_data='ETH')
btn_ltc = types.InlineKeyboardButton('LTC', callback_data='LTC')
btn_usd = types.InlineKeyboardButton('USD', callback_data='USD')
btn_eur = types.InlineKeyboardButton('EUR', callback_data='EUR')
btn_rub = types.InlineKeyboardButton('RUB', callback_data='RUB')
btn_back_feed_eng = types.InlineKeyboardButton('⬅️Back', callback_data='back_feed')

MARKUP_INLINE_CURRENCIES_F_ENG.add(btn_btc, btn_eth, btn_ltc, btn_usd, btn_eur, btn_rub, btn_back_feed_eng)


# !!
MARKUP_INLINE_CURRENCIES_S_ENG = types.InlineKeyboardMarkup(row_width=3)

btn_btc_s = types.InlineKeyboardButton('BTC', callback_data='BTC_s')
btn_eth_s = types.InlineKeyboardButton('ETH', callback_data='ETH_s')
btn_ltc_s = types.InlineKeyboardButton('LTC', callback_data='LTC_s')
btn_usd_s = types.InlineKeyboardButton('USD', callback_data='USD_s')
btn_eur_s = types.InlineKeyboardButton('EUR', callback_data='EUR_s')
btn_rub_s = types.InlineKeyboardButton('RUB', callback_data='RUB_s')
btn_back_sett_eng = types.InlineKeyboardButton('⬅️Back', callback_data='back_sett')

MARKUP_INLINE_CURRENCIES_S_ENG.add(btn_btc_s, btn_eth_s, btn_ltc_s, btn_usd_s, btn_eur_s, btn_rub_s, btn_back_sett_eng)


# # SERVICE SECTION

# About service menu INLINE
M_INLINE_SERVICE_MENU_ENG = types.InlineKeyboardMarkup(row_width=2)

btn_communication_en = types.InlineKeyboardButton('👥 Talks', callback_data="talks")
btn_support_en = types.InlineKeyboardButton('💬 Support', callback_data="support")
btn_partners_en = types.InlineKeyboardButton('👔 Affiliate', callback_data="partners")
btn_friends_en = types.InlineKeyboardButton('☕ Friends', callback_data="friends")

M_INLINE_SERVICE_MENU_ENG.add(btn_communication_en, btn_support_en, btn_partners_en, btn_friends_en)


# Talks menu INLINE
M_INLINE_TALKS_MENU_ENG = types.InlineKeyboardMarkup(row_width=2)

back_to_service_en = types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_service")

M_INLINE_TALKS_MENU_ENG.add(btn_world, btn_ru_chat, btn_smart_news, back_to_service_en)


# Back to about service
M_INLINE_BACK_TO_SERVICE_ENG = types.InlineKeyboardMarkup(row_width=1)
M_INLINE_BACK_TO_SERVICE_ENG.add(back_to_service_en)


# # # EXCHANGE SECTION
# # Inline markups.
# Exchange.
M_INLINE_EXCHANGE_ENG = types.InlineKeyboardMarkup(row_width=2)

buy_en = types.InlineKeyboardButton("📈 Buy", callback_data="buy")
sell_en = types.InlineKeyboardButton("📉 Sell", callback_data="sell")
my_announcements_en = types.InlineKeyboardButton("📔 My ads", callback_data="my_announcements")

M_INLINE_EXCHANGE_ENG.add(buy_en, sell_en, my_announcements_en)


# My ads.
M_INLINE_ADD_AD_ENG = types.InlineKeyboardMarkup(row_width=1)
add_ad_en = types.InlineKeyboardButton("📝 Add announcements", callback_data="add_ad")
M_INLINE_ADD_AD_ENG.add(add_ad_en)

# # Simple markups.
# Add ad.
MARKUP_TYPE_AD_ENG = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

want_buy_en = types.KeyboardButton("📈 You want to buy STX")
want_sell_en = types.KeyboardButton("📉 You want to sell STX")

MARKUP_TYPE_AD_ENG.add(want_buy_en, want_sell_en, cancel_btn_eng)


# Back.
MARKUP_BACK_ENG = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
back_en = types.KeyboardButton("⬅️ Back")
MARKUP_BACK_ENG.add(back)


# Want buy sell.
MARKUP_PAYMENT_METHOD_ENG = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
MARKUP_PAYMENT_METHOD_ENG.add(doge_btn, btc_btn, eth_btn, back_en)

# # Inline markups.
MARKUP_INL_ADD_SETTINGS_ENG = types.InlineKeyboardMarkup(row_width=1)
add_settings_btn_en = types.InlineKeyboardButton('⚙️ Additional settings', callback_data='add_settings')
MARKUP_INL_ADD_SETTINGS_ENG.add(add_settings_btn)


# Bot Markup
bot_markup = {'ru': {'menu': MARKUP_MENU, 'inline_wallet_menu': MARKUP_INLINE_WALLET,
                     'inl_settings': MARKUP_INLINE_SETTINGS, 'inl_lang_choice': MARKUP_INLINE_LANG_CHOICE,
                     'cancel': CANCEL_MARKUP, 'back_to_set': MARKUP_INLINE_BACK_TO_SET,
                     'select_currency': MARKUP__INLINE_SEL_CURRENCY, 'currency_f': MARKUP_INLINE_CURRENCIES_F,
                     'currency_s': MARKUP_INLINE_CURRENCIES_S, 'yes_no': MARKUP_YES_NO,
                     'service_menu': M_INLINE_SERVICE_MENU, 'talks': M_INLINE_TALKS_MENU,
                     'back_to_service': M_INLINE_BACK_TO_SERVICE, 'exchange': M_INLINE_EXCHANGE,
                     'inl_add_ad': M_INLINE_ADD_AD, 'ad_type': MARKUP_TYPE_AD, 'payment_method': MARKUP_PAYMENT_METHOD,
                     'back': MARKUP_BACK, 'inl_add_settings': MARKUP_INL_ADD_SETTINGS},
              'en': {'menu': MARKUP_MENU_EN, 'inline_wallet_menu': MARKUP_INLINE_WALLET_ENG,
                     'inl_settings': MARKUP_INLINE_SETTINGS_ENG, 'inl_lang_choice': MARKUP_INLINE_LANG_CHOICE_ENG,
                     'cancel': CANCEL_ENG_MARKUP, 'back_to_set': MARKUP_INLINE_BACK_TO_SET,
                     'select_currency': MARKUP__INLINE_SEL_CURRENCY_ENG, 'currency_f': MARKUP_INLINE_CURRENCIES_F_ENG,
                     'currency_s': MARKUP_INLINE_CURRENCIES_S_ENG, 'yes_no': MARKUP_YES_NO_ENG,
                     'service_menu': M_INLINE_SERVICE_MENU_ENG, 'talks': M_INLINE_TALKS_MENU_ENG,
                     'back_to_service': M_INLINE_BACK_TO_SERVICE_ENG, 'exchange': M_INLINE_EXCHANGE_ENG,
                     'inl_add_ad': M_INLINE_ADD_AD_ENG, 'ad_type': MARKUP_TYPE_AD_ENG,
                     'payment_method': MARKUP_PAYMENT_METHOD_ENG, 'back': MARKUP_BACK_ENG,
                     'inl_add_settings': MARKUP_INL_ADD_SETTINGS_ENG,}
              }


# Intersection
def markup_inline_rate(currency):
    price_per_one = float(get_rate(currency))     # price per one STX coin
    list_ = ['BTC', 'ETH', 'LTC']

    if currency in list_:
        coinmarketcap = 'CoinMarketCap ({0:.6f} {1})'.format(price_per_one, currency)
    else:
        coinmarketcap = 'CoinMarketCap ({0:.2f} {1})'.format(price_per_one, currency)

    markup_inline_rate = types.InlineKeyboardMarkup(row_width=1)
    btn_coinmarketcap = types.InlineKeyboardButton(coinmarketcap, callback_data='CoinMarketCap')
    markup_inline_rate.add(btn_coinmarketcap, btn_back_to_set)

    return markup_inline_rate
