"""ParkSmart: demonstrierbarer Parkplatz-Reservierungsprototyp.
Standardbibliothek-only; auf dem Raspberry Pi optional gpiozero fuer echte LEDs.
ACHTUNG: Lokaler Hochschul-Demonstrator ohne Nutzer-Authentifizierung.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('PARKSMART_DB', str(ROOT / 'parksmart.sqlite3')))
HOST = os.environ.get('PARKSMART_HOST', '127.0.0.1')
PORT = int(os.environ.get('PARKSMART_PORT', '8000'))
LED_MODE = os.environ.get('PARKSMART_LED_MODE', 'simulation').lower()
SPOTS = (
    {'id': 'P1', 'red': 17, 'green': 5},
    {'id': 'P2', 'red': 27, 'green': 6},
    {'id': 'P3', 'red': 22, 'green': 13},
    {'id': 'P4', 'red': 23, 'green': 19},
)
VALID_SPOTS = {p['id'] for p in SPOTS}


def db_connection():
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.execute('PRAGMA busy_timeout=10000')
    return conn


def initialize_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with db_connection() as con:
        con.executescript('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY,
                day TEXT NOT NULL,
                spot_id TEXT NOT NULL,
                owner TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(day, spot_id),
                UNIQUE(day, owner)
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        ''')


def valid_day(raw):
    if not isinstance(raw, str):
        raise ValueError('Bitte ein gueltiges Datum angeben.')
    try:
        day = date.fromisoformat(raw)
    except ValueError:
        raise ValueError('Bitte ein Datum im Format JJJJ-MM-TT angeben.') from None
    if day < date.today() or day > date.today() + timedelta(days=14):
        raise ValueError('Buchbar sind heute und die naechsten 14 Tage.')
    return day.isoformat()


def owner_code(raw):
    if not isinstance(raw, str):
        raise ValueError('Bitte ein Mitarbeiterkuerzel eingeben.')
    code = raw.strip().upper()
    if not (2 <= len(code) <= 24) or not all(c.isalnum() or c in ('-', '_') for c in code):
        raise ValueError('Kuerzel: 2-24 Zeichen, nur Buchstaben, Zahlen, - oder _.')
    return code


def booked_ids(day):
    with db_connection() as con:
        return {row[0] for row in con.execute('SELECT spot_id FROM bookings WHERE day=?', (day,))}


def get_setting(key):
    with db_connection() as con:
        row = con.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
    return row[0] if row else ''


def led_day():
    preview = get_setting('preview_day')
    if preview:
        try:
            return valid_day(preview)
        except ValueError:
            pass
    return date.today().isoformat()


def get_state(day):
    reservations = booked_ids(day)
    led_selected = led_day()
    illuminated = booked_ids(led_selected)
    return {
        'date': day,
        'today': date.today().isoformat(),
        'tomorrow': (date.today() + timedelta(days=1)).isoformat(),
        'max_date': (date.today() + timedelta(days=14)).isoformat(),
        'preview_date': get_setting('preview_day'),
        'led_date': led_selected,
        'led_mode': HARDWARE.mode,
        'spots': [{'id': p['id'], 'reserved': p['id'] in reservations} for p in SPOTS],
        'leds': [{'id': p['id'], 'red': p['id'] in illuminated} for p in SPOTS],
        'reserved_count': len(reservations),
    }


def create_booking(payload):
    day = valid_day(payload.get('date'))
    spot = payload.get('spot')
    if spot not in VALID_SPOTS:
        raise ValueError('Unbekannter Parkplatz.')
    owner = owner_code(payload.get('owner'))
    try:
        with db_connection() as con:
            con.execute('INSERT INTO bookings(day, spot_id, owner) VALUES(?,?,?)', (day, spot, owner))
    except sqlite3.IntegrityError:
        raise ValueError('Parkplatz bereits reserviert oder fuer dieses Kuerzel besteht schon eine Buchung an diesem Tag.') from None
    HARDWARE.update()
    return {'message': f'{spot} fuer {day} erfolgreich reserviert.', 'spot': spot, 'date': day}


def cancel_booking(payload):
    day = valid_day(payload.get('date'))
    spot = payload.get('spot')
    if spot not in VALID_SPOTS:
        raise ValueError('Unbekannter Parkplatz.')
    owner = owner_code(payload.get('owner'))
    with db_connection() as con:
        cur = con.execute('DELETE FROM bookings WHERE day=? AND spot_id=? AND owner=?', (day, spot, owner))
        if cur.rowcount != 1:
            raise ValueError('Buchung nicht gefunden oder Kuerzel stimmt nicht.')
    HARDWARE.update()
    return {'message': f'Reservierung von {spot} storniert.'}


def set_preview(payload):
    value = payload.get('date')
    if value in ('', None):
        day = ''
    else:
        day = valid_day(value)
    with db_connection() as con:
        con.execute('INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', ('preview_day', day))
    HARDWARE.update()
    return {'message': 'LED-Vorschau aktiviert.' if day else 'Echtzeitmodus aktiviert.'}


def reset_demo():
    with db_connection() as con:
        con.execute('DELETE FROM bookings')
        con.execute('DELETE FROM settings WHERE key=?', ('preview_day',))
    HARDWARE.update()
    return {'message': 'Demo-Daten geloescht.'}


class LEDHardware:
    def __init__(self):
        self.mode = 'Simulation'
        self.pins = {}
        self.lock = threading.Lock()
        if LED_MODE != 'real':
            return
        try:
            from gpiozero import LED
            self.pins = {p['id']: (LED(p['red']), LED(p['green'])) for p in SPOTS}
            self.mode = 'Echte GPIO-LEDs'
        except Exception as exc:
            self.mode = f'Simulation (GPIO-Fehler: {type(exc).__name__})'
            print(f'[ParkSmart] GPIO nicht verfuegbar: {exc}')

    def update(self):
        if not self.pins:
            return
        try:
            with self.lock:
                reserved = booked_ids(led_day())
                for spot_id, (red, green) in self.pins.items():
                    if spot_id in reserved:
                        green.off()
                        red.on()
                    else:
                        red.off()
                        green.on()
        except Exception as exc:
            print(f'[ParkSmart] LED-Update fehlgeschlagen: {exc}')


HARDWARE = LEDHardware()


class ParkSmartHandler(BaseHTTPRequestHandler):
    def send_json(self, value, status=200):
        blob = json.dumps(value, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(blob)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(blob)

    def send_file(self, filename, content_type):
        data = (ROOT / filename).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        files = {'/': ('static/index.html', 'text/html; charset=utf-8'),
                 '/static/style.css': ('static/style.css', 'text/css; charset=utf-8'),
                 '/static/app.js': ('static/app.js', 'application/javascript; charset=utf-8')}
        if parsed.path in files:
            self.send_file(*files[parsed.path])
            return
        if parsed.path == '/api/state':
            params = parse_qs(parsed.query)
            raw_day = params.get('date', [(date.today() + timedelta(days=1)).isoformat()])[0]
            try:
                self.send_json(get_state(valid_day(raw_day)))
            except ValueError as exc:
                self.send_json({'error': str(exc)}, 400)
            return
        self.send_json({'error': 'Nicht gefunden.'}, 404)

    def do_POST(self):
        path = urlparse(self.path).path
        actions = {'/api/book': create_booking,
                   '/api/cancel': cancel_booking,
                   '/api/preview': set_preview,
                   '/api/reset': lambda _: reset_demo()}
        if path not in actions:
            self.send_json({'error': 'Nicht gefunden.'}, 404)
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length > 4096:
                self.send_json({'error': 'Anfrage zu gross.'}, 413)
                return
            data = json.loads(self.rfile.read(length).decode('utf-8'))
            if not isinstance(data, dict):
                raise ValueError('Ungueltige Anfrage.')
            self.send_json(actions[path](data))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.send_json({'error': str(exc)}, 400)
        except sqlite3.Error as exc:
            print(f'[ParkSmart] Datenbankfehler: {exc}')
            self.send_json({'error': 'Datenbankfehler.'}, 500)


def led_refresh_loop():
    while True:
        HARDWARE.update()
        time.sleep(10)


def main():
    initialize_db()
    HARDWARE.update()
    threading.Thread(target=led_refresh_loop, daemon=True).start()
    server = ThreadingHTTPServer((HOST, PORT), ParkSmartHandler)
    print(f'ParkSmart gestartet: http://{HOST}:{PORT} | GPIO: {HARDWARE.mode}')
    print('ACHTUNG: Hochschul-Demo ohne Logins. Nicht ins Internet freigeben.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
