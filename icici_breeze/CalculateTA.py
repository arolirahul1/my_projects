import talib as ta
import pandas as pd
#import dbmysql as db
import numpy as np
#from SQLBuild import insert, update, connection
#from datetime import datetime #, timedelta
#import fileutil
class CalcData():
    def __init__(self, freq, symbol, dt=None, epoch=None):
        self.fCLOSE = "close"
        self.fOPEN = "open"
        self.fHIGH = "high"
        self.fLOW = "low"
        self.fVOLUME = "volume"
        self.freq = freq
        self.symbol = symbol
        #self.dt = dt
        #self.epoch = epoch
        #self.setTable()

    def CalculateEMA(self, df):
        #df["highlow"] =(df[self.fHIGH] + df[self.fLOW])/2
        #close_vals = df[self.fCLOSE].values.astype('float64')
        close_vals = np.array(df[self.fCLOSE].values.astype('float64'), dtype=float)
        #high_vals  = np.array(df[self.fHIGH].values.astype('float64'), dtype=float)
        #low_vals  = np.array(df[self.fHIGH].values.astype('float64'), dtype=float)
        
        upper = close_vals.max()
        lower = close_vals.min()
        new_close_vals = np.array([(i-lower)/(upper-lower)*100 for i in close_vals])
        '''
        upper = df.groupby('date')["close"].transform('max')
        lower = df.groupby('date')["close"].transform('min')
        new_close_vals = (close_vals - lower)/(upper-lower)*100
        '''
        df["RSI"] = ta.RSI(close_vals)

        #upper = close_vals * 1.0075
        #lower = close_vals * .9925
        #new_close_vals = np.array([(i-lower)/(upper-lower)*100 for i in close_vals])
        df['new_close']=new_close_vals
        new_ema = ta.EMA(new_close_vals, timeperiod=20).round(1)
        df["slope_ema20"] = ta.LINEARREG_ANGLE(new_ema, timeperiod=2).round(0)

        new_sma = ta.SMA(new_close_vals, timeperiod=20).round(1)
        df["slope_sma20"] = ta.LINEARREG_ANGLE(new_sma, timeperiod=2).round(0)

        new_ema = ta.EMA(new_close_vals, timeperiod=7).round(1)
        df["slope_ema7"] = ta.LINEARREG_ANGLE(new_ema, timeperiod=2).round(0)

        #df["ema5"] = ta.EMA(close_vals, timeperiod=7).round(1)
        df["ema7"] = ta.EMA(close_vals, timeperiod=7).round(0)
        df["ema20"] = ta.EMA(close_vals, timeperiod=20).round(0)
        df["ema50"] = ta.EMA(close_vals, timeperiod=50).round(0)
        df["ema100"] = ta.EMA(close_vals, timeperiod=100).round(0)
        df["ema200"] = ta.EMA(close_vals, timeperiod=200).round(0)
        df["ubb"], df["sma20"], df["lbb"] = ta.BBANDS(df[self.fCLOSE].values,matype=ta.MA_Type.SMA, timeperiod=20)
        df=df.round(1)        
        return df

    def CalculateCPR(self, df):
        prevdf = df
        df['PIVOT'] = (prevdf[self.fHIGH]+prevdf[self.fLOW]+prevdf[self.fCLOSE])/3
        df['BC'] = (prevdf[self.fHIGH]+prevdf[self.fLOW])/2
        df['TC'] = df['PIVOT']*2-df['BC']
        df['R1'] = df['PIVOT']*2-prevdf[self.fLOW]
        df['S1'] = df['PIVOT']*2-prevdf[self.fHIGH]
        df['R2'] = df['PIVOT']-df['S1']+df['R1']
        df['S2'] = df['PIVOT']+df['S1']-df['R1']
        df['R3'] = df['PIVOT']-df['S2']+df['R2']
        df['S3'] = df['PIVOT']+df['S2']-df['R2']
        df['R4'] = df['PIVOT']-df['S3']+df['R3']
        df['S4'] = df['PIVOT']+df['S3']-df['R3']
        return df


    def Calculate(self, df):
        n=14
        close = np.array(df[self.fCLOSE].values, dtype='f8')
        df["RSI"] = pd.Series(ta.RSI(close, n), index = df.index, name='RSI%s' % str(4))
        bb = ta.BBANDS(df[self.fCLOSE].values, matype=ta.MA_Type.SMA, timeperiod=20)
        df["BBUpper"] = bb[0]
        df["BBMiddle"] = bb[1]
        df["BBLower"] = bb[2]
        #df["BBUpper"] =round(df["BBUpper"],1)

        df["LONGEMA"] = ta.EMA(df[self.fCLOSE].values, timeperiod=200)
        df["MEDIUMEMA"] = ta.EMA(df[self.fCLOSE].values, timeperiod=100)
        df["SHORTEMA"] = ta.EMA(df[self.fCLOSE].values, timeperiod=50)
        df["EMA20"] = ta.EMA(df[self.fCLOSE].values, timeperiod=20)
        df["QUICKEMA"] = ta.EMA(df[self.fCLOSE].values, timeperiod=7)
        df["trendangle"] = ta.LINEARREG_ANGLE(df[self.fCLOSE].values, timeperiod=7)
        df['trend'] = df.apply(lambda x: 'U' if x['trendangle']>0 else 'D', axis=1)

        df.round({self.fOPEN:1, self.fVOLUME:0, "BBUpper":1, "BBMiddle":1, "BBLower":1, "SHORTEMA":1})

        df["CDL3BLACKCROWS"] = ta.CDL3BLACKCROWS(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLDARKCLOUDCOVER"] = ta.CDLDARKCLOUDCOVER(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE], 0)
        df["CDLDOJI"] = ta.CDLDOJI(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLDOJISTAR"] = ta.CDLDOJISTAR(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLDRAGONFLYDOJI"] = ta.CDLDRAGONFLYDOJI(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLENGULFING"] = ta.CDLENGULFING(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLEVENINGDOJISTAR"] = ta.CDLEVENINGDOJISTAR(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE], 0)
        df["CDLEVENINGSTAR"] = ta.CDLEVENINGSTAR(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE], 0)
        df["CDLGAPSIDESIDEWHITE"] = ta.CDLGAPSIDESIDEWHITE(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLGRAVESTONEDOJI"] = ta.CDLGAPSIDESIDEWHITE(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLHAMMER"] = ta.CDLHAMMER(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLHANGINGMAN"] = ta.CDLHANGINGMAN(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])

        df["CDLHARAMI"] = ta.CDLHARAMI(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLHARAMICROSS"] = ta.CDLHARAMICROSS(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLHIGHWAVE"] = ta.CDLHIGHWAVE(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLHIKKAKE"] = ta.CDLHIKKAKE(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLHIKKAKEMOD"] = ta.CDLHIKKAKEMOD(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLHOMINGPIGEON"] = ta.CDLHOMINGPIGEON(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLIDENTICAL3CROWS"] = ta.CDLIDENTICAL3CROWS(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLINNECK"] = ta.CDLINNECK(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLINVERTEDHAMMER"] = ta.CDLINVERTEDHAMMER(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLKICKING"] = ta.CDLKICKING(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLKICKINGBYLENGTH"] = ta.CDLKICKINGBYLENGTH(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLLADDERBOTTOM"] = ta.CDLLADDERBOTTOM(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLLONGLEGGEDDOJI"] = ta.CDLLONGLEGGEDDOJI(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLLONGLINE"] = ta.CDLLONGLINE(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLMATCHINGLOW"] = ta.CDLMATCHINGLOW(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])

        df["CDLMATHOLD"] = ta.CDLMATHOLD(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLMORNINGDOJISTAR"] = ta.CDLMORNINGDOJISTAR(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLMORNINGSTAR"] = ta.CDLMORNINGSTAR(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLONNECK"] = ta.CDLONNECK(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLPIERCING"] = ta.CDLPIERCING(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLRICKSHAWMAN"] = ta.CDLRICKSHAWMAN(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLRISEFALL3METHODS"] = ta.CDLRISEFALL3METHODS(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLSEPARATINGLINES"] = ta.CDLSEPARATINGLINES(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLSHOOTINGSTAR"] = ta.CDLSHOOTINGSTAR(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLSHORTLINE"] = ta.CDLSHORTLINE(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLSPINNINGTOP"] = ta.CDLSPINNINGTOP(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])


        df["CDLSTALLEDPATTERN"] = ta.CDLSTALLEDPATTERN(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLSTICKSANDWICH"] = ta.CDLSTICKSANDWICH(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLTAKURI"] = ta.CDLTAKURI(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLTASUKIGAP"] = ta.CDLTASUKIGAP(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLTHRUSTING"] = ta.CDLTHRUSTING(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLTRISTAR"] = ta.CDLTRISTAR(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLUNIQUE3RIVER"] = ta.CDLUNIQUE3RIVER(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLUPSIDEGAP2CROWS"] = ta.CDLUPSIDEGAP2CROWS(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["CDLXSIDEGAP3METHODS"] = ta.CDLXSIDEGAP3METHODS(df[self.fOPEN], df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])

        df["OBV"] = ta.OBV(df[self.fCLOSE], df[self.fVOLUME])
        df["AD"] = ta.AD(df[self.fHIGH], df[self.fLOW], df[self.fCLOSE], df[self.fVOLUME])
        df["ADOSC"] = ta.ADOSC(df[self.fHIGH], df[self.fLOW], df[self.fCLOSE], df[self.fVOLUME], 3, 10)
        df["ADOSC"] = ta.ADOSC(df[self.fHIGH], df[self.fLOW],df[self.fCLOSE], df[self.fVOLUME])


        df["ADX14"] = ta.ADX( df[self.fHIGH], df[self.fLOW], df[self.fCLOSE],14)
        df["ADXR14"] = ta.ADXR( df[self.fHIGH], df[self.fLOW], df[self.fCLOSE],14)
        df["APO_12_26"] = ta.APO(df[self.fCLOSE])
        df["AROON_14_Up"],df["AROON_14_Down"] = ta.AROON( df[self.fHIGH], df[self.fLOW])
        df["RSI_14"] = ta.RSI(df[self.fCLOSE])
        df["STOCH_k"], df["STOCH_d"] = ta.STOCH( df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["STOCHF_k"], df["STOCHF_d"] = ta.STOCHF( df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["STOCHRSI_k"],df["STOCHRSI_d"] = ta.STOCHRSI(df[self.fCLOSE])
        df["TRIX_30"] = ta.TRIX(df[self.fCLOSE], 20)
        df["ULTOSC"] = ta.ULTOSC( df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["WILLR_14"] = ta.WILLR( df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["DX_14"] = ta.DX( df[self.fHIGH], df[self.fLOW], df[self.fCLOSE])
        df["MACD"], df["MACD_Signal"], df["MACD_History"] = ta.MACD(df[self.fCLOSE])
        df["MFI"] = ta.MFI( df[self.fHIGH], df[self.fLOW], df[self.fCLOSE], df[self.fVOLUME])
        df["MOM"] = ta.MOM(df[self.fCLOSE])
        df["ROC_10"] = ta.ROC(df[self.fCLOSE])
        df["ROCP_10"] = ta.ROCP(df[self.fCLOSE])
        df["ROCR_10"] = ta.ROCR(df[self.fCLOSE])

        df = np.round(df, 2)
        return df

s="""
    def Insert(self):
        sql = 'insert into derived_1min({cols}) values({vals})'
        cols = 'Trend_1Min  , Bollinger_LB_1Min  , Bollinger_MB_1Min  , Bollinger_UB_1Min  , Short_EMA__1Min  , Medium_EMA_1Min  , Long_EMA_1Min  , Chart_Pattern1_1Min  , Chart_Pattern2_1Min  , PCR_Selected_Option  , IdealValue  , RiskPercentage  , RiskRewardRatio '
        vals = '{Trend_1Min}, {Bollinger_LB_1Min}, {Bollinger_MB_1Min}, {Bollinger_UB_1Min}, {Short_EMA__1Min}, {Medium_EMA_1Min}, {Long_EMA_1Min}, {Chart_Pattern1_1Min}, {Chart_Pattern2_1Min}, {PCR_Selected_Option}, {IdealValue}, {RiskPercentage}, {RiskRewardRatio}'
        vals = vals.format()
        sql = sql.format(cols=cols, vals=vals)
    def setTable(self ):
        if self.freq == 1:
            self.sourcetable = 'ohlc_1min'
            self.targettable = 'derived_1min'
            self.readSql = 'select * from(select ADATE, OPEN, HIGH, LOW, CLOSE, VOLUME, OI from OHLC_1min where epochid <={epoch} and SYMBOL='{symbol}' order by adate desc limit 30) as a order by adate'
        if self.freq == 5:
            self.sourcetable = 'ohlc_5min'
            self.targettable = 'derived_5min'
            self.readSql = 'select * from(select ADATE, OPEN, HIGH, LOW, CLOSE, VOLUME, OI from OHLC_5min where epochid <={epoch} and SYMBOL='{symbol}' order by adate desc limit 30) as a order by adate'
        if self.freq == 86400:
            self.sourcetable = 'eoddata'
            self.targettable = 'derived_eod'
            self.readSql = 'select * from(select ADATE, OPEN, HIGH, LOW, CLOSE, tottrdqty as VOLUME, 0 as OI from eoddata where Adate <='{dt}' and SYMBOL='{symbol}' order by adate desc limit 30) as a order by adate'
    
    def ReadData(self):
        readsql = self.readSql.format(dt=self.dt.strftime("%Y-%m-%d"), symbol=self.symbol, epoch=self.epoch)
        df = pd.read_sql_query(readsql, db.getConn())
        return df
    def test(self):
        df = self.ReadData()
        df = self.CalculateCPR(df)
        #df=self.Calculate(df)
        #row=df.iloc[-1]
        #prt = "Upper: {BBU}, Middle: {BBM}, Lower: {BBL}, RSI: {RSI}"
        return df.iloc[-1]
if __name__ == '__main__':
    calc = CalcData(86400, 'BANKNIFTY', datetime.today(), 0)
    lower = 300
    upper = 638
    a = [422, 421, 420, 431, 433]
    a = [(i-lower)/(upper-lower)*100 for i in a]
    ar = np.array(a)
    s = ta.LINEARREG_ANGLE(ar, timeperiod=2).round(0)
if __name__ == '__main__':
    filename = fileutil.getNamedTempFile('abc.csv')
    df=pd.read_csv(filename)
    new_close_vals  = np.array(df['close'].values.astype('float64'), dtype=float)
    upper=new_close_vals.max()
    lower=new_close_vals.min()
    new_close_vals  = np.array([(i-lower)/(upper-lower)*100 for i in new_close_vals])
    df['newclose'] =new_close_vals
    df['newema'] = ta.EMA(new_close_vals, timeperiod=20).round(1)
    df['newema101'] = ta.EMA(new_close_vals, timeperiod=101).round(1)
    #df['newslope'] =ta.LINEARREG_SLOPE(df['ema20'].values, timeperiod=2).round(0)*180/3.14
    df['newslope'] =ta.LINEARREG_ANGLE(df['newema'].values, timeperiod=2).round(0)
    df.to_csv(filename)
calc.test()
"""