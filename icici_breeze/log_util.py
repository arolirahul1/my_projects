# -*- coding: utf-8 -*-
"""
Logging utility, 
"""
from config.config import Config
import logging.config
#logging.config.fileConfig ('config/logging.ini', disable_existing_loggers=True)
#logger = logging.getLogger()
#def getLogger(name):
#    return logging.getLogger(name)
import logging
logging.basicConfig(filename='app.log', level=logging.INFO, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d-%H:%M:%S")

def info(msg):
    logging.info (msg)
    
def error(msg, err = None):
    print (f"{msg} {err}")
    if err is None:
        logging.error (f"{msg}", exc_info=True )
    else:
        #if err is not None:
        #    raise err
        logging.error (f"{msg} - {err}" )
        

def debug(msg, msg1="", msg2="", msg3="", msg4="", msg5=""):
    """
    Writes the logging messages in to default logging config
    """
    if 1==1: #Config.DEBUG:
        if msg1 == "":
            print (f"{msg}")
            logging.debug (msg)

            #logging.debug(msg)
        else:
            print (f"{msg}, {msg1}, {msg2}, {msg3}, {msg4}, {msg5}")