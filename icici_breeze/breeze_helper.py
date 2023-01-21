from breeze_connect import BreezeConnect
import dateUtil
from CalculateTA import CalcData
from datetime import datetime, timedelta
import os
import pandas as  pd
#import numpy as np
from config import Config
from levels import BuySell, ORDER_STATUS
#import statsmodels.api as sm
import log_util as log_util
import logging
import fileutil
import dalc
import calendar
import time
import json
#import redis_util as r

class HelperBreeze(): #BrokerHelper
    date_format = "%Y-%m-%d"
    broker = 'breeze'
    df=None
    kws=None
    vals = {}
    intervals = {1: "1minute", 5: "5minute", 15:"15minute", 1440:"1day"}
    logging.basicConfig(filename='app.log', level=logging.INFO, filemode='a', format='%(name)s - %(levelname)s - %(message)s')
    def __init__(self, userid=''):

        self.cfg = Config()
        self.testing = self.cfg.TESTING
        self.userid = Context.userid if userid == '' else userid
        log_util.debug (f"inside:: self testing: {self.testing}, userid: {self.userid}")
        self.cred = dalc.get_authen(self.userid)
        #self.cred = {"apikey": "954g5835lv234U^73~U0251026q8w14a", "apisecret": "*2Yr8J1K241q70)1w4nMI7_969733870", "accesstoken": "2347099"}
        breeze = BreezeConnect(api_key=self.cred['apikey'])
        breeze.generate_session(api_secret=self.cred['apisecret'],
                        session_token=self.cred['accesstoken'])
        self.client = breeze
        self.issue=False

    def setIssue(self, new_issue_status):
        if self.issue != new_issue_status:
            #TODO: update the issue column
            pass

    def getPositions(self):
        return helper.client.get_portfolio_positions()
        #return dalc.get_strikes_watch(self.userid)

    def writelogdb(self, position, close_type, close_price, close_at_time):
        pass

    def getInstruments (self):
        if self.df is None:
            filename=fileutil.getNamedTempFile("instruments_{d}.csv".format(d=datetime.now().date()), touch=False)
            if not os.path.exists(filename):
                instrument_dump = self.client.instruments("NFO")
                self.df = pd.DataFrame(instrument_dump)
                self.df.to_csv(filename,index=False)
                time.sleep(2)
            self.df= pd.read_csv(filename)
        return self.df

    def getSymbol(self, token):
        df=self.getInstruments()
        try:
            return df[df.instrument_token==token].tradingsymbol.values[0]
        except:
            return -1

    def instrumentLookup(self, symbol):
        """Looks up instrument token for a given script from instrument dump"""
        df=self.getInstruments()
        try:
            return df[df.tradingsymbol==symbol].instrument_token.values[0]
        except:
            return -1

    def getToken(self, symbol, pece, strikeprice, expirydate):
        """Looks up instrument token for a given script from instrument dump"""
        row = self.getrow(symbol, pece, strikeprice, expirydate)
        if row is None:
            return -1
        else:
            return row.instrument_token.item()
    
    def get_et_for_token(self, token):
        return token

    def getToken_for_et(self, exchangeToken):
        return exchangeToken


    def getExchangeToken(self, symbol, pece, strikeprice, expirydate):
        """Looks up instrument token for a given script from instrument dump"""
        row = self.getrow(symbol, pece, strikeprice, expirydate)
        if row is None:
            return -1
        else:
            return row.exchange_token.item()
        expiry = expirydate.strftime('%Y-%m-%d')
        df=self.getInstruments()
        try:
            return df[(df.name==symbol) & (df.strike==strikeprice) & (df.instrument_type==pece) & (df.expiry==expiry) ].instrument_token.values[0]
        except:
            return -1
    def getrow(self, symbol, pece, strikeprice, expirydate):
        """Looks up instrument token for a given script from instrument dump"""
        expiry = expirydate.strftime('%Y-%m-%d')
        df=self.getInstruments()
        try:
            row = df[(df.name==symbol) & (df.strike==strikeprice) & (df.instrument_type==pece) & (df.expiry==expiry) ].iloc[0]
            log_util.debug(row)
            return row
        except:
            return None

    def updateSLprice(self, orderid, sl, price):
        if self.testing:
            return
        try:
            self.client.modify_order(variety=self.client.VARIETY_REGULAR, \
                                   order_id = orderid, \
                                   order_type=self.client.ORDER_TYPE_SL,
                                   trigger_price = sl, price = price)
            return True
        except:
            log_util.debug ("Issue in Update SL Price")
            return False
 
    def log_order(self,order):
        dalc.log_order(order=order)
        '''cols="strategyid, at_time, symbol, buy_sell, qty, price, trigger_price, comments"
        vals ="{strategyid}, '{at_time}', '{symbol}', '{buysell}', {qty}, {price}, {trigger_price}, '{comments}'"
        vals=vals.format(strategyid=order.strategyid, at_time=order.at_time, symbol=order.symbol, buysell=order.buysell, qty=order.qty, price=order.price, trigger_price=order.trigger_price, comments=order.comments)
        sql = "insert into order_log ({cols}) values ({vals})".format(cols=cols, vals=vals)
        print (sql)
        db.executeSQL(sql)
        '''
        msg= "time: {time}: b/s: {buysell} symbol: {symbol}, Qty: {qty}, price: {price}, Comments: {comments}".format(time=order.at_time, buysell=order.buysell, symbol=order.symbol, qty=order.qty, price=order.price, comments=order.comments)
        logging.info(msg)
        print (msg)

    #def placeOrder(self, symbol,buy_sell,quantity, price, comments='', at_time=datetime.now()):

    def place_order_internal(self, order, check_status_retries):


        # for the order code, get the stock_code, exchange_code, product, action, order_type, stoploss, quantity, price, validity, validity_date, disclosed_quantity, expiry_date, right, strike_price
        exchange = 'NSE'
        product = 'equity'
        order_type = 'limit'

        _d = dalc.get_all_strikes()
        if _d is None or len(_d)==0:
            return None
        else:
            _d = _d[order.code]
            exchange = 'NFO'
            product = 'options'
            _d['symbol'] = 'NIFTY'
        if _d['pece'] == 'ce':
            right = 'call'
        else:
            right = 'put'
        if order.buysell == BuySell.buy:
            t_type='buy'
        elif order.buysell == BuySell.sell:
            t_type='sell'
            
        #validity_date="2022-08-30T06:00:00.000Z",
        #disclosed_quantity="0",
        #expiry_date= "2022-09-29T06:00:00.000Z",
        #Place an intraday stop loss order on NSE
        while (True):
            try :
                self.client.place_order(
                    stock_code=_d['symbol'],
                    exchange_code=exchange,
                    product=product,
                    action=t_type,
                    order_type=order_type,
                    stoploss=order.trigger_price,
                    quantity=order.qty,
                    price=order.price,
                    validity="day",
                    expiry_date=  _d['expirydate'].strftime('%Y-%m-%d'),
                    right=right,
                    strike_price=_d['strikeprice'], 
                    disclosed_quantity=0)
            except:
                print ('Issue in execute ')
                if order.orderid > 0:
                    break
            break
        return order
        
    def placeOrder(self, order, check_status_retries=1):
        #self, symbol,buy_sell,quantity, price, comments='', at_time=datetime.now()
        if self.testing:
            order.orderid=1
        else:
            order = self.place_order_internal(order, check_status_retries)

        status = self.didOrderExecuted(order, retry = check_status_retries)
        order.status=status
        print ("Order placed: order id: ", order.orderid, ", status: ", status)
        return order

    def didOrderExecuted(self, order, sl=0, retry=1):
        if self.testing:
            self.log_order(order)
            order.status = self.client.STATUS_COMPLETE
            print (f'didOrderExecuted::Order id: {order.orderid}')
            return order.status

        for retry_counter in range(1,retry+1):
            status = self.getstatus (order.orderid)
            #print (f"The order status is: {status}, order id: {order.orderid}")
            if status == ORDER_STATUS.OPEN:
                if order.ordtype == 'SL' and retry_counter>2:
                    self.updateSLprice(order.orderid, 1)
                    #TODO - update the order price to LTP-6
                time.sleep(1)

            elif status == self.client.STATUS_COMPLETE:
                self.log_order(order)
                time.sleep(1)
                break
            else :
                print (f'This order is not handled, order id: {order.orderid}')
                #TODO - It's unhandled, flag it to admin
                time.sleep(1)
                break
        return status

    def placeSLOrder(self, symbol,buy_sell,quantity,sl_price):
        # Place an intraday stop loss order on NSE
        if buy_sell == "buy":
            t_type=self.client.TRANSACTION_TYPE_BUY
            t_type_sl=self.client.TRANSACTION_TYPE_SELL
        elif buy_sell == "sell":
            t_type=self.client.TRANSACTION_TYPE_SELL
            t_type_sl=self.client.TRANSACTION_TYPE_BUY
        self.client.place_order(tradingsymbol=symbol,
                        exchange=self.client.EXCHANGE_NSE,
                        transaction_type=t_type,
                        quantity=quantity,
                        order_type=self.client.ORDER_TYPE_MARKET,
                        product=self.client.PRODUCT_MIS,
                        variety=self.client.VARIETY_REGULAR)
        self.client.place_order(tradingsymbol=symbol,
                        exchange=self.client.EXCHANGE_NSE,
                        transaction_type=t_type_sl,
                        quantity=quantity,
                        order_type=self.client.ORDER_TYPE_SL,
                        price=sl_price,
                        trigger_price = sl_price,
                        product=self.client.PRODUCT_MIS,
                        variety=self.client.VARIETY_REGULAR)

    def ModifyOrder(self, order_id,price):
        # Modify order given order id
        self.client.modify_order(order_id=order_id,
                        price=price,
                        trigger_price=price,
                        order_type=self.client.ORDER_TYPE_SL,
                        variety=self.client.VARIETY_REGULAR)

    def positions(self):
        pos = self.client.positions()['day']
        #print('KiteHelper::positions: ', pos)
        #s = json.dumps (pos)
        #s = s.replace ('instrument_token', 'instrumentToken')
        #s = s.replace ('quantity', 'netTrdQtyLot')
        #pos = json.loads(s)
        return pos

    def holdings(self):
        return self.client.holdings()

    def cancel_all_orders(self):
        orders = self.orders()
        orders = [{'order_id': o['order_id'], 'variety': o['variety']} for o in orders if o['status'] in ('TRIGGER PENDING', 'OPEN') ]
        for o in orders:
            self.client.cancel_order(variety = o['variety'], order_id = o['order_id'])

    def close_all_positions(self):
        positions = self.client.positions()['net']
        positions = [{'quantity': p['quantity'], 'exchange': p['exchange'], 'tradingsymbol': p['tradingsymbol']} for p in positions if p['quantity'] != 0 if p['product'] == self.client.PRODUCT_MIS]

        for p in positions:
            if p['quantity']>0:
                tran_type = self.client.TRANSACTION_TYPE_SELL
            else:
                tran_type = self.client.TRANSACTION_TYPE_BUY
            self.client.place_order (tradingsymbol= p['tradingsymbol'], variety=self.client.VARIETY_REGULAR, exchange=p['exchange'], transaction_type=tran_type, quantity=abs(p['quantity']), product=self.client.PRODUCT_MIS, order_type=self.client.ORDER_TYPE_MARKET)

    def getstatus (self, orderid):
        if self.testing:
            return self.client.STATUS_COMPLETE
        return self.getorder(orderid).status

    def getorder (self, orderid):
        if self.testing:
            return self.client.STATUS_COMPLETE, 0
        o = self.get_order_detail ('NFO', orderid)
        return  o
    
    def optionchain(self, symbol, expiry):
        ret = []
        date_str = expiry.strftime(self.date_format)
        ce = self.client.get_option_chain_quotes(stock_code=symbol,
                    exchange_code="NFO", product_type="options",
                    expiry_date=date_str,  right="call")
        pe = self.client.get_option_chain_quotes(stock_code=symbol,
                    exchange_code="NFO", product_type="options",
                    expiry_date=date_str,  right="put")
        ret.extend(ce['Success'])
        ret.extend(pe['Success'])
        return ret

    def cancel_if_exists(self, orderid):
        try:
            self.client.cancel_order(exchange_code = 'NFO', order_id=orderid)
        except:
            print ("There is an issue cancelling the order")
            pass
        status= self.getstatus (orderid)
        return status

    def orders(self):
        try:
            date_str =  datetime.now().strftime(self.date_format)
            orders =  self.client.get_order_list(exchange_code = 'NFO', 
                from_date=date_str, to_date=date_str)
            return orders
        except:
            self.issue=True
            return None

    def getOptionSymbol(self, underlying, expiry, pece, strike):
        if not isinstance(expiry, str):
            #check if it's the last thursday of the month.
            last_day = calendar.monthrange(expiry.year,expiry.month)[1]
            if last_day - expiry.day < 7:
                expiry = expiry.strftime("%y%b").upper()
            elif expiry.month <10 :
                expiry=expiry.strftime("%y%#m%d")
            elif expiry.month ==10 :
                expiry=expiry.strftime("%yO%d")
            elif expiry.month ==11 :
                expiry=expiry.strftime("%yN%d")
            elif expiry.month ==12 :
                expiry=expiry.strftime("%yD%d")
        #TODO: date format is not portable, replace it with portable code
        symbol = underlying + expiry + str(strike) +  pece
        return symbol

    def closeSocket(self):
        print ("Trying to close KiteTicker")
        self.close=1
        self.kws.close()
        if self.kws.is_connected():
            print ("Trying again to close KiteTicker")
            self.kws.close()

    def getAllOHLC(self, token, hours=300, to_time=None):
        allOHLC={}
        #intervals = ['minute', '5minute', '15minute']
        #intervals_int=[1,5,15]
        hours = [hours, hours, hours]
        for minute, minute_str in self.intervals.items():
            ohlc = self.fetchOHLC(token, minute, hours=hours[0], to_time=to_time)
            allOHLC[minute]= ohlc
        return allOHLC

    def historical_data (self, instrument,from_time, to_time,interval):
        from_time = from_time.strftime("%Y-%m-%d %H:%M:%S")
        to_time = to_time.strftime("%Y-%m-%d %H:%M:%S")

        for i in range(1,5):
            try:
                params = {'stock_code':'CNXBAN', 'exchange_code':'NSE', 'expiry_date':'', 'strike_price':'', 'right':''}
                data = self.client.get_historical_data(interval=self.intervals[interval], from_date=from_time, to_date=to_time,  **params)
                #data = self.client.historical_data (instrument,from_time, to_time,self.intervals[interval])
                return data
                break
            except:
                time.sleep(1)

    def fetchOHLC(self, token,interval, hours=300, to_time=None):
        """extracts historical data and outputs in the form of dataframe"""
        interval_str= self.intervals[interval]
        #print (f'fetchOHLC token: {token}')

        to_time=datetime.now() if to_time is None else to_time
        #print (interval, self.intervals[interval])
        data=self.client.historical_data(token,to_time-timedelta(hours=hours), to_time ,interval_str)
        data = pd.DataFrame(data)[-2000:]
        #print (data)
        c=CalcData(1, 'BANKNIFTY', '2021-02-13', 234729489)
        data=c.CalculateEMA(data)
        if token == 260105:
            data.to_csv(f'{token}_{interval}.csv')
            #print (f'Data after calculate ema: {token}', data[['date', 'open', 'close', 'ubb', 'lbb', 'sma20']])
        return data

    def fetchOHLC_time(self, token,from_time, to_time, interval):
        """extracts historical data and outputs in the form of dataframe"""
        data=self.client.historical_data(token,from_time, to_time ,interval)
        data = pd.DataFrame(data)
        c=CalcData(1, 'BANKNIFTY', '2021-02-13', 234729489)
        data=c.CalculateEMA(data)
        return data

    def CreateWebSocket(self, on_tick, on_connect=None, on_close=None, on_error=None, on_reconnect=None):
        #access_token= dalc.get_access_token(self.cred['apikey'])
        kws = KiteTicker(self.cred['apikey'], self.cred['accesstoken'])
        kws.on_ticks = on_tick
        kws.on_connect = on_connect
        kws.on_reconnect = on_reconnect
        kws.connect(threaded=True)
        print ("Createwebsocket successful")
        self.kws= kws
        print ("Connection status: ", self.kws.is_connected())
        return self.kws

    def max_pain(self, data, range_from=0, range_to=500000):
        def get_val(row):
            if row['totalval'] is not None:
                return row['totalval']
            return None

        results = []
        for row in data:
            if row['strike_price'] < range_from or row['strike_price'] > range_to:
                continue
            peval = sum([abs(round(oc['strike_price'] - row['strike_price'], 1)) * oc['open_interest'] for oc in data if oc['strike_price'] > row['strike_price'] and oc['right'] == 'Put'])
            ceval = sum([abs(round(oc['strike_price'] - row['strike_price'], 1)) * oc['open_interest'] for oc in data if oc['strike_price'] < row['strike_price'] and oc['right'] == 'Call'])
            results.append({
                'strike_price': row['strike_price'],
                'peval': peval,
                'ceval': ceval,
                'totalval': peval + ceval
            })

        maxpain = min(results, key=lambda x: x['totalval'])
        return maxpain['strike_price']

    def get_vitals(self, optionchain):
        vitals = {}
        call = [c['open_interest'] for c in optionchain if c['right'] == 'Call']
        put = [c['open_interest'] for c in optionchain if c['right'] == 'Put']
        vitals ['pcr'] =  sum(put) / sum(call)
        vitals['maxpain'] = self.max_pain(optionchain, 42500, 43500)
        return vitals

    def place_order_test(self):
        self.client.place_order(stock_code="NIFTY",
                    exchange_code="NFO",
                    product="options",
                    action="buy",
                    order_type="market",
                    stoploss="",
                    quantity="50",
                    price="",
                    validity="day",
                    validity_date="2023-01-05T06:00:00.000Z",
                    disclosed_quantity="0",
                    expiry_date="2023-01-05T06:00:00.000Z",
                    right="call",
                    strike_price="18000")
