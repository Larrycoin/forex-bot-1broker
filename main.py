#!/usr/bin/python
import API1brokerlib
import shared
try:
    import qt
except ImportError:
    shared.gui = False# qt not available

import json
import urllib2
import time
import datetime
import threading
import logging

def broker_update():
    broker = API1brokerlib.Connection(shared.API_KEY, 2)
    logging.debug("Updating 1broker info (overview).")
    shared.broker_fetch_count += 1
    overview = broker.account_overview()
    
    # check if failed
    if overview == False:
        logging.error("Error when updating 1broker info.")
        return False
    shared.overview = overview
     
    # calc P/L (DEPRECATED)
    shared.profitloss = int((float(overview['response']['positions_worth_btc'])-float(shared.MARGIN))*100000000)
    
    # remove positions data (in case of SL/TP)
    logging.debug("Clearing positions data.")
    for symbol in shared.SYMBOLS:
        shared.position[symbol] = (False, False)
    
    # check for open positions for all pairs
    logging.debug("Getting positions data.")
    for position in overview['response']['positions_open']:
        position_str = "Value: "+str(position['value'])+"; P/L: "+str(position['profit_loss'])
        if position['direction'] == "long":
            logging.debug(position['symbol']+": There is a long position open. "+position_str)
            shared.position[position['symbol']] = ("long", position['position_id'])
        elif position['direction'] == "short":
            logging.debug(position['symbol']+": There is a short position open. "+position_str)
            shared.position[position['symbol']] = ("short", position['position_id'])
        else:
            logging.debug(position['symbol']+": There is no position open. "+position_str)
            shared.position[position['symbol']] = (False, False)
    
    # get more data - balance, locked balance, total btc, open orders
    shared.balance = overview['response']['balance_btc']
    if shared.startup_balance == 0:
        shared.startup_balance = shared.balance
    shared.locked_balance = overview['response']['positions_worth_btc']
    shared.total_btc = overview['response']['net_worth_btc']
    
    # open orders
    if len(overview['response']['orders_open']) == 0:
        shared.orders = False
        logging.debug("No open orders.")
    else:
        shared.orders = True
        logging.debug("There is an order opened.")

    # get data for all symbols (bars, smas)
    for symbol in shared.SYMBOLS:
        # get bars
        logging.debug("Updating 1broker info (bars) for "+symbol+".")
        shared.broker_fetch_count += 1
        bars = broker.market_get_bars(symbol, shared.BARS_TIME)
        # check if ok
        if bars == False:
            logging.error("Error when updating 1broker info (bars).")
            return False
        shared.bars[symbol] = bars
        
        # SMA formula
        def calculate_sma(sma_range, delay=0):
            sma = 0
            for x in range(1+delay, sma_range+1+delay):
                sma += float(bars['response'][-x]['c'])
            return sma/sma_range
           
        # update SMAs
        shared.prev_sma5[symbol] = calculate_sma(5, 1)
        shared.prev_sma20[symbol] = calculate_sma(10, 1)
        shared.sma5[symbol] = calculate_sma(5)
        shared.sma20[symbol] = calculate_sma(10)
        
