from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

pico_ip = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global pico_ip
    if request.method == 'POST':
        ssid = request.form['ssid']
        password = request.form['password']
        # Tutaj wykonaj żądanie POST na endpoint /log z danymi logowania
        response = requests.post(f'http://{pico_ip}/log', json={'ssid': ssid, 'password': password})
        if response.status_code == 200:
            pico_ip = response.json().get('ip_address')
            return redirect(url_for('endpoints'))
        else:
            return render_template('error.html', error_message=response.json().get('error'))

    return render_template('login.html')

@app.route('/endpoints')
def endpoints():
    global pico_ip
    if pico_ip:
        endpoints_list = [
            {'name': 'Pobierz zużycie wody', 'url': f'http://{pico_ip}/water_usage'},
            {'name': 'Pobierz zużytą wodę', 'url': f'http://{pico_ip}/water_used'},
            {'name': 'Średnie zużycie z ostatnich 12 godzin', 'url': f'http://{pico_ip}/average_usage_last_12_hours'}
        ]
        return render_template('endpoints.html', endpoints=endpoints_list)
    else:
        return render_template('error.html', error_message='Nie można pobrać adresu IP Pico. Spróbuj ponownie.')

if __name__ == '__main__':
    app.run(debug=True)