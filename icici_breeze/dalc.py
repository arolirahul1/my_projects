# -*- coding: utf-8 -*-
import dbmysql as db
import components.log_util as log_util
from config.config import Config

import pandas as pd
from datetime import datetime#, timedelta

cfg = Config()

def get_instruments_to_download():
    return db.getArray("select distinct kitetoken from strikes_watch where statusid=1 ")

def get_ks_instruments():
    return db.getDictList("select refid as code, kstoken as token, optionsymbol, strikeprice, pece, expirydate, underlying from  strikes_watch where statusid=1 ")


def get_optionchain_info(day, attime):
    sql = f'''SELECT pcr, underlyingvalue, maxpain FROM optionchainref
        WHERE asondate < '{attime} and dayofmonth(asondate) = {day}'
        ORDER BY asondate desc
        LIMIT 1'''
    d = db.getDictList (sql)[0]
    return d
def get_strike_ks_conf():
    sql= "SELECT kitetoken as code, kstoken AS token from strikes_watch"
    d = db.getDict (sql)

    return d
def get_strike_ks_kite_conf():
    if not cfg.STUB:
        sql= "SELECT kstoken AS token, kitetoken as code from strikes_watch"
        d = db.getDict (sql)
    else:
        d={1:2, 2:3, 3:4, 4:5}
    return d
def get_strike_conf():
    if cfg.STUB:
        sql= "SELECT refid as code, kitetoken AS token from strikes_watch"
        d = db.getDict (sql)
    else:
        d={401:2, 402:3, 403:4, 404:5}
    return d
def get_eod_report(d):
    sql = f"SELECT buysell, SUM(qty*price) AS sum FROM usertrade  WHERE userid=8 and DATE(at_time) = '{d}' GROUP BY buysell"
    log_util.debug(sql)
    di = db.getDict(sql)
    sql = f"SELECT count(1) AS sum FROM usertrade  WHERE userid=8 and DATE(at_time) = '{d}'"
    log_util.debug(sql)
    cnt = db.getScalar(sql)
    return di, cnt

def get_access_token(apikey):
    sql= "select accesstoken  from authen where apikey='{apikey}'".format(apikey=apikey)
    log_util.debug(sql)
    return db.getScalar(sql)

def get_strikes_watch(userid):
    if not cfg.STUB:
        sql= "SELECT refid as code, kitetoken AS token, optionsymbol, 0 as qty, 0 as price  from strikes_watch where refid between 401 and 410"
        dictlist = db.getDictList (sql)
        return dictlist
    else:
        return {401:1, 402: 2, 403:3, 404:4}

def get_user(id):
    sql= f"SELECT * from user where id = {id}"
    dictlist = db.getDictList (sql)
    return dictlist

def get_authen(id):
    if not cfg.STUB:
        sql= f"SELECT authen.*, user.email, user.active, user.brokerapi from authen join user on authen.userid = user.id where userid = {id}"
        dictlist = db.getDictList (sql)[0]
    else:
        dictlist = {'userid':19, 'username':'SV06011988', 'pin': '8205', 'password':'6HpSFh8Kob', 'email':'roopesht@gmail.com','active':'1', 'brokerapi':'ks', 'requesttoken': '82417b3d-6a80-31fd-bb8b-b7eb5a68a6bc', 'apikey': 'cF56LIisWDpDWPv8PzKCFwf6fnUa', 'app_id':'DefaultApplication'}
        #'', 'pin', 'apipassword', 'apikey', 'apisecret', 'accesstoken', , 'app_id', 'otp_code', 
    return dictlist

def orderlog_error(userid, attime, error):
    if not cfg.STUB:
        try:
            sql = 'insert into orderlog_error (userid, attime, error_msg) values('
            sql = sql + f'{userid}, {attime}, "{error}")'
            db.executeSQL(sql)
        except Exception as e:
            pass
    
def update_authen(userid, pin, requesttoken):
    sql = f'update authen set pin = {pin}, requesttoken = "{requesttoken}" where userid = {userid}'
    db.executeSQL(sql)