def main_algo():
    # for all pairs
    for symbol in shared.SYMBOLS:
        logging.debug("Main algorithm started for "+symbol+".")
    
        smas_str =  "SMA5: "+str(shared.sma5[symbol])+", SMA20: "+str(shared.sma20[symbol])+", prev SMA5: "+str(shared.prev_sma5[symbol])+", prev SMA20: "+str(shared.prev_sma20[symbol])
        # calculate crosses; if not initialized, do nothing
        if shared.sma5[symbol] == 0 or shared.sma20[symbol] == 0 or shared.prev_sma5[symbol] == 0 or shared.prev_sma20[symbol] == 0:
            logging.debug(symbol+": Crosses not yet initialized. ("+smas_str+")")
            cross = 0
        else:
            # fast crosses over slow
            if shared.sma5[symbol] > shared.sma20[symbol] and shared.prev_sma5[symbol] <= shared.prev_sma20[symbol]:
                cross = 1
                logging.debug(symbol+": Fast SMA crosses over slow. ("+smas_str+")")
            # fast crosses below slow
            elif shared.sma5[symbol] < shared.sma20[symbol] and shared.prev_sma5[symbol] >= shared.prev_sma20[symbol]:
                cross = -1
                logging.debug(symbol+": Fast SMA crosses below slow. ("+smas_str+")")
            # no crosses
            else:
                cross = 0
                logging.debug(symbol+": No crosses. ("+smas_str+")")
        
        # we need 1broker connection
        broker = API1brokerlib.Connection(shared.API_KEY, 1)
                
        # trailing stop TODO: set stop loss
        #if shared.profitloss > shared.current_position_highest_profitloss and shared.position != False:
        #    shared.current_position_highest_profitloss = shared.profitloss
        #    logging.info("Raising highest_profitloss to "+str(shared.profitloss))
        #if shared.current_position_highest_profitloss > shared.profitloss+shared.FOLLOWING_STOP_MARGIN and shared.position != False:
        #    broker.position_edit(int(shared.overview['response']['positions_open'][0]['position_id']), market_close="true")
        #    # reset highest P/L
        #    shared.current_position_highest_profitloss = shared.STARTING_HIGHEST_PL
        #    logging.info("Closed position by following stop. P/L: "+str(shared.profitloss))
            
        # real algo
        if cross == -1:
            # close long position, if open
            if shared.position[symbol][0] == "long":
                broker.position_edit(int(shared.position[symbol][1]), market_close="true")
                logging.info(symbol+": Closed long position: cross. P/L: "+str(shared.profitloss))
                shared.position[symbol] = (False, False)# reset position info; I think we dont need any of this anymore
        if cross == 1:
            # close short position, if open
            if shared.position[symbol][0] == "short":
                broker.position_edit(int(shared.position[symbol][1]), market_close="true")
                logging.info(symbol+": Closed short position: cross. P/L: "+str(shared.profitloss))
                shared.position[symbol] = (False, False)
        if cross == -1:
            # open short position, if not opened and if no open orders
            if shared.position[symbol][0] == False and shared.orders == False:
                rate = float(shared.bars[symbol]['response'][-1]['c'])
                stop_loss = rate+rate*shared.STOP_LOSS_PERCENT/100
                take_profit = rate-rate*shared.TAKE_PROFIT_PERCENT/100
                broker.order_create(symbol, shared.MARGIN, "short", shared.LEVERAGE, "Market", stop_loss=float(stop_loss), take_profit=float(take_profit))
                logging.info(symbol+": Opened short position, SL: "+str(stop_loss)+", TP: "+str(take_profit))
                shared.position[symbol] = ("short", True)
        if cross == 1:
            # open long position, if not opened and if no open orders
            if shared.position[symbol][0] == False and shared.orders == False:
                rate = float(shared.bars[symbol]['response'][-1]['c'])
                stop_loss = rate-rate*shared.STOP_LOSS_PERCENT/100
                take_profit = rate+rate*shared.TAKE_PROFIT_PERCENT/100
                broker.order_create(symbol, shared.MARGIN, "long", shared.LEVERAGE, "Market", stop_loss=float(stop_loss), take_profit=float(take_profit))
                logging.info(symbol+": Opened long position, SL: "+str(stop_loss)+", TP: "+str(take_profit))
                shared.position[symbol] = ("long", True)
        if cross == 0:
            # do nothing
            logging.debug("No crosses - doing nothing.")

def main_thread():
    logging.info("Initializing main daemon.")
    while shared.running == True:
        try:
            broker_update()
            main_algo()
            logging.debug("Sleeping for "+str(shared.MAIN_SLEEP_TIME)+" sec.")
            time.sleep(shared.MAIN_SLEEP_TIME)
        except:
            logging.error("Unknown error occurred.")
    logging.debug("Main thread exited cleanly.")

def main():
    try:
        # run all threads
        threading.Thread(target=main_thread).start()
        
        # start qt
        if shared.gui == True:
            ui = qt.UserInterface()
            ui.run()
            ui.ui_exit()
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        logging.warning("Keyboard interrupt")
        shared.running = False
        quit()

if __name__ == "__main__":
    main()
