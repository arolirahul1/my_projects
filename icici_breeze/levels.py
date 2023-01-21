from datetime import datetime
from CalculateTA import CalcData
#import copy

class ORDER_STATUS:
    OPEN = 'OPEN'
    COMPLETE = 'COMPLETE'
    CANCELLED= 'CANCELLED'
    REJECTED= 'REJECTED'
    TRIGGER_PENDING = 'TRIGGER PENDING'

class Order_pref:
    profit_perc = .03
    sl_perc = .02
    order_price_threshold=.0025
    extreme_sl_perc=.1

    def __init__(self, profit_perc, sl_perc, order_price_threshold, extreme_sl_perc):
        self.profit_perc = profit_perc
        self.sl_perc =sl_perc
        self.order_price_threshold=order_price_threshold
        self.extreme_sl_perc = extreme_sl_perc
    def eff_target_price(self, price, buysell):
        if buysell==BuySell.buy:
            ret= (1+self.profit_perc) * price+.5
        if buysell==BuySell.sell:
            ret= (1-self.profit_perc) * price-.5
        return round(ret,1)
    def eff_sl_price(self, price, buysell):
        if buysell==BuySell.buy:
            ret= (1-self.sl_perc) * price-.5
        if buysell==BuySell.sell:
            ret =(1+self.sl_perc) * price+.5
        return round(ret,1)
    def eff_sl_extreme(self, price, buysell):
        if buysell==BuySell.buy:
            ret= (1-self.extreme_sl_perc) * price-10
        if buysell==BuySell.sell:
            ret =(1+self.sl_extreme_sl_perc) * price+10
        return round(ret,1)
    def eff_order_price_threshold(self, price, buysell):
        if buysell==BuySell.buy:
            ret=(1+self.order_price_threshold) * price
        if buysell==BuySell.sell:
            ret=(1-self.order_price_threshold) * price
        return round(ret,1)
    def eff_extreme_sl_price(self, price, buysell):
        if buysell==BuySell.buy:
            ret= (1-self.extreme_sl_perc) * price
        if buysell==BuySell.sell:
            ret =(1+self.extreme_sl_perc) * price
        return round(ret,1)


class action:
    new_position='New'
    none='None'
    stop_loss = 'SL'
    
class Position:
    symbol=''
    token=0
    qty=0 #qty can be negative if shorted
    price=0.0
    buysell=''
    target_price=0.0
    sl_price=0.0
    sl_extreme=0.0
    orderid=0
    comments=''
    last_action = action.none
    last_action_time = None

    def update(self, order, order_pref, sl=0):
        self.symbol = order.symbol
        self.token=order.token
        self.buysell=order.buysell
        self.last_action_time = order.at_time
        if self.buysell==BuySell.buy:
            self.price = (self.qty*self.price + order.qty*order.price)/(self.qty + order.qty)
            self.qty=self.qty+order.qty
            self.target_price = order_pref.eff_target_price(order.price,BuySell.buy)
            self.sl_extreme = order_pref.eff_sl_extreme(order.price,BuySell.buy)
            if sl == 0:
                self.sl_price = order_pref.eff_sl_price(order.price,BuySell.buy)
            else:
                self.sl_price = sl
        elif order.buysell==BuySell.sell:
            self.qty=self.qty-order.qty
        if self.qty==0:
            self.price=0
            self.last_action=action.none
        elif self.qty > 0:
            self.last_action=action.new_position
            
        self.orderid=0


        """
                multiplier=1 if self.position.qty<0 else -1
                self.position
                self.position.target_price = self.position.price * (1 + self.profit_perc * multiplier)
                self.position.target_price = round(self.position.target_price, 1)
                self.position.sl_price = self.position.price * (1 - self.sl_perc * multiplier)
                self.position.sl_price = round(self.position.sl_price , 1)
        """

class Order :
    exchangeToken=0
    strategyid=0
    code = 0
    orderid=0
    symbol=''
    token=0
    buysell=''
    qty=0
    pending_qty=0
    price=0
    trigger_price=0
    at_time=None
    ordtype =''
    status=''

    def __init__(self, symbol, exchangeToken, buysell, qty, price, comments, at_time=None,  ordtype='', trigger_price=0, strategyid=0, code=0):
        self.init_time=datetime.now()
        self.symbol=symbol
        self.exchangeToken=exchangeToken
        self.token=exchangeToken
        self.buysell=buysell
        self.qty=qty
        self.price=price
        self.comments=comments
        self.trigger_price = trigger_price
        self.ordtype = ordtype
        self.strategyid=strategyid
        self.code = code
        if at_time is None:
            self.at_time=datetime.now()
        else:
            self.at_time=at_time
    def to_string(self):
        return f'symbol: {self.symbol}, token: {self.token}, qty: {self.qty}, code: {self.code}, b/s: {self.buysell}'

    @classmethod
    def fromjson(self, ordjson):
        "Initialize MyData from a file"
        ord = self(ordjson['symbol'], 1,2,3,4,5,6,7)
        return ord

class Trend:
    up='U'
    down = 'D'
    sideways='S'

class PositionStatus:
    isopen='O'
    isclosed='C'

class Reco:
    def __init__(self, reco):
        self.reco=reco
        s_code = reco['specific_code']
        s_price = reco['specific_price']
        self.buysell=reco['buysell']
        self.direction = reco['direction']
        self.probability = reco['probability']
        self.id = reco['id']
        self.strategy= '' #reco['specific_strategy']
        if s_code != None and s_code != '':
            self.code = int(s_code)
        else:
            self.code=0
        self.close = reco['close']

        if s_price != None and s_price != '':
            self.price = int(s_price )
        else:
            self.price=0
        self.probability=int(reco['probability'])

    def copy(self):
        return Reco(self.reco)



