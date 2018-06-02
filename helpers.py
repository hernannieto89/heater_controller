import os
import sys
import time

import RPi.GPIO as GPIO
import Adafruit_DHT


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
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity > 100 or temperature > 100:
        time.sleep(3)
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        if humidity > 100 or temperature > 100:
            raise Exception
    return humidity, temperature


def work(pin, work_time):

    GPIO.setup(pin, GPIO.IN)
    if GPIO.input(pin) != GPIO.LOW:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    time.sleep(work_time)
    GPIO.setup(pin, GPIO.IN)
    if GPIO.input(pin) != GPIO.HIGH:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
