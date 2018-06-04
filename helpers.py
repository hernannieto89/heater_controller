import os
import sys
import time
import datetime

import RPi.GPIO as GPIO
import Adafruit_DHT


DELAY_INTERVAL = 5
MAX_RETRIES = 5
FILE_NAME = '/home/pi/stadistics.txt'

def setup_sensor(pin):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    sensor = Adafruit_DHT.DHT22
    return sensor


def setup_controller(pin):
    GPIO.cleanup(pin)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)


def check_sudo():
    """
    Checks for superuser privileges.
    :return: None
    """
    if os.getuid() != 0:
        print >> sys.stderr, "You need to have root privileges to run this script.\n" \
                             "Please try again, this time using 'sudo'. Exiting."
        sys.exit(1)


def get_ht(sensor, pin):
    tries = 0
    try:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        while out_of_range(humidity) or out_of_range(temperature):
            register_to_disk(temperature, humidity, "Out of Range - Beginning try {0}".format(tries))
            tries += 1
            time.sleep(DELAY_INTERVAL)
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
            if tries > MAX_RETRIES:
                raise Exception
    except Exception:
        humidity = 101.
        temperature = 101.
        register_to_disk(temperature, humidity, "Exception reading.")
    return humidity, temperature


def out_of_range(value):
    return value > 100


def work(pin_heater, work_time, sensor, pin_dht):
    counter = 0

    GPIO.setup(pin_heater, GPIO.IN)
    if GPIO.input(pin_heater) != GPIO.LOW:
        GPIO.setup(pin_heater, GPIO.OUT)
        GPIO.output(pin_heater, GPIO.LOW)

    humidity, temperature = get_ht(sensor, pin_dht)
    register_to_disk(temperature, humidity, "Beginning to work.".format(counter))
    while counter < work_time:
        if humidity < 25 or temperature > 18:
            break
        humidity, temperature = get_ht(sensor, pin_dht)
        counter += 10
        register_to_disk(temperature, humidity, "Working... Elapsed time: {0} seconds".format(counter))
        time.sleep(10)

    register_to_disk(temperature, humidity, "Work finished. Beginning to rest.".format(counter))
    GPIO.setup(pin_heater, GPIO.IN)
    if GPIO.input(pin_heater) != GPIO.HIGH:
        GPIO.setup(pin_heater, GPIO.OUT)
        GPIO.output(pin_heater, GPIO.HIGH)


def got_to_work(start, end):
    """
    Ask if actual hour is within start - end range.
    :param start:
    :param end:
    :return: Boolean
    """
    now = datetime.datetime.now()
    now_time = now.time()
    start_time = datetime.time(start)
    end_time = datetime.time(end)

    if start_time < end_time:
        return now_time >= start_time and now_time <= end_time
    # Over midnight
    return now_time >= start_time or now_time <= end_time


def register_to_disk(temperature, humidity, message):
    with open(FILE_NAME, 'a') as the_file:
        the_file.write(message + '\n')
        the_file.write('Temp={0:0.1f}*  Humidity={1:0.1f}%\n'.format(temperature, humidity))