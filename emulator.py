import machine
import time

INTERVAL = 1000
IMPULS_TIME = 100
TOLLERANCE = 200

last_increase_time = 0
last_decrease_time = 0

def increase_interval_handler(*args,**kwargs):
    global INTERVAL, last_increase_time
    if time.ticks_ms() - last_increase_time > TOLLERANCE:
        INTERVAL += 100
        last_increase_time = time.ticks_ms()

def decrease_interval_handler(*args,**kwargs):
    global INTERVAL, last_decrease_time
    if time.ticks_ms() - last_decrease_time > TOLLERANCE:
        if INTERVAL >= 200:
            INTERVAL -= 100
        last_decrease_time = time.ticks_ms()

button_increase = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)
button_decrease = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
button_increase.irq(trigger=machine.Pin.IRQ_RISING, handler=increase_interval_handler)
button_decrease.irq(trigger=machine.Pin.IRQ_RISING, handler=decrease_interval_handler)
output_pin = machine.Pin(3, machine.Pin.OUT)

def send_impulse():
    global INTERVAL
    while True:
        output_pin.on()
        time.sleep_ms(IMPULS_TIME)  
        output_pin.off() 
        time.sleep_ms(INTERVAL)  

if __name__ == '__main__':
    send_impulse()