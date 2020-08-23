#!/usr/bin/python3
#encoding:utf-8

# Simple MQTT publishing from water flow sensor yf-s201 on RPI
#
# Written and (C) 2020 by Lubomir Kamensky <lubomir.kamensky@gmail.com>
# Provided under the terms of the MIT license
#
# Requires:
# - Eclipse Paho for Python - http://www.eclipse.org/paho/clients/python/

import os
import logging
import logging.handlers
import time
import paho.mqtt.client as mqtt
import sys
import configparser
import RPi.GPIO as GPIO 
import time
import statistics
import argparse

parser = argparse.ArgumentParser(description='Simple MQTT publishing from water flow sensor yf-s201 on RPI')
parser.add_argument('--configuration', help='Configuration file. Required!')
args=parser.parse_args()

GPIO.setmode(GPIO.BCM)                                 #Set GPIO pin numbering 
config = configparser.ConfigParser()
config.read(os.path.join(sys.path[0], args.configuration))

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

topic=config['MQTT']['topic']
if not topic.endswith("/"):
    topic+="/"
frequency=int(config['MQTT']['frequency'])

lastValue = {}

INPT = int(config['GpioPins']['inpt'])
CONSTANT= float(config['Calibration']['constant'])
TOT_CNT = int(config['Calibration']['tot_cnt'])

class Element:
    def __init__(self,row):
        self.topic=row[0]
        self.value=row[1]

    def publish(self):
        try:
            if self.value!=lastValue.get(self.topic,0) or config['MQTT']['onlychanges'] == 'False':
                lastValue[self.topic] = self.value
                fulltopic=topic+self.topic
                logging.info("Publishing " + fulltopic)
                mqc.publish(fulltopic,self.value,qos=0,retain=False)

        except Exception as exc:
            logging.error("Error reading "+self.topic+": %s", exc)

try:
    mqc=mqtt.Client()
    mqc.connect(config['MQTT']['host'],int(config['MQTT']['port']),10)
    mqc.loop_start()

    print("Flow measurement in progress")
    GPIO.setup(INPT,GPIO.IN)                         #Set pin as GPIO in
    rate_cnt = 0
    time_zero = time.time()
    time_start = 0.0
    time_end = 0.0
    gpio_last = 0
    pulses = 0
    
    while True:
        close_time=time.time()+frequency
        totalFlow=[]
        minuteFlow=[]

        while True:
            if time.time()>close_time:
                data = []
                row = ["totalFlow"]
                row.insert(1,max(totalFlow))
                data.append(row)
                row = ["minuteFlow"]
                row.insert(1,statistics.mean(minuteFlow))
                data.append(row)
                elements=[]

                for row in data:
                    e=Element(row)
                    elements.append(e)

                for e in elements:
                    e.publish()

                config.set('Calibration', 'tot_cnt', tot_cnt)
                break

            rate_cnt = 0
            pulses = 0
            time_start = time.time()

            while pulses <= 5:
                gpio_cur = GPIO.input(INPT)

                if gpio_cur != 0 and gpio_cur != gpio_last:
                    pulses += 1
                    gpio_last = gpio_cur

            rate_cnt += 1
            tot_cnt += 1
            time_end = time.time()

            print('\nLiters / min ' , round((rate_cnt * constant) / (time_end-time_start), 2) , 'approximate')
            minuteFlow.append(round((rate_cnt * constant) / (time_end-time_start), 2))
            print('Total Liters ', round(tot_cnt * constant,1))
            totalFlow.append(round(tot_cnt * constant,1))

except Exception as e:
    logging.error("Unhandled error [" + str(e) + "]")
    sys.exit(1)
    
