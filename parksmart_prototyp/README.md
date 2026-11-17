# ParkSmart – Smart Parking (Hochschul-Demonstrator)

Ein browserbasierter Reservierungsprototyp für vier Stellplätze. Es gibt **keine externen Python-Abhängigkeiten** für die Simulation; SQLite und der Webserver sind bereits Bestandteil von Python. Optional steuert `gpiozero` auf dem Raspberry Pi reale LED-Paare.

**Wichtig:** Nur Lehr-/Vorführsystem ohne Benutzeranmeldung und Zugriffsrechte. Nicht öffentlich ins Internet stellen, nicht als echtes Buchungs-/Zufahrtssystem einsetzen.

## 1. Sofort auf einem Windows-PC testen (ohne Raspberry Pi)

Python 3.10 oder neuer installieren. Projekt entpacken. Terminal im Ordner `parksmart_prototyp` öffnen:

```powershell
python server.py
```

Falls Windows `python` nicht erkennt: `py server.py` verwenden.

Danach im Browser **http://127.0.0.1:8000** öffnen. App startet im Simulationsmodus. Es muss nichts zusätzlich mit pip installiert werden.

## 2. Start auf einem Raspberry Pi 4/5

Raspberry Pi OS mit Python 3 installieren, Pi im WLAN. Projektordner auf den Pi kopieren und starten:

```bash
cd parksmart_prototyp
PARKSMART_HOST=0.0.0.0 python3 server.py
```

Am Pi unter `http://127.0.0.1:8000` öffnen. Auf einem Handy, das **im selben WLAN** ist, `http://<IP-DES-PI>:8000` öffnen. Die IP findet ihr z. B. mit `hostname -I`. Die Freigabe an `0.0.0.0` ist nur für ein vertrauenswürdiges lokales Testnetz gedacht.

## 3. Echte LEDs anschließen

Benötigt werden: 4 rote LEDs, 4 grüne LEDs, 8 Widerstände mit **330 Ohm**, Breadboard, Jumperkabel, Raspberry Pi mit Netzteil.

Alle Pins sind **BCM-GPIO-Nummern**, nicht physische Stecker-Pin-Nummern.

| Parkplatz | Rot (GPIO) | Grün (GPIO) |
|--|--:|--:|
| P1 | 17 | 5 |
| P2 | 27 | 6 |
| P3 | 22 | 13 |
| P4 | 23 | 19 |

Für jede LED: GPIO-Pin → 330Ω-Vorwiderstand → langes LED-Bein (Anode, +); kurzes LED-Bein (Kathode, −) → gemeinsamer GND am Pi.

**Raspberry Pi vor dem Verkabeln vollständig ausschalten und von der Stromversorgung trennen.** Keine 5/12/24V direkt an GPIO-Pins legen. LED nie ohne Widerstand anschließen. Bei Unsicherheit Schaltung vor Inbetriebnahme prüfen lassen.

GPIO Zero über Systempakete installieren (Pi OS):

```bash
sudo apt update
sudo apt install -y python3-gpiozero python3-lgpio
```

Dann im Projektordner **ohne virtuelle Umgebung**:

```bash
PARKSMART_HOST=0.0.0.0 PARKSMART_LED_MODE=real GPIOZERO_PIN_FACTORY=lgpio python3 server.py
```

Für Raspberry Pi 5 ist `lgpio` der geeignete Pin-Backend. Falls Pakete anders heißen, zuerst die Paketverfügbarkeit auf dem verwendeten OS prüfen. Falls die GPIO-Initialisierung fehlschlägt, arbeitet die Webseite mit LEDs im Simulationsmodus weiter.

## 4. Was passiert bei einer Buchung?

- Buchung von **morgen** wird sofort in der Datenbank für morgen gespeichert; am realen Parkplatz bleiben heute die heutigen LED-Zustände sichtbar.
- Wenn morgen der nächste Tag ist, aktualisiert das System die realen LEDs spätestens innerhalb von 10 Sekunden.
- Für die Präsentation klickt ihr auf **„Gewählten Tag am Modell anzeigen“**. Jetzt wird der Buchungstag auf das physische Modell gespiegelt. Rot = gebucht, Grün = frei.
- **„Auf heutigen Tag umstellen“** stellt den normalen Betrieb wieder her.
- **„Demo-Buchungen löschen“** löscht alle Reservierungen aus der lokalen Demo-Datenbank.

## 5. Beispiel für die Präsentation

1. Vorführung vorbereiten: Demo-Daten löschen, Mitarbeiterkürzel `PT01` eingeben, morgen als Datum wählen.
2. P2 buchen. P2 wird in der App rot angezeigt, die anderen Parkplätze grün.
3. Den Präsentationsmodus aktivieren. Physische LED an P2 wird rot, P1/P3/P4 leuchten grün.
4. Zweiten Browser öffnen und P2 erneut buchen: Buchung wird abgelehnt (Doppelbuchungsschutz).
5. Mit gleichem Mitarbeiterkürzel P2 stornieren. P2 wird wieder grün.

## 6. Was der Prototyp bereits leistet

- Tagesreservierung für heute bis 14 Tage im Voraus (Standarddatum: morgen).
- Ein Platz höchstens einmal je Tag und ein Mitarbeiterkürzel höchstens einmal je Tag.
- Persistente Speicherung in SQLite (`parksmart.sqlite3`).
- Stornierung mit dem bei Buchung verwendeten Mitarbeiterkürzel (keine echte Sicherheit).
- Raspberry-Pi-LED-Steuerung und ohne Pi nutzbare Simulation.
- Responsives Interface für Smartphone und Desktop.

## 7. Explizite Grenzen des MVP

**Kein Login, keine echte Identitätsprüfung, keine Verschlüsselung im lokalen HTTP-Zugriff, kein Rollenmodell, keine Schrankensteuerung, keine Fahrzeuge-/Belegungserkennung, keine automatische No-Show-Freigabe, kein echtes Campus-Parkraummanagement.** Mitarbeiterkürzel sind Testdaten. Die Platzvergabe funktioniert nur, wenn alle Beteiligten das Reservierungssystem und die Reservierungen respektieren. Ein echter Pilot müsste u. a. Unternehmens-SSO, datenschutzkonforme Speicherdauer, Berechtigungskonzept, Netzwerk-/Betriebssicherheit und reale Stellplatzorganisation ergänzen.

## 8. Projektstruktur

- `server.py` – HTTP-Server, SQLite, Geschäftslogik, GPIO-Ansteuerung
- `static/index.html` – Oberfläche
- `static/style.css` – Design für Handy und PC
- `static/app.js` – Benutzerinteraktion, Buchung und LED-Vorschau
- `tests/test_parksmart.py` – automatisierte Logiktests
- `PRAESENTATION_UND_BUSINESS_CASE.md` – Management-Storyline und Projektplan

## 9. Projekt testen

```bash
python -m unittest discover -s tests -v
```

Bitte nur mit Testkürzeln arbeiten. Das ist kein für Produktion geeignetes Campus-System.