class BuySell:
    buy='b'
    sell= 's'

class TradeSignal:
    buysell=""
    probability=0 #in percentage, between 1 and 100
    def __init__(self, buysell, probability):
        self.buysell=buysell
        self.probability = probability

class common_params:
    cpr_resistances=[]
    cpr_supports=[]
    cpr_top=0
    cpr_bottom=0
    global_markets_trend=Trend.sideways
    pcr=0
    pcr_trend=Trend.sideways
    maxpain=0
    maxpain_trend=Trend.sideways
    levels_up=[]
    levels_down=[]

class BB:
    bottom=0
    top=0
    middle=0
    def __init__(self, bottom, middle, top):
        self.bottom=bottom
        self.middle=middle
        self.top = top

class Values:
    token=0
    trend={}
    last_price=0
    df_1=None
    df_5=None
    df_15=None
    #ema_1m = {}
    #ema_5m = {}
    #ema_15m = {}
    trend_ema20_1=Trend.sideways
    trend_ema20_5=Trend.sideways
    trend_ema20_15=Trend.sideways
    trend_sma20_1=Trend.sideways
    trend_ema7_1=Trend.sideways
    angle_ema7_1=0
    angle_ema20=0

    sma20_1= 0
    ema20_1 = 0
    ema20_5 = 0
    ohlcs=None
    def __init__(self):
        self.levels_up=[36240, 35490, 35580]
        self.levels_down=[36140, 35200, 35100]
    def calculate(self):
        c=CalcData(1, 'BANKNIFTY', '2021-02-13', 234729489)

        self.df_1=c.CalculateEMA(self.df_1)
        row=self.df_1.iloc[-1]
        #angle = row.slope_ema20_1
        self.ema20_1= row.ema20
        self.sma20_1= row.sma20
        self.ema7_1= row.ema7
        self.ema200_1 = row.ema200

        self.angle_ema7_1 = row.slope_ema7
        self.angle_ema20_1 = row.slope_ema20
        self.angle_sma20_1 = row.slope_sma20

        self.trend_ema7_1 = self.angletoTrend(row.slope_ema7)
        self.trend_ema20_1 = self.angletoTrend(row.slope_ema20)
        self.trend_sma20_1 = self.angletoTrend(row.slope_sma20)

        self.ubb_1 = row.ubb
        self.lbb_1 = row.lbb

        self.touched_ema200 =  self.ema200_1 in range (int(self.df_1.tail(5).high.min()), int(self.df_1.tail(5).high.max()))
        self.closer_to_mbb = True if (self.ubb_1 - self.ema7_1)/(self.ema7_1 - self.sma20_1)>2 else False

        self.df_5=c.CalculateEMA(self.df_5)
        row=self.df_5.iloc[-1]
        self.ema20_5= row.ema20
        self.trend_ema20_5 = self.angletoTrend( row.slope_ema20)

        self.df_15=c.CalculateEMA(self.df_15)
        row=self.df_5.iloc[-1]
        self.ema20_15= row.ema20
        self.trend_ema20_15 = self.angletoTrend( row.slope_ema20)

    def __str__(self):
        return "ema20_1: {} sma20_1: {} ema7_1: {} ema200_1: {} angle_ema7_1 : {} angle_ema20_1: {} angle_sma20_1: {} trend_ema7_1 : {} trend_ema20_1: {} trend_sma20_1: {} ubb_1 : {} lbb_1 : {} touched_ema200: {} closer_to_mbb: {} ema20_5: {} trend_ema20_5: {} ema20_15: {} trend_ema20_15: {}".format(self.ema20_1, self.sma20_1, self.ema7_1, self.ema200_1, self.angle_ema7_1 , self.angle_ema20_1, self.angle_sma20_1, self.trend_ema7_1 , self.trend_ema20_1, self.trend_sma20_1, self.ubb_1 , self.lbb_1 , self.touched_ema200, self.closer_to_mbb, self.ema20_5, self.trend_ema20_5, self.ema20_15, self.trend_ema20_15)

    def angletoTrend(self, angle):
        if angle<-7 :
            return Trend.down
        elif angle<7:
            return Trend.sideways
        else:
            return Trend.up

    def is_1min_up(self):
        if (self.trend_ema20_1 == Trend.up):
            return True
        else:
            return False

    def is_1min_down(self):
        if (self.trend_ema20_1 == Trend.down):
            return True
        else:
            return False

    def is_all_up(self):
        if (self.trend_ema20_1 == self.trend_ema20_5) & (self.trend_ema20_5 == self.trend_ema20_15)  & (self.trend_ema20_1 == Trend.up):
            return True
        else:
            return False

    def is_all_up_except1(self):
        if (self.trend_ema20_15 == self.trend_ema20_5 ) & (self.trend_ema20_15 == Trend.up):
            return True
        else:
            return False

    def is_all_up_except5(self):
        if (self.trend_ema20_1 == self.trend_ema20_15)  & (self.trend_ema20_1 == Trend.up):
            return True
        else:
            return False

    def is_all_down(self):
        if (self.trend_ema20_1 == self.trend_ema20_5) & (self.trend_ema20_5 == self.trend_ema20_15)  & (self.trend_ema20_1 == Trend.down):
            return True
        else:
            return False

    def is_all_down_except5(self):
        if (self.trend_ema20_1 == self.trend_ema20_15)  & (self.trend_ema20_1 == Trend.down):
            return True
        else:
            return False

    def is_all_down_except1(self):
        if (self.trend_ema20_15 == self.trend_ema20_5)  & (self.trend_ema20_15 == Trend.down):
            return True
        else:
            return False