def get_symbol_bycode(refid):
    sql= "select kitetoken from strikes_watch where refid='{refid}'".format(refid=refid)
    return db.getScalar(sql)

def add_order(order, userid):
    cols="at_time, userid, optionid, symbol, buysell, qty, price, comments"
    vals =f"'{order.at_time}', {userid}, 0, '{order.symbol}', '{order.buysell}', {order.qty}, {order.price}, '{order.comments}'"
    sql = "insert into usertrade ({cols}) values ({vals})".format(cols=cols, vals=vals)
    log_util.debug(sql)
    db.executeSQL(sql)

def log_order(order):
    if not cfg.STUB:
            
        cols="strategyid, at_time, symbol, buy_sell, qty, price, trigger_price, comments"
        vals ="{strategyid}, '{at_time}', '{symbol}', '{buysell}', {qty}, {price}, {trigger_price}, '{comments}'"
        vals=vals.format(strategyid=order.strategyid, at_time=order.at_time, symbol=order.symbol, buysell=order.buysell, qty=order.qty, price=order.price, trigger_price=order.trigger_price, comments=order.comments)
        sql = "insert into order_log ({cols}) values ({vals})".format(cols=cols, vals=vals)
        log_util.debug(sql)
        db.executeSQL(sql)
def get_start():
    return db.getScalar("select start from liveconfig")
def get_all_tokens():
    return pd.read_sql (con=db.getSQLAConn(), sql='SELECT DISTINCT token FROM 1min')
def save_df(tablename, df):
    df.to_sql (tablename, if_exists='append', con=db.getSQLAConn())

def save_global_index(indices):
    sql = '''insert into globalindex (adate,atime,CAC,  DAX, NASDAQ,FTSE,KOSPI,SGXNifty,Nikkei225,StraitsTimes,HangSeng,TaiwanWeighted,SETComposite,JakartaComposite,ShanghaiComposite)
    values  ({adate},{atime}, '{CAC}','{DAX}', '{NASDAQ}', '{FTSE}', '{KOSPI}','{SGXNifty}','{Nikkei225}','{StraitsTimes}','{HangSeng}','{TaiwanWeighted}','{SETComposite}','{JakartaComposite}','{ShanghaiComposite}' )'''
    sql = sql.format(adate='curdate()', atime='CURRENT_TIME()',  CAC=indices['CAC'],  DAX=indices['DAX'], NASDAQ=indices['Nasdaq'], FTSE=indices['FTSE'],
                     KOSPI=indices['KOSPI'],SGXNifty=indices['SGX Nifty'],Nikkei225=indices['Nikkei 225'],StraitsTimes=indices['Straits Times'],
                     HangSeng=indices['Hang Seng'],TaiwanWeighted=indices['Taiwan Weighted'],SETComposite=indices['SET Composite'],
                     JakartaComposite=indices['Jakarta Composite'],ShanghaiComposite=indices['Shanghai Composite'])
    db.executeSQL(sql)

def update_max_pain(refid, maxpain, pcr):
    sql="UPDATE optionchainref SET maxpain = getMaxPain(id), pcr={pcr} WHERE id={refid} "
    db.executeSQL(sql.format(pcr=pcr, refid=refid))

def get_crref_newid() :
    return db.getScalarOne ("select max(Id) + 1 from optionchainref ")[0]

