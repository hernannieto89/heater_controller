#!/usr/bin/python
"""
Heater Controller - Main module.
"""
import argparse
import time
from helpers import check_sudo, setup_sensor, get_ht, setup_controller, work, got_to_work


def main():
    """
    Heater Controller.
    """
    check_sudo()
    parser = argparse.ArgumentParser(description='Heater Controller..')
    parser.add_argument('--pin-heater',
                        action='store',
                        dest='pin-heater',
                        type=int,
                        required=True,
                        help='raspberry pins GPIO.BCM mode for heater')
    parser.add_argument('--pin-dht',
                        action='store',
                        dest='pin_dht',
                        type=int,
                        required=True,
                        help='raspberry pins GPIO.BCM mode for sensor')
    parser.add_argument('--work_time',
                        action='store',
                        dest='work_time',
                        type=int,
                        required=True,
                        help='work time for job (in seconds)')
    parser.add_argument('--sleep_time',
                        action='store',
                        dest='sleep_time',
                        type=int,
                        required=True,
                        help='sleep time for job (in seconds)')
    parser.add_argument('--start_time',
                        action='store',
                        dest='start_time',
                        type=int,
                        required=True,
                        help='start time for timer (between 0 and 23)')
    parser.add_argument('--end_time',
                        action='store',
                        dest='end_time',
                        type=int,
                        required=True,
                        help='end time for timer (between 0 and 23)')

    args = parser.parse_args()
    # sanitizes args
    pin_dht = args.pin_dht
    pin_heater = args.pin_heater
    work_time = args.work_time
    sleep_time = args.sleep_time
    start = args.start_time
    end = args.end_time
    # setup GPIO
    sensor = setup_sensor(pin_dht)
    setup_controller(pin_heater)

    while True:
        on_time = got_to_work(start, end)
        if on_time:
            try:
                humidity, temperature = get_ht(sensor, pin_dht)
            except Exception:
                temperature = 99
                humidity = 99

            if temperature < 20:
                work(pin_heater, work_time)
            else:
                time.sleep(sleep_time)

    # Reset GPIO settings
    # teardown()


if __name__ == "__main__":
    main()