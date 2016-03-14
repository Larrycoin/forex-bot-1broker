#!/usr/bin/python

# start gui
gui = False

# candles chart time
BARS_TIME = "3600"

# broker data refresh thread sleep time 
BROKER_SLEEP_TIME = 3

# main algorithm loop sleep time
MAIN_SLEEP_TIME = 10

# assets on which this script trades
SYMBOLS = ["EURUSD", "EURGBP", "USDCAD", "USDJPY", "GBPUSD", "EURJPY", "AUDUSD", "USDCHF"]
# all symbols:
#BTCUSD, EURCHF, USDCAD, GBPUSD, EURGBP, EURJPY, EURNOK, EURSEK, EURUSD, NZDUSD, USDCNH, AUDNZD, AUDUSD, USDRUB, USDJPY, USDCHF, SILVER, GOLD, OILWTI, NFLX, MSFT, PEP, WU, TSLA, TWTR, BAC, V, VOW, KO, AAPL, BMW, BABA, F, FB, GOOG, GPRO, AMZN, INTC, CSCO, AU200, CH30, DAX, UK100, DOW, EU50, SP500, HK50, JP225

# margin used for single position, and leverage
MARGIN = "0.01"
LEVERAGE = "2"

# stop loss&take profit; in market change, multiply by leverage to get profit or loss %
# divided by leverage to get pure %
STOP_LOSS_PERCENT = round(0.75/float(LEVERAGE), 2)
TAKE_PROFIT_PERCENT = round(1.5/float(LEVERAGE), 2)

# your 1broker API token
API_KEY = "CHANGEME"

# old, trailing stop setting
FOLLOWING_STOP_MARGIN = 2000

running = True

STARTING_HIGHEST_PL = -FOLLOWING_STOP_MARGIN
current_position_highest_profitloss = STARTING_HIGHEST_PL

# 1broker
overview = ""
bars = {}
position = {}
orders = False
profitloss = 0
balance = 0
locked_balance = 0
total_btc = 0
sma5 = {}
sma20 = {}
prev_sma5 = {}
prev_sma20 = {}

# some stats
broker_fetch_count = 0
startup_balance = 0

# init
for symbol in SYMBOLS:
	sma5[symbol] = 0
	sma20[symbol] = 0
	prev_sma5[symbol] = 0
	prev_sma20[symbol] = 0
	position[symbol] = (False, False)

# logging
import logging
import logging.config
log_level = "DEBUG"
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': log_level,
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'level': "DEBUG",
            'filename': 'debug.log',
            'maxBytes': 2097152, # 2 MiB
            'backupCount': 10,
        },
        'file_info': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'level': "INFO",
            'filename': 'info.log',
            'maxBytes': 2097152, # 2 MiB
            'backupCount': 10,
        }
    },
    'loggers': {
        'console_only': {
            'handlers': ['console'],
            'propagate' : 0
        },
        'file_only': {
            'handlers': ['file'],
            'propagate' : 0
        },
        'both': {
            'handlers': ['console', 'file'],
            'propagate' : 0
        },
    },
    'root': {
        'level': log_level,
        'handlers': ['console', 'file', 'file_info'],
    },
})
