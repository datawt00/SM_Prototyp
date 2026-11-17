# ParkSmart – Vorschlag für den Management-Pitch

## Kernbotschaft

„Wir reduzieren die Unsicherheit beim morgendlichen Parken: Mitarbeiter reservieren ihren Parkplatz bereits am Vortag. Ein digitales System verhindert Doppelbuchungen und signalisiert die Reservierung am Stellplatz. Unser Prototyp zeigt die komplette Kette – vom Handy bis zur LED.“

## Storyline – acht Folien

1. **Peter vor dem Arbeitstag:** Ingenieur bei einem Automotive-OEM mit Familie; Campus schwer mit ÖPNV erreichbar, viele fahren Auto; Parkplätze konkurrieren außerdem mit Prototypfahrzeugen.
2. **Das Problem:** Parkplatzsuche kostet Zeit, schafft Stress, beeinträchtigt Planbarkeit. Die Größe des Problems muss im Feld gemessen werden, nicht einfach angenommen.
3. **Die Vision:** „Reserve today. Park tomorrow.“ Peter bucht am Vorabend einen Platz; klare Kennzeichnung am Stellplatz.
4. **Die Nutzerreise:** App öffnen → Datum/Platz auswählen → Reservierung → am richtigen Tag rote LED → direkt parken. Storyboard als Vorher/Nachher.
5. **Architektur und Technologie:** Weboberfläche ↔ Python-Webserver ↔ SQLite ↔ Raspberry Pi GPIO ↔ LEDs.
6. **Live-Prototyp:** P2 buchen, rote LED anzeigen, doppelte Buchung abweisen, Reservierung stornieren.
7. **Business Case:** Suchzeit, Stress, Auslastung, Fairness; Annahmen und Szenarien offen darstellen.
8. **Umsetzungsplan und Entscheidung:** Sechs Wochen MVP; Pilot mit realen Nutzern; klare Kriterien für Go/No-Go.

## Beispielrechenweg (hypothetisch, NICHT erhobene Campus-Daten)

Annahmen: 300 Mitarbeitende, 3 betroffene Arbeitstage pro Woche, 5 Minuten vermiedene Parkplatzsuche, 46 Arbeitswochen pro Jahr.

Zeitersparnis = 300 × 3 × 5 / 60 × 46 = **3.450 Stunden/Jahr**.

Bewertung als monetarisierter Zeitwert bei beispielhaft 35 €/Stunde = **120.750 €/Jahr**. **Keine automatische Budgeteinsparung:** vermeidbare Suchzeit ist nicht zwangsläufig vollständig produktive oder bezahlte Arbeitszeit. Reale Zahl erst nach Vorher-Nachher-Messung, Kostenprüfung und Nutzertests angeben.

Investitionen: Raspberry Pi + Modell + LEDs und Entwicklung/Wartung; echte Standortintegration kann deutlich mehr kosten. Für den Vortrag Hardwareangebot und Entwicklungsaufwand separat kalkulieren.

## Erfolgskennzahlen (Pilot)

- Durchschnittliche Parkplatzsuchzeit vor/nach Einführung, Minuten.
- Anteil erfolgreich eingelöster Reservierungen (%).
- Doppelbuchungen (Ziel: 0 bei systeminternen Reservierungen).
- No-Show-Quote (%).
- Belegte und reservierte Plätze je Tag; Gefahr der künstlichen Verknappung.
- Zufriedenheit von Peter und weiteren Nutzern.
- Aufwand von Facility Management und IT.

## Projektplan für sechs Wochen

- **Woche 1:** Anforderungen definieren, Stakeholder befragen, Parkplatz-Regeln festlegen.
- **Woche 2:** Web-App und Datenmodell implementieren.
- **Woche 3:** LED-Modell mit Raspberry Pi verdrahten, Buchung und Anzeige verbinden.
- **Woche 4:** Testen: Storno, Doppelbuchungen, Datum, Neustart, WLAN-Ausfall; mit Peter/anderen Nutzern Feedback sammeln.
- **Woche 5:** Usability verbessern, Pilotkonzept/Business Case plausibilisieren und Kennzahlen vorbereiten.
- **Woche 6:** Live-Demo proben, Management-Slides abschließen, Code und Präsentation nach Moodle hochladen.

## Erwartbare Management-Fragen

**Warum nicht freie Stellplätze ohne Reservierung anzeigen?** Weil die Kernfrustration im Storyboard fehlende Planbarkeit ist. Eine Reservierung am Vorabend nimmt Unsicherheit bereits vor Fahrtantritt.

**Was passiert, wenn jemand auf dem reservierten Platz parkt?** Die LED allein verhindert keine Falschparker. Ein Pilot braucht Parkplatzregeln, Beschilderung und einen Prozess für Konflikte. Bei hoher Störquote ggf. Sperrbügel oder Zufahrtskontrolle bewerten.

**Was ist mit Prototypfahrzeugen?** Entweder getrennte Stellplatzkontingente oder eine vorrangige, durch Facility Management verwaltete Zuteilung. Nicht jeder Stellplatz darf ohne Regeln öffentlich buchbar sein.

**Wie verhindert ihr reservierte, aber leere Plätze?** Geplant: Buchungsfrist, Check-in, Freigabe bei Nichterscheinen, keine Mehrfachreservierung. Im MVP ist nur die Ein-Buchung-pro-Tag-Regel umgesetzt.

**Was kostet es?** Hardware-Demo und echtes Rollout strikt trennen. Der Demonstrator validiert den Ablauf, nicht den Business Case eines großen Campus.

**Wie wird Datenschutz eingehalten?** Demo nur mit Testkürzeln. Echter Pilot mit Login/SSO, Minimaldatensatz, Rollenrechten, Löschfristen und IT-/Datenschutzfreigabe.

## Abgabe-Checkliste

- Storyboard ✔
- Funktionierende lokale Web-App / LED-Modell ✔ als Codebasis; auf eurer Hardware noch aufzubauen und zu testen
- Anforderungen und Technologiebild ✔
- Userfeedback ❑
- Gemessene Business-Case-Parameter ❑
- Fotos/Video des Hardware-Prototyps ❑
- Management-Präsentation ❑
- Präsentation und Code in Moodle hochladen ❑
