import machine
import time

INTERVAL = 500
IMPULS_TIME = 100


def increase_interval_callback(pin):
    global INTERVAL
    INTERVAL += 100

def decrease_interval_callback(pin):
    global INTERVAL
    if INTERVAL >= 200:
        INTERVAL -= 100

button_increase = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)
button_decrease = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
button_increase.irq(trigger=machine.Pin.IRQ_FALLING, handler=increase_interval_callback)
button_decrease.irq(trigger=machine.Pin.IRQ_FALLING, handler=decrease_interval_callback)
output_pin = machine.Pin(3, machine.Pin.OUT)

def send_impulse():
    while True:
        output_pin.on()
        time.sleep_ms(IMPULS_TIME)  
        output_pin.off() 
        time.sleep_ms(INTERVAL)  

if __name__ == '__main__':
    send_impulse()