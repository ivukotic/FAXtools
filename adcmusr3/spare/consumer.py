#!/usr/bin/env python

import stomp
import sys
import time
import pickle
import logging, logging.handlers
import config, ConfigParser

LOG_FILENAME = '/tmp/FAX_monitoring.log'
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG, format=FORMAT)
logger = logging.getLogger('consumer')

config = ConfigParser.ConfigParser()
config.read("neet.cfg")
HOST = config.get("Connection", "HOST")
PORT = int(config.get("Connection", "PORT"))
QUEUE = config.get("Connection", "QUEUE")


class MyListener(object):

    def on_connecting(self, host_and_port):
        logger.info('Connecting...')

    def on_disconnected(self):
        logger.info('Lost connection!')

    def on_message(self, headers, body):
        self.__print_async("MESSAGES", headers, body)
        self.__save(body)

    def on_error(self, headers, body):
        self.__print_async("ERROR", headers, body)

    def on_receipt(self, headers, body):
        self.__print_async("RECEIPT", headers, body)

    def on_connected(self, headers, body):
        self.__print_async("CONNECTED", headers, body)

    def __print_async(self, frame_type, headers, body):

        logger.info('\r  \r%s'%frame_type)
       
        for header_key in headers.keys():
            logger.info('%s: %s' % (header_key, headers[header_key]))
           
        logger.info('%s\n\n'%body)

    def __save(self, body):

        report = pickle.loads(body)
        if not report.has_key('machine') or not report.has_key('xml'):
            logger.info('Incorrect message')
            return
               
        f=open('/var/www/html/sls/%s.xml'%report['id'],'w')
        f.write(report['xml'])
        f.close()
        logger.info('Message correctly saved for %s' %report['machine'])
       

def startListener():
    conn = stomp.Connection([(HOST,PORT)])
    conn.set_listener('MyConsumer', MyListener())
    conn.start()
    conn.connect()
   
    conn.subscribe(destination = QUEUE, ack = 'auto', headers = {})
    return conn

 
def run():
    logger.info('Starting up the consumer')
    conn=startListener()

    i=0
    while i<30:
        try:
            if not conn.is_connected():
                logger.info('Reconnecting ...')
                try:
                    conn.stop()
                except:
                    pass
                conn=startListener()

            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt detected. Closing connection to activeMQ and leaving...")
            conn.disconnect()
            logger.info("DISCONNECTED")
            sys.exit(0)
        except:
            excType, excValue, excStack = sys.exc_info()
            logger.error('Exception: %s \n%s' %(excValue, traceback.format_exc()))
        i+=1
           
    logger.info("Consumer going to disconnect...")
    conn.disconnect()
    logger.info("DISCONNECTED")
                       
if __name__ == '__main__':
    run()
