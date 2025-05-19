# Malování

Aplikace pro malování vytvořená v Pythonu s využitím PyQt6 s moderním designem. Tato aplikace nabízí rozšířené funkce podobné aplikaci Paint ve Windows, ale s pokročilým uživatelským rozhraním, více nástroji a možnostmi přizpůsobení.

## Funkce

- Moderní uživatelské rozhraní s horními záložkami (ribbon)
- Možnost přepínání mezi světlým a tmavým tématem
- Nastavitelná průhlednost a efekt rozmazání
- Podpora písem Arial a Arial Black pro různé části aplikace

### Nástroje pro kreslení
- Tužka - základní nástroj pro kreslení
- Štětec - kreslení s hladšími okraji
- Guma - mazání částí obrázku
- Text - přidávání textu s možností formátování
- Výplň - vyplnění uzavřených oblastí barvou
- Výběr - výběr a přesun částí obrázku

### Tvary
- Linie - kreslení přímých čar
- Obdélník - kreslení obdélníků
- Zaoblený obdélník - kreslení obdélníků se zaoblenými rohy
- Elipsa - kreslení elips a kruhů
- Trojúhelník - kreslení trojúhelníků
- Pentagon - kreslení pětiúhelníků
- Šestiúhelník - kreslení šestiúhelníků
- Hvězda - kreslení hvězd
- Šipka - kreslení šipek

### Textové funkce
- Výběr z různých fontů
- Nastavení velikosti textu
- Podpora tučného, kurzívy a podtrženého textu
- Zarovnání textu (vlevo, na střed, vpravo)

### Další funkce
- Výběr barvy z palety nebo vlastní barvy
- Nastavení tloušťky čar
- Ukládání a načítání obrázků
- Změna velikosti plátna a zoom
- Funkce zpět/znovu pro neomezené úpravy

## Požadavky

- Python 3.8+
- PyQt6
- numpy (pro některé funkce)
- pytest (pro testy)

## Instalace

```bash
pip install -r requirements.txt
```

## Spuštění

```bash
python main.py
```

## Ribbon záložky

### Domů
- Nástroje pro kreslení
- Výběr tvarů
- Nastavení tloušťky
- Rychlý výběr barev

### Text
- Výběr fontu a velikosti
- Styl textu (tučné, kurzíva, podtržené)
- Zarovnání textu

### Vzhled
- Přepínání mezi světlým a tmavým tématem
- Nastavení průhlednosti aplikace
- Efekt rozmazání
- Změna velikosti plátna

## Klávesové zkratky

- **Ctrl+N** - Nový obrázek
- **Ctrl+O** - Otevřít obrázek
- **Ctrl+S** - Uložit obrázek
- **Ctrl+Z** - Zpět
- **Ctrl+Shift+Z** - Znovu
- **Ctrl+** nebo **Ctrl+=** - Přiblížení
- **Ctrl-** - Oddálení
- **Ctrl+Q** - Ukončit aplikaci

## Boční panel
Obsahuje další nástroje, které se nevešly do horního ribbonu, jako jsou dodatečné tvary (pentagon, šestiúhelník, hvězda).

## Testy

Aplikace obsahuje testy vytvořené pomocí pytest. Pro spuštění testů použijte:

```bash
pytest
```