def updaterank(refid, oldrefid):
    sql = '''
    WITH vals AS (
    SELECT refid, id, symbol, expirydate, strikeprice, pece, oidiff, ivdiff, volume, voldiff,
    rank() over (PARTITION BY refid, symbol, expirydate, pece ORDER BY oidiff DESC) AS oirank,
    rank() over (PARTITION BY refid, symbol, expirydate, pece ORDER BY oidiff) AS oirankdown,
    rank() over (PARTITION BY refid, symbol, expirydate, pece ORDER BY ivdiff DESC) AS ivrank,
    rank() over (PARTITION BY refid, symbol, expirydate, pece ORDER BY voldiff DESC) AS volrank
    FROM
    (select o.refid, o.id, oref.symbol, oref.expirydate, o.strikeprice, o.pece, o.volume,
    o.oi - oprev.oi as oidiff, round(o.iv - oprev.iv, 1) as ivdiff, o.volume - oprev.volume as voldiff
    FROM optionchain o join optionchainref oref ON o.RefId=oref.ID
    join optionchain oprev on oprev.strikeprice = o.strikeprice and oprev.pece = o.pece
    WHERE o.refid ={refid} and oprev.refid={oldrefid}) as diff
    )
    update optionchain as o, vals
    set o.oirank1m = if (vals.oidiff >0, if(vals.oirank<{maxval} < {maxval}, vals.oirank, {maxval}), 0)
    , o.oirankdown1m = if (vals.oidiff <0, if(vals.oirankdown<{maxval}, vals.oirankdown, {maxval}), 0)
    , o.volrank1m = if (vals.voldiff>0, if(vals.volrank<{maxval}, vals.volrank, {maxval}), 0)
    , o.ivrank1m=if(ivdiff!=0,  if(vals.ivrank<{maxval}, vals.ivrank, {maxval}), 0)
    , o.oi_change = vals.oidiff
    where o.id=vals.id and o.refid={refid}
    '''
    sql = sql.format(refid=refid, oldrefid=oldrefid, maxval=40)
    db.executeSQL(sql)

def getnewdate():
   sql="select adddate( max(date),interval 1 day )from dayprop " 
   #sql=sql.format(date=dt)
   return db.getScalar(sql)

def check_if_dayprop_url_exists(url):
    sql='''SELECT count(1) FROM dayprop WHERE Nifty_Bramesh='{url}'  '''
    sql=sql.format(url=url)
    count=db.getScalar(sql)
    return True if count > 0 else False

def save_dayprop_url(NF_url,BN_url,date):
   sql = '''insert into dayprop (date,BN_Bramesh,Nifty_Bramesh)
   values  ('{date}', '{BN_Bramesh}','{Nifty_Bramesh}')'''
   sql=sql.format(date=(getnewdate().strftime("%Y-%m-%d")),BN_Bramesh=BN_url,Nifty_Bramesh=NF_url)
   db.executeSQL(sql)

def getDateTimeDiff(fromDate, toDate):
    dateDiffQuery = '''SELECT b.slno - a.slno +1  FROM dateserial a, dateserial b
                        WHERE a.ADate = \''''+fromDate.strftime("%Y/%m/%d")+'''\' 
                        AND b.adate = \''''+toDate.strftime("%Y/%m/%d")+'\''
    noOfDays = db.getScalar(dateDiffQuery)
    return noOfDays;

def getLatestDate(adate):
    if not cfg.STUB:
        sql = "select max(adate) from dateserial where adate <= '" + adate.strftime("%Y-%m-%d")  + "'"
        return db.getScalar(sql)
    else:
        return adate

def getNextExpiry(adate):
    sql = "select min(adate) from dateserial where adate >= '" + adate.strftime("%Y-%m-%d")  + "' and isexpiry=true"
    return db.getScalar(sql)

def getoptionvals(asondate, expiry, strike, cepe):
    sql = f'''SELECT asondate, ltp
        from optionchainref r JOIN optionchain o
        ON o.RefId = r.ID
        WHERE refid IN (SELECT id FROM optionchainref 
        WHERE DATE(asondate) =  DATE('{asondate}')
        and expirydate =  '{expiry}'
        )
        AND strikeprice = {strike}
        AND pece = '{cepe}'
    '''
    d = db.getDict(sql)
    d1 = {}
    for key in d:
        key1 = key.replace(second=0)
        d1[key1] = d[key]
    return d1

def getCurrentExpiry(dt = datetime.now().date()):
    return getNextExpiry(dt)

if __name__ == '__main__':
    print(get_ks_instruments())