import time
import json

from m365py import m365py
from m365py import m365message

# this sets debug level of m365py
import logging
logging.getLogger('m365py').setLevel(logging.DEBUG)

# callback for received messages from scooter
def handle_message(m365_peripheral, m365_message, value):
    print('Received message => {}'.format(json.dumps(value, indent=4)))

    # check for specific message
    if m365_message.attribute == m365message.Attribute.BATTERY_VOLTAGE:
        print('Battery voltage {} V'.format(value['battery_voltage']))

    if m365_message.attribute == m365message.Attribute.SUPPLEMENTARY:
        if value['kers_mode'] == m365py.KersMode.WEAK:
            print('kers set to weak')


scooter_mac_address = 'D6:0E:DB:7B:EA:AB'
scooter = m365py.M365(scooter_mac_address, handle_message)
scooter.connect()

# Make tail light blink in a blocking fashion, timeout = 2.0
scooter.request(m365message.turn_off_tail_light)
received_within_timeout = scooter.waitForNotifications(2.0)
scooter.request(m365message.turn_on_tail_light)
received_within_timeout = scooter.waitForNotifications(2.0)
scooter.request(m365message.turn_off_tail_light)
received_within_timeout = scooter.waitForNotifications(2.0)

# turn on cruise mode
scooter.request(m365message.turn_on_cruise)
# fetch value to confirm that the scooter cruise mode has been enabled
scooter.request(m365message.cruise_status)
# reset cruise mode
scooter.request(m365message.turn_off_cruise)

# turn on lock
scooter.request(m365message.turn_on_lock)
# fetch value to confirm that the scooter is locked
scooter.request(m365message.lock_status)
# turn off cruise mode
scooter.request(m365message.turn_off_lock)

update_interval_s = 5.0
while True:
    start_time = time.time()

    # Request all currently supported 'attributes'
    scooter.request(m365message.battery_voltage)
    scooter.request(m365message.battery_ampere)
    scooter.request(m365message.battery_percentage)
    scooter.request(m365message.battery_cell_voltages)
    scooter.request(m365message.battery_info)

    scooter.request(m365message.general_info)
    scooter.request(m365message.motor_info)
    scooter.request(m365message.trip_info)
    scooter.request(m365message.trip_distance)
    scooter.request(m365message.distance_left)
    scooter.request(m365message.speed)
    scooter.request(m365message.tail_light_status)
    scooter.request(m365message.cruise_status)
    scooter.request(m365message.supplementary)

    # m365py also stores a cached state of received values
    print(json.dumps(scooter.cached_state, indent=4, sort_keys=True))

    # try to consistently run loop every 5 seconds
    elapsed_time = time.time() - start_time
    sleep_time = max(update_interval_s - elapsed_time, 0)
    time.sleep(sleep_time)

scooter.disconnect()

