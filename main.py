# For ESP8266
from machine import Pin
from time import sleep, ticks_ms
import constant as c

# Assigning Pins
counter_relay_module = Pin(4, Pin.OUT)
valve_relay_module = Pin(5, Pin.OUT)
register_button = Pin(12, Pin.IN)
led = Pin(13, Pin.OUT)

# Initialize to prevent opening of relay during start up
counter_relay_module.value(c.RELAY_OPEN)
valve_relay_module.value(c.RELAY_OPEN)
led.value(c.LED_OFF)
  
def refill(event='start'):
    if event == 'start':
        valve_relay_module.value(c.RELAY_CLOSE)
        led.value(c.LED_ON)
        counter_relay_module.value(c.RELAY_CLOSE)
        sleep(c.COUNTER_ENERGIZE) # Cannot be lower than 0.2sec to prevent double credits
        counter_relay_module.value(c.RELAY_OPEN)
        print('Refilling started...')
        return event
    elif event == 'stop':
        valve_relay_module.value(c.RELAY_OPEN)
        led.value(c.LED_OFF)
        sleep(c.DEBOUNCE_DELAY)
        print('Refilling done...')
        return event
    else:
        print('Invalid event...')
        return 0

# Use if your register is without WiFi connectivity or internet
def app():
    import json
    from machine import Pin
    
    # Open the configuration file and read the value
    with open('config.json', 'r') as file:
        data = json.load(file)
    
    # Open the valve on a specified duration in seconds
    refill_duration = data["refill_duration_5gal"]
    
    # Initialize variables
    register_button_state = 'stop'
    refill_start_time = 0
    time_elapsed_sec = 0
    
    print('System Start-Up\n')
    
    while True:
        # Start refilling
        if register_button.value() == c.BUTTON_PRESSED and register_button_state == 'stop':
            register_button_state = refill('start')
            refill_start_time = ticks_ms()
      
        # Manual stop refilling
        elif register_button.value() == c.BUTTON_PRESSED and register_button_state == 'start':
            register_button_state = refill('stop')
            print('Time elapsed: {} sec\n'.format(time_elapsed_sec))
     
        # Auto-Stop refilling
        elif time_elapsed_sec >= refill_duration and register_button_state == 'start':
            register_button_state = refill('stop')
            print('Time elapsed: {} sec\n'.format(time_elapsed_sec))
        
        # Compute for the time elapsed after start of refilling
        time_elapsed_sec = (ticks_ms() - refill_start_time)/1000

        
if __name__ == '__main__':
    app()