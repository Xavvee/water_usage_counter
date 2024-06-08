import time
import threading
from machine import mem32
from microdot import Microdot, Response
import network
import ujson

# Konfiguracja punktu dostępu Wi-Fi
AP_SSID = 'PicoW_Setup'
AP_PASSWORD = '12345678'
AP_IP = '192.168.4.1'
AP_NETMASK = '255.255.255.0'
AP_GATEWAY = '192.168.4.1'

# Utworzenie punktu dostępu
ap = network.WLAN(network.AP_IF)
ap.config(essid=AP_SSID, password=AP_PASSWORD)
ap.ifconfig((AP_IP, AP_NETMASK, AP_GATEWAY, AP_GATEWAY))
ap.active(True)

while not ap.active():
    time.sleep(1)

print('Punkt dostępu uruchomiony, IP:', ap.ifconfig()[0])

# Kod Licznika PWM
_conditions = {"FREE": 0x0, "GATED": 0x1, "EDGE_RISING": 0x2, "EDGE_FALLING": 0x3}

class PWMCounter:
    def __init__(self, pin, condition="FREE"):
        assert pin < 30
        assert pin % 2
        self.pin = pin
        self.pin_reg = 0x40014000 + (0x04 + pin * 8)
        self.csr = 0x40050000 + ((pin // 2) * 0x14)
        self.ctr = self.csr + 0x08
        self.condition = condition
        self.setup()
    
    def setup(self):
        mem32[self.pin_reg] = 4
        mem32[self.csr] = (_conditions[self.condition] << 4)
        self.reset()
    
    def start(self):
        mem32[self.csr] |= 1 << 0 
        
    def stop(self):
        mem32[self.csr] &= ~(1 << 0) 
    
    def reset(self):
        mem32[self.ctr] = 0
    
    def read(self):
        return mem32[self.ctr]


class WaterCounter:
    
    def __init__(self):
        self.counter = PWMCounter(15, "EDGE_FALLING")
        self.counter.start()
        self.last_read_time = time.time()
        self.last_ticks = self.counter.read()
        self.hourly_usage = []
        self.lock = threading.Lock()
        self.record_hourly_usage()
    
    def water_usage(self):
        current_time = time.time()
        current_ticks = self.counter.read()
        
        elapsed_time = current_time - self.last_read_time
        tick_difference = current_ticks - self.last_ticks
        
        self.last_read_time = current_time
        self.last_ticks = current_ticks
        
        if elapsed_time > 0:
            return tick_difference / elapsed_time
        else:
            return 0
    
    def water_used(self):
        return self.counter.read()
    
    def record_hourly_usage(self):
        def record():
            while True:
                time.sleep(3600)
                usage = self.water_usage()
                with self.lock:
                    if len(self.hourly_usage) >= 12:
                        self.hourly_usage.pop(0)
                    self.hourly_usage.append(usage)
        
        thread = threading.Thread(target=record, daemon=True)
        thread.start()
    
    def average_usage_last_12_hours(self):
        with self.lock:
            if not self.hourly_usage:
                return 0
            return sum(self.hourly_usage) / len(self.hourly_usage)


water_counter = WaterCounter()
app = Microdot()

@app.route('/log', methods=['POST'])
def log(request):
    data = request.json
    ssid = data.get('ssid')
    password = data.get('password')
    
    if ssid and password:
        ap.active(False)
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)

        ip_address = wlan.ifconfig()[0]
        return {'status': 'Połączono', 'ip_address': ip_address}, 200
    else:
        return {'error': 'Brak ssid lub hasła'}, 400

@app.route('/water_usage')
def get_water_usage(request):
    return {'water_usage': water_counter.water_usage()}

@app.route('/water_used')
def get_water_used(request):
    return {'water_used': water_counter.water_used()}

@app.route('/average_usage_last_12_hours')
def get_average_usage_last_12_hours(request):
    return {'average_usage_last_12_hours': water_counter.average_usage_last_12_hours()}

app.run(host='0.0.0.0', port=80)
