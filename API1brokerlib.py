#!/usr/bin/python
import urllib2
import json
import time

# urllib2 header
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
'Accept-Encoding': 'none',
'Accept-Language': 'en-US,en;q=0.8',
'Connection': 'keep-alive'}

# referral ID
ref = 3727

class Connection:
    
    token = ""
    delay = 0
    
    def __init__(self, API_key, delay=0):
        self.token = API_key
        self.delay = delay

    # runs any of the requests specified later
    def request_1b(self, site):
        try:
            request = urllib2.Request(site, headers=hdr)
            page = urllib2.urlopen(request)
            time.sleep(self.delay)
            content = page.read()
            view = json.loads(content)
            return view
        except:
            return False
    
    # 1brokers API full python implementation (for API 1.3)  
    def account_overview(self):
        site = "https://1broker.com/api/v1/account/overview.php?token=%s" % self.token
        return self.request_1b(site)
        
    def account_info(self):
        site = "https://1broker.com/api/v1/account/info.php?token=%s" % self.token
        return self.request_1b(site)
    
    def account_bitcoin_deposit_address(self):
        site = "https://1broker.com/api/v1/account/bitcoin_deposit_address.php?token=%s" % self.token
        return self.request_1b(site)
        
    def order_list_open(self):
        site = "https://1broker.com/api/v1/order/list_open.php?token=%s" % self.token
        return self.request_1b(site)
        
    def order_create(self, symbol, margin, direction, leverage, order_type, order_type_parameter=None, stop_loss=None, take_profit=None, referral_id=ref):
        site = "https://1broker.com/api/v1/order/create.php?symbol=%s&margin=%s&direction=%s&leverage=%s&order_type=%s&token=%s&referral_id=%s" % (symbol, margin, direction, leverage, order_type, self.token, referral_id)
        if stop_loss:
            site = "%s&stop_loss=%s" % (site, stop_loss)
        if take_profit:
            site = "%s&take_profit=%s" % (site, take_profit)
        if order_type is "Market":
            site = "%s&order_type=Market" % site
        else:
            site = "%s&order_type=%s&order_type_parameter=%s" % (site, order_type, order_type_parameter)
        return self.request_1b(site)

    def order_cancel(self, order_id):
        site = "https://1broker.com/api/v1/order/cancel.php?order_id=%d&token=%s" % (order_id, self.token)
        return self.request_1b(site)

    def position_list_open(self):
        site = "https://1broker.com/api/v1/position/list_open.php?token=%s" % self.token
        return self.request_1b(site)
        
    def position_list_history(self, limit=None, offset=None):
        site = "https://1broker.com/api/v1/position/list_history.php?token=%s" % self.token
        if limit:
            site = "%s&limit=%s" % (site, limit)
        if offset:
            site = "%s&offset=%s" % (site, offset)
        return self.request_1b(site)

    def position_edit(self, position_id, market_close=None, stop_loss=None, take_profit=None):
        site = "https://1broker.com/api/v1/position/edit.php?&token=%s&position_id=%d" % (self.token, position_id)
        if market_close:
            site = "%s&market_close=%s" % (site, market_close)
        if stop_loss:
            site = "%s&stop_loss=%s" % (site, stop_loss)
        if take_profit:
            site = "%s&take_profit=%s" % (site, take_profit)
        return self.request_1b(site)

    def market_list(self):
        site = "https://1broker.com/api/v1/market/list.php?token=%s" % self.token
        return self.request_1b(site)
        
    def market_detail(self, symbol):
        site = "https://1broker.com/api/v1/market/detail.php?token=%s&symbol=%s" % (self.token, symbol)
        return self.request_1b(site)

    def market_quotes(self, symbols):
        site = "https://1broker.com/api/v1/market/quotes.php?token=%s&symbols=%s" % (self.token, symbols)
        return self.request_1b(site)
    
    def market_get_bars(self, symbol, resolution, from_time=None, to_time=None):
        site = "https://1broker.com/api/v1/market/get_bars.php?token=%s&symbol=%s&resolution=%s" % (self.token, symbol, resolution)
        if from_time:
            site = "%s&from=%s" % (site, from_time)
        if to_time:
            site = "%s&to=%s" % (site, to_time)
        return self.request_1b(site)