def testohlc(token):
    helper=KiteHelper()
    df = helper.fetchOHLC(token,1, hours=24)
    file=fileutil.getNamedTempFile('test.csv')
    df.to_csv(file)



if __name__=='__main__':
    #testohlc(260105)
    from levels import Order
    helper=HelperBreeze(38)
    order = Order(None, None, BuySell.buy, 25, 101, 'test', code=401)
    helper.place_order_test()
    print (helper.orders())
    helper.place_order_internal(order, 1)
    print (datetime.now())
    chain= helper.optionchain('CNXBAN', dateUtil.get_nextday_of_week(datetime.today().date(), 4))
    print (helper.get_vitals(chain))
    print (datetime.now())
    #data = helper.client.get_historical_data(interval='minute', from_date='2022-12-01', to_date='2022-12-30',  exchange_code='NSE', stock_code='CNXBAN', product='equity', expiry_date='', strike_price='', right='')
    data = helper.historical_data(1, datetime(2022,12,20), datetime(2022, 12, 25), 1)
    print (data)
    #a = [{k:v for (k,v) in c.items() if k in ('ltp', 'strike_price', 'right', 'open_interest')} for c in chain]
    #helper.historical_data ( 260105, datetime.today()- timedelta(days=4), datetime.today()- timedelta(days=1), 15)
    #sym=helper.getOptionSymbol('BANKNIFTY', datetime.today()+ timedelta(days=15), 'CE', 32000 )
    #print (sym)
    #helper.cancel_all_orders()
    #helper.close_all_positions()