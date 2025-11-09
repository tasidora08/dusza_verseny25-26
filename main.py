import sys
from pathlib import Path
import copy
import os
import shutil
import math
import argparse
from typing import List, Optional, Tuple, Set, Dict

class Kartya():
    def __init__(self, nev, sebzes, eletero, tipus, sorszam):
        self.nev = nev
        self.sebzes = int(sebzes)
        self.eletero = int(eletero)
        self.tipus = tipus
        self.sorszam = int(sorszam)
    

class Vezer(Kartya):
    def __init__(self, uj_nev, alap_kartya, duplazas=None):
        super().__init__(
            alap_kartya.nev,
            alap_kartya.sebzes,
            alap_kartya.eletero,
            alap_kartya.tipus,
            alap_kartya.sorszam
        )
        self.nev = uj_nev 
        
        if duplazas == "sebzes":
            self.sebzes *= 2
        elif duplazas == "eletero":
            self.eletero *= 2
            


class Kazamata(Kartya):
    def __init__(self, tipusa, elnevezes, alap_kartya, mitad=None):
        super().__init__(
            alap_kartya.nev,
            alap_kartya.sebzes,
            alap_kartya.eletero,
            alap_kartya.tipus,
            alap_kartya.sorszam
        )
        self.tipusa = tipusa
        self.elnevezes = elnevezes
        self.mitad = mitad


class VezerKazamata(Vezer):
    def __init__(self, elnevezes, alap_vezer, tipusa, mitad=None):
        super().__init__(
            alap_vezer.nev,
            alap_vezer,
            None 
        )
        self.elnevezes = elnevezes
        self.tipusa = tipusa
        self.mitad = mitad
        
        if self.mitad == "sebzes":
            self.sebzes *= 2
        elif self.mitad == "eletero":
            self.eletero *= 2
        


# --------------------------------------------------------------------

def sebzes_szamitas(tamado_tipus, vedo_tipus, tamado_sebzes):
    sebzes = tamado_sebzes

    if (tamado_tipus == "levego" and vedo_tipus == "fold") \
       or (tamado_tipus == "fold" and vedo_tipus == "viz") \
       or (tamado_tipus == "viz" and vedo_tipus == "tuz") \
       or (tamado_tipus == "tuz" and vedo_tipus == "levego"):
        sebzes = tamado_sebzes * 2

    elif (tamado_tipus == "levego" and vedo_tipus == "tuz") \
       or (tamado_tipus == "tuz" and vedo_tipus == "viz") \
       or (tamado_tipus == "viz" and vedo_tipus == "fold") \
       or (tamado_tipus == "fold" and vedo_tipus == "levego"):
        sebzes = tamado_sebzes // 2  

    else:
        sebzes = tamado_sebzes

    return sebzes

def harc(pakli,kazamatak,file_helye):
    file_helye = Path(file_helye)
    file_helye.parent.mkdir(parents=True, exist_ok=True)
    kor_szamlalo = 0
    if not pakli:
        raise ValueError("A pakli üres, nincs mivel harcolni.")
    if not kazamatak:
        raise ValueError("Nincsenek kazamaták (ellenfél hiányzik).")
    with file_helye.open("w", encoding="utf-8") as f:
        akt_jatekos = pakli[0]
        akt_kazamata = kazamatak[0]

        pakli = [k for k in pakli]
        kazamatak = [k for k in kazamatak]
        f.write(f"harc kezdődik: {akt_kazamata.nev}\n") 
        while pakli and kazamatak:
            kor_szamlalo += 1
            akcio_j= "kijatszik"
            akcio_k="kijatszik"
            while pakli and kazamatak:
                f.write(f"{kor_szamlalo}.kor;kazamata;{akcio_k};{akt_kazamata.nev};{akt_kazamata.sebzes};{akt_kazamata.eletero};{akt_kazamata.tipus}\n")
                f.write(f"{kor_szamlalo}.kor;jatekos;{akcio_j};{akt_jatekos.nev};{akt_jatekos.sebzes};{akt_jatekos.eletero};{akt_jatekos.tipus}\n")
                akcio_j="tamad"
                akcio_k="tamad"
                akt_jatekos.eletero -= sebzes_szamitas(akt_kazamata.tipus,akt_jatekos.tipus,akt_kazamata.sebzes) 
                
                akt_kazamata.eletero -= sebzes_szamitas(akt_jatekos.tipus,akt_kazamata.tipus,akt_jatekos.sebzes)
                if akt_kazamata.eletero <= 0:
                    kazamatak.pop(0)
                    akcio_k="kijatszik"
                    
                    if len(kazamatak) == 0:
                        f.write(f"jatekos nyert;{akt_jatekos.eletero};{akt_jatekos.nev}")
                        break
                    else: 
                        pass
                if akt_jatekos.eletero <=0:             
                    pakli.pop(0)
                    akcio_j="kijatszik"
                                    
                    if len(pakli) == 0:
                        f.write(f"jatekos vesztett")
                        break
                    else:
                        continue
# -----------------------------------------------------------------------

def main():
    if len(sys.argv) == 1:
        print("Használat: python script.py [--ui | <test_dir_path>]")
        sys.exit(1)

    if sys.argv[1] == "--ui":
        run_ui()
    else:
        run_automated_test(sys.argv[1])


