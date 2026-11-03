# Python_SZOR
Python szorgalmi feladat – robotos sci-fi könyvek elemzése

## Adathalmaz
`sf_robots.csv` – 1250 robotos témájú könyv a Goodreads-ről: cím, szerző, átlagos értékelés
(`Rating_score`), szavazatok száma (`Rating_votes`), szöveges kritikák száma (`Review_number`),
megjelenés éve, műfajcímkék.

**Tisztítás:** a 0-s megjelenési év hiányzó adatnak számít (6 könyv); az értékelést érintő
elemzésekben csak a legalább 10 szavazatot kapott könyvek szerepelnek (1221 könyv).

## Futtatás
```
py -m pip install -r requirements.txt
py elemzes.py
```
Az interaktív Plotly ábrák az `abrak/` mappába kerülnek (HTML, böngészőben nyithatók).

## Kérdések és válaszok

### 1. Jobb értékelést kapnak-e a népszerűbb könyvek?
Mérsékelt pozitív kapcsolat van a szavazatszám logaritmusa és az értékelés között (r ≈ 0,33;
a nyers szavazatszámmal csak r ≈ 0,14, mert a szavazatszám nagyon ferde eloszlású).

| Szavazatok | Könyvek | Átlag | Szórás |
|---|---|---|---|
| 10–100 | 178 | 3,78 | 0,39 |
| 100–1 000 | 405 | 3,82 | 0,32 |
| 1 000–10 000 | 377 | 3,95 | 0,30 |
| 10 000+ | 261 | 4,06 | 0,26 |

Ahogy nő a népszerűség, nő az átlag és csökken a szórás.

### 2. Hogyan változott a robotos könyvek száma és értékelése az évtizedek során?
A könyvek 82%-a 2000 után jelent meg (a 2010-es évtizedben 678 könyv). Az átlagos értékelés
végig ~3,9 körül marad, a csúcs az 1950-es évek (4,11 – Asimov-korszak). Az egy könyvre jutó
medián szavazatszám viszont meredeken csökken: több könyv osztozik a figyelmen.

### 3. Melyik műfajokat értékelik legjobbra?
(Legalább 40 könyvet tartalmazó műfajcímkék, összátlag: 3,91)
- **Legjobbak:** Manga (4,10), Middle Grade gyerekkönyvek (4,05), képregények és grafikus
  regények (~4,03), klasszikusok (4,03)
- **Leggyengébbek:** gyerek képeskönyvek / Storytime (~3,66), Young Adult (Teen) (3,79),
  „Aliens” (3,81) és a kifejezetten „Robots” címkés könyvek (3,82)

### 4. Milyen kapcsolat van a szavazatok és a szöveges kritikák között?
Nagyon erős (log-log skálán r ≈ 0,94). Mediánban kb. minden 9. értékelő ír kritikát is.
Az arány viszont erősen függ a megjelenés idejétől: a 2010 utáni könyveknél a medián arány
0,159, a 2000 előttieknél csak ~0,05. Az új könyvekről tehát az olvasók sokkal inkább írnak
szöveges véleményt, a régi klasszikusokat inkább csak csillagozzák.

### 5. Jobbak / népszerűbbek-e a termékeny szerzők könyvei?
| Szerző könyvei | Szerzők | Átlagos értékelés | Medián szavazat |
|---|---|---|---|
| 1 könyv | 504 | 3,79 | 546 |
| 2–3 könyv | 135 | 3,91 | 1 758 |
| 4+ könyv | 58 | 4,02 | 3 336 |

Igen: a termékenyebb szerzők jobb értékelést és több szavazatot kapnak. A figyelem nagyon
koncentrált – a 697 szerzőből a top 10 (Douglas Adams, Ray Bradbury, Marissa Meyer,
Isaac Asimov, …) gyűjti be az összes szavazat 55%-át.
