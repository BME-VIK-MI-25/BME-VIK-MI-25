<h1>BME-VIK-MI-25-</h1>
<table>
    <tr>
      <img align="right" width="135" height="135" src="https://github.com/BME-VIK-MI-25/public-files/blob/main/logo2.png">
      <p style="font-size:24">Ez a projekt azért készült, hogy együtt fejlesszünk a 2025-ben induló BME-VIK Mérnökinformatikus szak Discord szervere számára egy használható hitelesítő Discord Bot-ot.  Erre azért volt szükségünk, hogy valamilyen módon megkülönböztessük a nem szaktársainkat a szaktársainktól, hogy a releváns csatornákat csak azok az emberek láthassák akikre az ténylegesen vonatkozik.<p>
    </tr>
  </table>

## A projekt alapelvei:
1. A kódbázis legyen rendezett, minden kiegészítés a `modules` mappába helyezendő.
2. A Bot alapvető célja az a szerveren való hitelesítés megvalósítása, ezen felül pedig néhány moderációval kapcsolatos funkció létrehozása.
3. A hozzájárulásokat minden esetben külön ágon kell megvalósítani amit majd később egy `pull request`-tel kell jóváhagyásra bocsátani.

## Hogyan futtasd a botot?

Először telepítsd a szükséges modulokat, majd generáld le a használt prisma adatbázist. Ezt egy egyszerű futtatószkripttel megteheted:
```
python -m pip install -r requirements.txt
prisma generate
prisma db push
```