def run_ui():
    class Stilus:
        SZIN_VISSZA = "\033[0m"
        SZIN_KERET = "\033[38;5;75m"
        SZIN_SZOVEG = "\033[97m"
        SZIN_HIBA = "\033[91m"
        SZIN_FIGYELMEZTETES = "\033[93m"

        BAL_FELSO = "╔"
        JOBB_FELSO = "╗"
        BAL_ALSO = "╚"
        JOBB_ALSO = "╝"
        VIZSZINTES = "═"
        FUGGOLEGES = "║"


    class Panel:
        def __init__(self, sorok: List[str], belso_hely: int = 2):
            self.sorok = sorok
            self.belso_hely = belso_hely
            self.panel_sorok: List[str] = []

        def keszit(self):
            max_hossz = max((len(sor) for sor in self.sorok), default=0)
            belso_szelesseg = max_hossz + self.belso_hely * 2

            f = Stilus
            p: List[str] = []
            p.append(f.BAL_FELSO + f.VIZSZINTES *
                    (belso_szelesseg + 2) + f.JOBB_FELSO)
            p.append(f.FUGGOLEGES + " " * (belso_szelesseg + 2) + f.FUGGOLEGES)

            for sor in self.sorok:
                tartalom = " " * self.belso_hely + \
                    sor.ljust(max_hossz) + " " * self.belso_hely
                p.append(f.FUGGOLEGES + " " + tartalom + " " + f.FUGGOLEGES)

            p.append(f.FUGGOLEGES + " " * (belso_szelesseg + 2) + f.FUGGOLEGES)
            p.append(f.BAL_ALSO + f.VIZSZINTES *
                    (belso_szelesseg + 2) + f.JOBB_ALSO)

            self.panel_sorok = p
            return p


    class Kepernyo:
        @staticmethod
        def torol():

            os.system("cls" if os.name == "nt" else "clear")

        @staticmethod
        def kozepre_ir(panel_sorok: List[str]):

            try:
                szelesseg, magassag = shutil.get_terminal_size(fallback=(80, 24))
            except Exception:
                szelesseg, magassag = (80, 24)
            panel_magassag = len(panel_sorok)
            felso_margo = max((magassag - panel_magassag) // 2, 0)

            Kepernyo.torol()
            for _ in range(felso_margo):
                print()

            for sor in panel_sorok:

                behuzas = max((szelesseg - len(sor)) // 2, 0)

                if sor.startswith(Stilus.FUGGOLEGES) or sor[0] in (Stilus.BAL_FELSO, Stilus.BAL_ALSO):
                    print(" " * behuzas + Stilus.SZIN_KERET +
                        sor + Stilus.SZIN_VISSZA)
                else:
                    print(" " * behuzas + Stilus.SZIN_SZOVEG +
                        sor + Stilus.SZIN_VISSZA)

        @staticmethod
        def kozepre_input(szoveg: str) -> str:
            try:
                szelesseg = shutil.get_terminal_size(fallback=(80, 24)).columns
            except Exception:
                szelesseg = 80
            behuzas = " " * max(((szelesseg - len(szoveg)) // 2), 0)
            try:
                return input(f"{behuzas}{Stilus.SZIN_SZOVEG}{szoveg}{Stilus.SZIN_VISSZA}")
            except KeyboardInterrupt:
                print("\nKilépés... (CTRL-C) ")
                raise
            except Exception:

                return ""


    class Kartya:
        MAX_NEV_HOSSZ = 16

        def __init__(self, nev: str, sebzes: int, eletero: int, tipus: str, vezer: bool = False):
            self.nev = nev
            self.sebzes = sebzes
            self.eletero = eletero
            self.tipus = tipus
            self.vezer = vezer

        def klon_harcra(self) -> 'KartyaHarci':

            return KartyaHarci(self.nev, self.sebzes, self.eletero, self.tipus, self.vezer)

        @classmethod
        def from_line(cls, line: str) -> Tuple[Optional['Kartya'], Optional[str]]:
            """
            Létrehoz egy Kartya példányt egy TXT sorból.
            Formátum: NÉV|SEBZÉS|ÉLETERŐ|TÍPUS|VEZÉR(True/False)
            Visszatér: (Kartya objektum vagy None, Érvénytelen név vagy None)
            """
            try:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) < 4:

                    return None, None

                nev = parts[0]

                if len(nev) > cls.MAX_NEV_HOSSZ:

                    return None, nev

                sebzes = int(parts[1])
                eletero = int(parts[2])
                tipus = parts[3].lower()
                vezer = False
                if len(parts) >= 5 and parts[4].lower() == "true":
                    vezer = True

                if not nev or sebzes < 0 or eletero < 0 or tipus.lower().strip() not in Harc.STRONG_AGAINST.keys():
                    return None, None

                return cls(nev, sebzes, eletero, tipus, vezer), None
            except Exception:
                return None, None


    class KartyaHarci(Kartya):
        def __init__(self, nev: str, sebzes: int, eletero: int, tipus: str, vezer: bool = False):
            super().__init__(nev, sebzes, eletero, tipus, vezer)
            self.current_hp = eletero


    class Kazamata:
        MAX_NEV_HOSSZ = 16

        def __init__(self, tipus: str, nev: str, ellenseg_nevek: List[str], vezer_nev: Optional[str], jutalom: Optional[str], uj_kartya: Optional[str] = None):
            self.tipus = tipus
            self.nev = nev
            self.ellenseg_nevek = ellenseg_nevek
            self.vezer_nev = vezer_nev
            self.jutalom = jutalom
            self.uj_kartya = uj_kartya

        @classmethod
        def from_line(cls, line: str) -> Tuple[Optional['Kazamata'], Optional[str]]:
            """
            Létrehoz egy Kazamata példányt egy TXT sorból.
            Formátum: NÉV|TÍPUS|ELLENSÉGEK_VESSZŐVEL|VEZÉRNÉV_VAGY_ÜRES|JUTALOM(...)
            Visszatér: (Kazamata objektum vagy None, Érvénytelen név vagy None)
            """
            try:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) < 5:
                    return None, None

                nev = parts[0]

                if len(nev) > cls.MAX_NEV_HOSSZ:

                    return None, nev

                tipus = parts[1].lower()
                ellenseg_nevek = [n.strip()
                                for n in parts[2].split(",") if n.strip()]

                vezer_nev = parts[3] if parts[3] else None
                jutalom_raw = parts[4].lower()

                jutalom = None
                uj_kartya = None

                if tipus == "nagy":
                    uj_kartya = "uj_kartya"
                elif jutalom_raw in ["sebzes", "eletero"]:
                    jutalom = jutalom_raw

                if not nev or not tipus or not ellenseg_nevek:
                    return None, None

                return cls(tipus, nev, ellenseg_nevek, vezer_nev, jutalom, uj_kartya), None
            except Exception:
                return None, None


    class Harc:

        STRONG_AGAINST = {
            "levego": "fold",
            "fold": "viz",
            "viz": "tuz",
            "tuz": "levego"
        }

        def __init__(self, jatekos_pakli: List[Kartya], jatekos_gyujtemeny: List[Kartya], vilag: List[Kartya], kazamata: Kazamata):

            self.jatekos_gyujtemeny_nevek = {k.nev for k in jatekos_gyujtemeny}
            self.vilag = vilag

            self.jatekos_pakli_harci: List[KartyaHarci] = [
                k.klon_harcra() for k in jatekos_pakli]

            self.kazamata_harci: List[KartyaHarci] = []

            for nev in kazamata.ellenseg_nevek:
                adat = next((k for k in vilag if k.nev == nev), None)
                if adat:
                    self.kazamata_harci.append(adat.klon_harcra())
                else:

                    self.kazamata_harci.append(KartyaHarci(nev, 2, 2, "fold"))

            if kazamata.vezer_nev:
                vez = next((k for k in vilag if k.nev == kazamata.vezer_nev), None)
                if vez:
                    self.kazamata_harci.append(vez.klon_harcra())
                else:
                    self.kazamata_harci.append(KartyaHarci(
                        kazamata.vezer_nev, 4, 4, "fold", vezer=True))
            self.kazamata = kazamata
            self.log: List[str] = []

        @staticmethod
        def tipus_norma(t: str) -> str:
            return t.lower().strip()

        def módosított_sebzes(self, attacker: KartyaHarci, defender: KartyaHarci) -> int:
            a = attacker.sebzes
            at = attacker.tipus
            dt = defender.tipus
            at = self.tipus_norma(at)
            dt = self.tipus_norma(dt)

            is_strong = (Harc.STRONG_AGAINST.get(at) == dt)
            is_weak = (Harc.STRONG_AGAINST.get(dt) == at)

            if is_strong:
                return a * 2
            elif is_weak:

                return a // 2
            else:
                return a

        def futtat(self) -> Tuple[List[str], str, Optional[Tuple[str, str]]]:
            """
            A harcmenet logikája.
            """
            self.log.append(f"harc kezdodik;{self.kazamata.nev}")

            lep = 1
            idx_j = 0
            idx_k = 0
            jatekos = self.jatekos_pakli_harci
            kaz = self.kazamata_harci

            if not jatekos:
                self.log.append("jatekos vesztett")
                return self.log, "vesztett", None
            if not kaz:
                self.log.append("jatekos nyert")
                return self.log, "nyert", None

            while True:

                if idx_j >= len(jatekos):
                    self.log.append("jatekos vesztett")
                    return self.log, "vesztett", None

                if idx_k >= len(kaz):
                    jutalom_info = None

                    last_player_card = None
                    for pj in range(min(idx_j, len(jatekos)-1), -1, -1):
                        if jatekos[pj].current_hp > 0:
                            last_player_card = jatekos[pj].nev
                            break
                    if not last_player_card and jatekos:
                        last_player_card = jatekos[min(idx_j, len(jatekos)-1)].nev

                    if self.kazamata.tipus in ["egyszeru", "kis"]:
                        if last_player_card and self.kazamata.jutalom:
                            self.log.append(
                                f"jatekos nyert;{self.kazamata.jutalom};{last_player_card}")
                            jutalom_info = (self.kazamata.jutalom,
                                            last_player_card)
                        else:
                            self.log.append("jatekos nyert")
                            jutalom_info = None

                    elif self.kazamata.tipus == "nagy":

                        newcard = None
                        for worldcard in self.vilag:
                            if not worldcard.vezer and worldcard.nev not in self.jatekos_gyujtemeny_nevek:
                                newcard = worldcard.nev
                                break
                        if newcard:
                            self.log.append(f"jatekos nyert;uj_kartya;{newcard}")
                            jutalom_info = ("uj_kartya", newcard)
                        else:

                            self.log.append("jatekos nyert;uj_kartya;Nincs")
                            jutalom_info = ("uj_kartya", "Nincs")

                    return self.log, "nyert", jutalom_info

                while idx_k < len(kaz) and kaz[idx_k].current_hp <= 0:
                    idx_k += 1
                if idx_k >= len(kaz):
                    continue

                kaz_current = kaz[idx_k]

                while idx_j < len(jatekos) and jatekos[idx_j].current_hp <= 0:
                    idx_j += 1
                if idx_j >= len(jatekos):
                    self.log.append("jatekos vesztett")
                    return self.log, "vesztett", None

                jatekos_current = jatekos[idx_j]

                if kaz_current.current_hp == kaz_current.eletero:
                    self.log.append(
                        f"{lep}.kor;kazamata;kijatszik;{kaz_current.nev};{kaz_current.sebzes};{kaz_current.eletero};{kaz_current.tipus}")
                    lep += 1

                if jatekos_current.current_hp == jatekos_current.eletero:
                    self.log.append(
                        f"{lep}.kor;jatekos;kijatszik;{jatekos_current.nev};{jatekos_current.sebzes};{jatekos_current.eletero};{jatekos_current.tipus}")
                    lep += 1

                dmg_k_to_j = self.módosított_sebzes(kaz_current, jatekos_current)
                jatekos_current.current_hp -= dmg_k_to_j
                if jatekos_current.current_hp <= 0:
                    jatekos_current.current_hp = 0
                self.log.append(
                    f"{lep}.kor;kazamata;tamad;{kaz_current.nev};{dmg_k_to_j};{jatekos_current.nev};{jatekos_current.current_hp}")
                lep += 1

                if jatekos_current.current_hp <= 0:
                    idx_j += 1
                    if idx_j >= len(jatekos):
                        self.log.append("jatekos vesztett")
                        return self.log, "vesztett", None
                    continue

                if kaz_current.current_hp > 0:
                    dmg_j_to_k = self.módosított_sebzes(
                        jatekos_current, kaz_current)
                    kaz_current.current_hp -= dmg_j_to_k
                    if kaz_current.current_hp <= 0:
                        kaz_current.current_hp = 0
                    self.log.append(
                        f"{lep}.kor;jatekos;tamad;{jatekos_current.nev};{dmg_j_to_k};{kaz_current.nev};{kaz_current.current_hp}")
                    lep += 1

                    if kaz_current.current_hp <= 0:
                        idx_k += 1
                        continue

            


    class KazamataValaszto:
        def __init__(self, kazamata_file: str):
            self.kazamata_file = kazamata_file
            self.kazamatak: List[Kazamata] = []

        def _read_kazamatak_from_file(self) -> Tuple[List[Kazamata], List[str]]:
            """
            Beolvassa a Kazamatákat a megadott TXT fájlból,
            visszaadja az érvénytelen kazamataneveket is.
            """
            kazamatak: List[Kazamata] = []
            invalid_names: List[str] = []
            if not self.kazamata_file or not os.path.exists(self.kazamata_file):
                return [], []

            try:
                with open(self.kazamata_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        kazamata, invalid_name = Kazamata.from_line(line)
                        if kazamata:
                            kazamatak.append(kazamata)
                        elif invalid_name:
                            invalid_names.append(invalid_name)
            except Exception:

                return [], []

            self.kazamatak = kazamatak
            return kazamatak, invalid_names

        def megjelenit(self):
            if not self.kazamatak:
                Kepernyo.torol()
                print("Nincs beolvasott kazamata. Kérjük, ellenőrizze a fájlt.")
                input("ENTER → vissza")
                return None

            f = Stilus
            belso_szelesseg = 65
            sorok = []
            sorok.append(f"╔{'═' * belso_szelesseg}╗")
            sorok.append(f"║{'KAZAMATÁK VÁLASZTÁSA'.center(belso_szelesseg)}║")
            sorok.append(f"║{'':^{belso_szelesseg}}║")

            MAX_NEV_KIJELZES = 14

            for i, k in enumerate(self.kazamatak, start=1):
                sorok.append(f"║ {'═' * (belso_szelesseg - 2)} ║")
                sorok.append(
                    f"║ [ {i} ] {k.nev:<{MAX_NEV_KIJELZES}}  {'_' * (belso_szelesseg - 7 - MAX_NEV_KIJELZES)} ║")

                ellensegek = ", ".join(k.ellenseg_nevek)

                sorok.append(
                    f"║   Típus: {k.tipus:<10} Ellenségek: {ellensegek:<{belso_szelesseg - 33}}║")

                vezer_info = f"  Vezér: {k.vezer_nev}" if k.vezer_nev else "  Vezér: Nincs"

                sorok.append(f"║{vezer_info:<{belso_szelesseg}}║")

                if k.tipus == "nagy":
                    jutalom_nev = "Új kártya a világból"
                elif k.tipus == "egyszeru" or k.tipus == "kis":
                    if k.jutalom == "sebzes":
                        jutalom_nev = "+1 Sebzés"
                    elif k.jutalom == "eletero":
                        jutalom_nev = "+2 Életerő"
                    else:
                        jutalom_nev = "Nincs meghatározva"
                else:
                    jutalom_nev = "Nincs meghatározva"

                jutalom_sor = f"  Nyeremény: {jutalom_nev}"

                sorok.append(f"║{jutalom_sor:<{belso_szelesseg}}║")

            sorok.append(f"╚{'═' * belso_szelesseg}╝")

            max_hossz = max(len(s) for s in sorok)
            szelesseg = shutil.get_terminal_size(fallback=(100, 24)).columns
            behuzas = max((szelesseg - max_hossz) // 2, 0)

            Kepernyo.torol()
            for s in sorok:
                print(" " * behuzas + f.SZIN_KERET + s + f.SZIN_VISSZA)

            print()
            try:
                valasztas = Kepernyo.kozepre_input(
                    "Válaszd ki a kazamata számát: [ _ ] ")
            except KeyboardInterrupt:
                return None
            except Exception:
                return None

            try:
                valasztas = int(valasztas)
            except ValueError:
                valasztas = -1
            if 1 <= valasztas <= len(self.kazamatak):
                return self.kazamatak[valasztas - 1]
            return None


    class JatekközpontUI:
        def __init__(self, card_file: str, kazamata_file: str, vilag: List[Kartya]):
            self.card_file = card_file
            self.kazamata_file = kazamata_file
            self.vilag: List[Kartya] = vilag

            kezdo_nevek = ["Arin", "Liora", "Nerun", "Selia"]
            self.kartyak: List[Kartya] = []
            for n in kezdo_nevek:
                k = next((v for v in self.vilag if v.nev == n), None)
                if k and not next((c for c in self.kartyak if c.nev == n), None):
                    self.kartyak.append(
                        Kartya(k.nev, k.sebzes, k.eletero, k.tipus, k.vezer))

            self.pakli: List[Kartya] = []

            self.menu_sorok_template = [
                "D   A   M   A   R   E   E   N",
                "",
                f"Kártya fájl: {self.card_file}",
                f"Kazamata fájl: {self.kazamata_file}",
                "Kártyák: {sima_lapok}/{max_sima} ",
                "Pakli: Még nincs összeállítva!",
                "",
                "Válassz akciót:",
                "═════════════════════════════════════",
                "[1]   Pakli Összeállítása/Módosítása",
                "[2]   Harc Indítása (Kazamataválasztás)",
                "[3]   Gyűjtemény Megtekintése",
                "[4]   Világ Megtekintése",
                "[5]   Kazamaták Megtekintése",
                "[0]   Vissza a Főmenübe"
            ]

        def _read_cards_from_file(self) -> Tuple[List[Kartya], List[str]]:
            """
            Beolvassa a Világ kártyáit. EZT MÁR A DAMAREENMENU FOGJA FUTTATNI, 
            ez a metódus itt csak a régi struktúrát mutatja.
            """
            cards: List[Kartya] = []
            invalid_names: List[str] = []
            if not self.card_file or not os.path.exists(self.card_file):
                return [], []

            try:
                with open(self.card_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        card, invalid_name = Kartya.from_line(line)
                        if card:
                            cards.append(card)
                        elif invalid_name:
                            invalid_names.append(invalid_name)
            except Exception:
                return [], []

            return cards, invalid_names

        def _build_menu(self) -> List[str]:
            sorok = list(self.menu_sorok_template)
            sima = len([k for k in self.kartyak if not k.vezer])
            vezer = len([k for k in self.kartyak if k.vezer])
            max_sima = len([k for k in self.vilag if not k.vezer])

            sorok[4] = sorok[4].format(
                sima_lapok=sima, max_sima=max_sima, vezer_lapok=vezer)
            sorok[5] = f"Pakli: {len(self.pakli)} kártya" if self.pakli else "Pakli: Még nincs összeállítva!"
            return sorok

        def megjelenit(self):
            panel = Panel(self._build_menu(), belso_hely=3)
            panel.keszit()
            Kepernyo.kozepre_ir(panel.panel_sorok)

        def gyujtemeny_megjelenit(self):
            sorok = ["A TE KÁRTYÁID:", ""]
            if not self.kartyak:
                sorok.append("A gyűjteményed üres.")
            else:
                for k in self.kartyak:
                    vez = " (Vezér)" if k.vezer else ""
                    sorok.append(
                        f"{k.nev:<16} | Sebzés: {k.sebzes:<3} | Életerő: {k.eletero:<3} | Típus: {k.tipus}{vez}")
            panel = Panel(sorok, belso_hely=3)
            panel.keszit()
            Kepernyo.kozepre_ir(panel.panel_sorok)
            input("\nENTER → vissza")

        def vilag_megjelenit(self):
            sorok = ["A VILÁG KÁRTYÁI:", ""]
            if not self.vilag:
                sorok.append("Nincs kártya beolvasva a fájlból.")
            else:
                for k in self.vilag:
                    vez = " (Vezér)" if k.vezer else ""
                    sorok.append(
                        f"{k.nev:<16} | Sebzés: {k.sebzes:<3} | Életerő: {k.eletero:<3} | Típus: {k.tipus}{vez}")
            panel = Panel(sorok, belso_hely=3)
            panel.keszit()
            Kepernyo.kozepre_ir(panel.panel_sorok)
            input("\nENTER → vissza")

        def kazamatak_megjelenit(self):
            kv = KazamataValaszto(self.kazamata_file)
            kv._read_kazamatak_from_file()

            if not kv.kazamatak:
                Kepernyo.torol()
                print(
                    f"HIBA: Nem sikerült beolvasni kazamatákat a(z) '{self.kazamata_file}' fájlból.")
                input("ENTER → vissza")
                return

            sorok = ["A VILÁG KAZAMATÁI:", ""]
            for k in kv.kazamatak:
                sorok.append(f"Név: {k.nev}")
                sorok.append(f"Típus: {k.tipus}")
                sorok.append(f"Ellenségek: {', '.join(k.ellenseg_nevek)}")
                if k.vezer_nev:
                    sorok.append(f"Vezér: {k.vezer_nev}")
                if k.jutalom == "sebzes":
                    sorok.append(f"Jutalom: +1 Sebzés")
                elif k.jutalom == "eletero":
                    sorok.append(f"Jutalom: +2 Életerő")
                elif k.tipus == "nagy":
                    sorok.append(f"Jutalom: Új sima kártya")
                sorok.append("─" * 50)
            panel = Panel(sorok, belso_hely=3)
            panel.keszit()
            Kepernyo.kozepre_ir(panel.panel_sorok)
            input("\nENTER → vissza")

        def pakli_megjelenit(self):
            sorok = ["AKTUÁLIS PAKLID:", ""]
            if self.pakli:
                for k in self.pakli:
                    sorok.append(
                        f"{k.nev:<16} | Sebzés: {k.sebzes:<3} | Életerő: {k.eletero:<3} | Típus: {k.tipus}")
            else:
                sorok.append("Még nincs paklid.")
            panel = Panel(sorok, belso_hely=3)
            panel.keszit()
            Kepernyo.kozepre_ir(panel.panel_sorok)

            valasz = Kepernyo.kozepre_input(
                "Szeretnél új paklit összeállítani? (i/n): ").lower()
            if valasz == "i":
                self.osszeallit_paklit()

        def osszeallit_paklit(self):
            if not self.kartyak:
                print("Nincs kártyád a gyűjteményben, nem tudsz paklit összeállítani!")
                input("ENTER → vissza")
                return

            felso_limit = math.ceil(len(self.kartyak) / 2)
            Kepernyo.torol()
            print(f"Maximum {felso_limit} kártyát választhatsz a gyűjteményedből.")
            print("\nGyűjteményed kártyái:")
            for i, k in enumerate(self.kartyak, start=1):
                print(
                    f"[{i}] {k.nev:<16} | Sebzés: {k.sebzes} | Életerő: {k.eletero} | Típus: {k.tipus}")

            try:
                szamok = Kepernyo.kozepre_input(
                    "\nAdd meg a kiválasztott kártyák sorszámait (vesszővel elválasztva): ")
            except KeyboardInterrupt:
                return

            uj_pakli: List[Kartya] = []
            try:
                valasztott = [int(x.strip())
                            for x in szamok.split(",") if x.strip()]

                for v in valasztott[:felso_limit]:
                    if 1 <= v <= len(self.kartyak):
                        uj_pakli.append(self.kartyak[v - 1])

                if len(uj_pakli) > 0:
                    self.pakli = uj_pakli
                    print(
                        f"A paklid sikeresen összeállítva ({len(self.pakli)} kártya).")
                else:
                    print("Nem sikerült érvényes paklit összeállítani.")

            except ValueError:
                print("Érvénytelen bemenet. A pakli nincs módosítva.")

            input("\nENTER → vissza")

        def harc_megjelenit(self, kazamata: Kazamata):
            if not self.pakli:
                print("Nincs összeállított paklid! Előbb állíts össze paklit.")
                input("ENTER → vissza")
                return

            if kazamata.tipus == "nagy":
                sima_vilag_kartyak = {k.nev for k in self.vilag if not k.vezer}
                sima_gyujtemeny_kartyak = {
                    k.nev for k in self.kartyak if not k.vezer}

                if sima_vilag_kartyak.issubset(sima_gyujtemeny_kartyak):
                    print(
                        "Nem indítható Nagy kazamata harc, mert már minden sima kártya a gyűjteményedben van! (Nincs mit nyerni.)")
                    input("ENTER → vissza")
                    return

            harc = Harc(self.pakli, self.kartyak, self.vilag, kazamata)
            log, eredmeny, jutalom = harc.futtat()

            panel = Panel(
                ["HARC NAPLÓ:", f"Eredmény: {eredmeny.upper()}"] + [""] + log, belso_hely=1)
            panel.keszit()
            Kepernyo.kozepre_ir(panel.panel_sorok)

            if eredmeny == "nyert" and jutalom:
                typ, target = jutalom

                if typ == "eletero":
                    kar = next((k for k in self.kartyak if k.nev == target), None)
                    if kar:
                        kar.eletero += 2
                        print(
                            f"\nGratulálunk! {kar.nev} Életereje +2 lett (Új Élet: {kar.eletero})!")
                elif typ == "sebzes":
                    kar = next((k for k in self.kartyak if k.nev == target), None)
                    if kar:
                        kar.sebzes += 1
                        print(
                            f"\nGratulálunk! {kar.nev} Sebzése +1 lett (Új Sebzés: {kar.sebzes})!")
                elif typ == "uj_kartya":
                    cardname = target
                    if cardname != "Nincs":
                        worldcard = next(
                            (k for k in self.vilag if k.nev == cardname and not k.vezer), None)

                        existing = next(
                            (k for k in self.kartyak if k.nev == cardname), None)

                        if worldcard and not existing:
                            self.kartyak.append(
                                Kartya(worldcard.nev, worldcard.sebzes, worldcard.eletero, worldcard.tipus))
                            print(
                                f"\nGratulálunk! Megszerezted az új kártyát: {cardname}!")
                        else:
                            print(
                                "\nA harcot megnyerted, de valami hiba történt a jutalom kártya hozzáadásakor.")
                    else:
                        print(
                            "\nA harcot megnyerted, de már minden sima kártya a gyűjteményedben van.")
            input("\nENTER → vissza")

        def futtat(self):
            kv = KazamataValaszto(self.kazamata_file)
            kv._read_kazamatak_from_file()

            while True:
                self.megjelenit()
                try:
                    valasztas = Kepernyo.kozepre_input("Választás: ")
                except KeyboardInterrupt:
                    print("\nKilépés a menüből (CTRL-C).")
                    return
                except Exception:
                    valasztas = -1

                try:
                    valasztas = int(valasztas)
                except ValueError:
                    valasztas = -1

                if valasztas == 0:
                    break
                elif valasztas == 1:
                    self.pakli_megjelenit()
                elif valasztas == 2:
                    kiv = kv.megjelenit()
                    if kiv:
                        self.harc_megjelenit(kiv)
                    else:
                        print("Érvénytelen kazamata választás.")
                        input("ENTER → vissza")
                elif valasztas == 3:
                    self.gyujtemeny_megjelenit()
                elif valasztas == 4:
                    self.vilag_megjelenit()
                elif valasztas == 5:
                    self.kazamatak_megjelenit()
                else:
                    print("Érvénytelen parancs!")
                    input("ENTER → folytatás")


    class DamareenMenu:

        def _read_cards_from_file(self, card_file: str) -> Tuple[List[Kartya], List[str], bool]:
            cards: List[Kartya] = []
            invalid_names: List[str] = []
            if not card_file or not os.path.exists(card_file):
                return [], [], False

            try:
                with open(card_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        card, invalid_name = Kartya.from_line(line)
                        if card:
                            cards.append(card)
                        elif invalid_name:
                            invalid_names.append(invalid_name)
            except Exception:
                return [], [], False

            return cards, invalid_names, True

        def _read_kazamatak_from_file(self, kazamata_file: str) -> Tuple[List[Kazamata], List[str], bool]:
            kazamatak: List[Kazamata] = []
            invalid_names: List[str] = []
            if not kazamata_file or not os.path.exists(kazamata_file):
                return [], [], False

            try:
                with open(kazamata_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        kazamata, invalid_name = Kazamata.from_line(line)
                        if kazamata:
                            kazamatak.append(kazamata)
                        elif invalid_name:
                            invalid_names.append(invalid_name)
            except Exception:
                return [], [], False

            return kazamatak, invalid_names, True

        def __init__(self):
            self.menu_sorok = [
                "D   A   M   A   R   E   E   N",
                "",
                "Üdvözöllek!",
                "Válaszd ki, hogyan szeretnél játszani: (konsolos UI van)",
                "",
                "[1] [*] UI mód ",
                "[0] [X] Kilépés"
            ]

        def megjelenit(self):
            panel = Panel(self.menu_sorok, belso_hely=2)
            panel.keszit()
            Kepernyo.kozepre_ir(panel.panel_sorok)

        def kilepes_megjelenitese(self):
            kilepo_sorok = [
                "D   A   M   A   R   E   E   N",
                "",
                "Kiléptél a programból. Viszlát!"
            ]
            panel = Panel(kilepo_sorok, belso_hely=2)
            panel.keszit()
            Kepernyo.kozepre_ir(panel.panel_sorok)

        def futtat(self):
            while True:
                self.megjelenit()
                try:
                    valasztas = Kepernyo.kozepre_input("Választás: ")
                except KeyboardInterrupt:
                    print("\nKilépés... (CTRL-C)")
                    return
                except Exception:
                    valasztas = -1

                try:
                    valasztas = int(valasztas)
                except ValueError:
                    valasztas = -1

                if valasztas == 0:
                    self.kilepes_megjelenitese()
                    break
                elif valasztas == 1:
                    Kepernyo.torol()
                    card_file = Kepernyo.kozepre_input(
                        "Add meg a kártyákat tartalmazó TXT fájl nevét (pl.: vilag.txt): ").strip()
                    kazamata_file = Kepernyo.kozepre_input(
                        "Add meg a kazamatákat tartalmazó TXT fájl nevét (pl.: kazamatak.txt): ").strip()

                    vilag_kartyak, invalid_card_names, card_read_success = self._read_cards_from_file(
                        card_file)

                    if not card_read_success:
                        Kepernyo.torol()
                        print(
                            f"{Stilus.SZIN_HIBA}HIBA:{Stilus.SZIN_VISSZA} Nem sikerült beolvasni a kártya fájlt ('{card_file}').")
                        input("ENTER → vissza a főmenübe")
                        continue

                    if not vilag_kartyak and not invalid_card_names:
                        Kepernyo.torol()
                        print(
                            f"{Stilus.SZIN_HIBA}HIBA:{Stilus.SZIN_VISSZA} A kártya fájl üres vagy érvénytelen adatokat tartalmazott.")
                        input("ENTER → vissza a főmenübe")
                        continue

                    _, invalid_kazamata_names, kazamata_read_success = self._read_kazamatak_from_file(
                        kazamata_file)

                    if not kazamata_read_success:
                        Kepernyo.torol()
                        print(
                            f"{Stilus.SZIN_HIBA}HIBA:{Stilus.SZIN_VISSZA} Nem sikerült beolvasni a kazamata fájlt ('{kazamata_file}').")
                        input("ENTER → vissza a főmenübe")
                        continue

                    osszes_ervenytelen_nev = invalid_card_names + invalid_kazamata_names

                    if osszes_ervenytelen_nev:
                        Kepernyo.torol()

                        figyelmezteto_sorok = [
                            f"{Stilus.SZIN_FIGYELMEZTETES}FIGYELMEZTETÉS: Néhány név túl hosszú (max. {Kartya.MAX_NEV_HOSSZ} karakter):{Stilus.SZIN_SZOVEG}",
                            ""
                        ]

                        if invalid_card_names:
                            figyelmezteto_sorok.append(f"  Kártyák ({card_file}):")
                            for nev in invalid_card_names:
                                figyelmezteto_sorok.append(f"    - {nev}")

                        if invalid_kazamata_names:
                            if invalid_card_names:
                                figyelmezteto_sorok.append("")
                            figyelmezteto_sorok.append(
                                f"  Kazamaták ({kazamata_file}):")
                            for nev in invalid_kazamata_names:
                                figyelmezteto_sorok.append(f"    - {nev}")

                        figyelmezteto_sorok.append("")
                        figyelmezteto_sorok.append(
                            f"{Stilus.SZIN_SZOVEG}A játék csak az érvényes (rövidebb) neveket fogja használni.")
                        figyelmezteto_sorok.append(
                            f"Szeretnéd így is folytatni? (i/n)")

                        panel = Panel(figyelmezteto_sorok, belso_hely=3)
                        panel.keszit()
                        Kepernyo.kozepre_ir(panel.panel_sorok)

                        valasz = Kepernyo.kozepre_input(
                            "Folytatás? (i/n): ").lower().strip()
                        if valasz != "i":
                            continue

                    jatek = JatekközpontUI(card_file, kazamata_file, vilag_kartyak)
                    jatek.futtat()

                else:
                    print("Nem értelmezhető parancs!")
                    input("ENTER → újrapróbálás")


    def main():
        parser = argparse.ArgumentParser(
            description="Damareen - konzolos UI (csak játékos mód).")
        parser.add_argument("--ui", action="store_true",
                            help="Indítás játékos (UI) módban.")
        args = parser.parse_args()

        if args.ui or True:
            menu = DamareenMenu()
            try:
                menu.futtat()
            except KeyboardInterrupt:
                print("\nKilépés... viszlát!")


    if __name__ == "__main__":
        main()

def run_automated_test(test_dir_path):
    test_dir = Path(test_dir_path)
    in_file = test_dir / "in.txt"
    out_file = test_dir / "out.txt"

    if not in_file.exists():
        print(f"Hiba: {in_file} nem található.")
        sys.exit(1)

    kazamata_vilag = []
    sorszam = 1
    sima_kartyak = []
    vezer_kartyak = []
    kazamatak = [] 
    gyujtemeny_kartyai = []
    pakli = [] 

    with open(in_file, "r", encoding="utf-8") as in_fajl:
        for sor in in_fajl:
            adat = sor.strip().split(";")
            if not adat or adat[0] == "":
                continue
                
            parancs = adat[0]
            
            if parancs == "uj kartya":
                uj_s_kartya = Kartya(adat[1], adat[2], adat[3], adat[4], sorszam)
                sorszam += 1
                sima_kartyak.append(uj_s_kartya)
            
            elif parancs == "uj vezer":
                alap_kartya = next((k for k in sima_kartyak if k.nev == adat[2]), None)
                if alap_kartya:
                    dupl = adat[3] if len(adat) > 3 else None
                    uj_vezer = Vezer(adat[1], alap_kartya, dupl)
                    vezer_kartyak.append(uj_vezer)
                else:
                    print(f"Hiba: Nincs ilyen alap kártya a vezérhez: {adat[2]}")
            
            elif parancs == "uj kazamata":
                tipusa = adat[1]
                elnevezes = adat[2]
                ellensegek = [n.strip() for n in adat[3].split(",")]
                if len(adat) == 6:
                    kiir = f"{tipusa};{elnevezes};{adat[3]};{adat[4]};{adat[5]}"
                else:
                    kiir = f"{tipusa};{elnevezes};{adat[3]};{adat[4]}"
                kazamata_vilag.append(kiir)
                modosit = None
                vezer_nev = None
                
                if len(adat) >= 5:
                    if adat[4] in ("sebzes", "eletero"):
                        modosit = adat[4]
                    else:
                        vezer_nev = adat[4]
                        
                if len(adat) == 6:
                    modosit = adat[5]
                    vezer_nev = adat[4]

                for nev in ellensegek:
                    alap_kartya = next((k for k in sima_kartyak if k.nev == nev), None)
                    if alap_kartya:
                        uj_k = Kazamata(tipusa, elnevezes, alap_kartya, modosit)
                        kazamatak.append(uj_k)
                    else:
                        print(f"Hiba: Nincs ilyen ellenség-kártya a kazamatához: {nev}")
                        
                if vezer_nev:
                    alap_vezer = next((v for v in vezer_kartyak if v.nev == vezer_nev), None)
                    if alap_vezer:
                        v_kaz = VezerKazamata(elnevezes, alap_vezer, tipusa, modosit)
                        kazamatak.append(v_kaz)
                    else:
                        print(f"Hiba: Nincs ilyen vezér a kazamata számára: {vezer_nev}")
            
            elif parancs == "felvetel gyujtemenybe":
                kartya = next((k for k in sima_kartyak if k.nev == adat[1]), None)
                if kartya:
                    gyujtemeny_kartyai.append(kartya)
                else:
                    print(f"Hiba: Nincs ilyen kártya a gyűjteményhez: {adat[1]}")
            
            elif parancs == "uj pakli":
                pakli_n = [n.strip() for n in adat[1].split(",")]
                pakli.clear() 
                for nev in pakli_n:
                    kartya_p = next((k for k in sima_kartyak if k.nev == nev), None)
                    if kartya_p:
                        pakli.append(kartya_p) 
                    else:
                        print(f"Hiba: Nincs ilyen kártya a paklihoz: {nev}")
                        
            elif parancs == "export vilag":
                out_file = test_dir / adat[1]
                with open(out_file, "w", encoding="utf-8") as file:
                    for i in sima_kartyak:
                        file.write(f"kartya;{i.nev};{i.sebzes};{i.eletero};{i.tipus}\n")
                    file.write("\n")
                    for i in vezer_kartyak:
                        file.write(f"vezer;{i.nev};{i.sebzes};{i.eletero};{i.tipus}\n")
                    file.write("\n")
                    for i in kazamata_vilag:
                        file.write(f"kazamata;{i}\n")
                    file.write("\n")
                print("A fájl ide kerül:", out_file)
            elif parancs == "export jatekos":
                out_file = test_dir / adat[1]
                with open(out_file, "w", encoding="utf-8") as file:
                    for i in gyujtemeny_kartyai:
                        file.write(f"gyujtemeny;{i.nev};{i.sebzes};{i.eletero};{i.tipus}\n")
                    file.write(f"\n")
                    for i in pakli:
                        file.write(f"pakli;{i.nev}\n")
                print("A fájl ide kerül:", out_file)
            elif parancs == "harc":
                file_nev = test_dir / adat[2]
                harc(pakli, kazamatak, file_nev, gyujtemeny_kartyai)
            
if __name__ == "__main__":
    main()
