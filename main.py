import sys
from pathlib import Path

class Kartya():
    def __init__(self, nev, sebzes, eletero, tipus, sorszam):
        self.nev = nev
        self.sebzes = int(sebzes)
        self.eletero = int(eletero)
        self.tipus = tipus
        self.sorszam = int(sorszam)
    def szep_kiiras(self):
        return f"{self.sorszam}. {self.nev}: Sebzés: {self.sebzes}, Életerő: {self.eletero}, Típus: {self.tipus}"

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
    def szep_kiiras(self):
        return f"Vezér: {self.nev}: Sebzés: {self.sebzes}, Életerő: {self.eletero}, Típus: {self.tipus}"

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
    def szep_kiiras(self):
        return f"Típusa: {self.tipusa}, {self.elnevezes}, Kártya: {self.nev}, Módosít: {self.mitad}, Sebzés: {self.sebzes}, Életerő: {self.eletero}, Típus: {self.tipus}"

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
    def szep_kiiras(self):
        return f"Vezér Kazamata típusa: {self.tipusa}: {self.elnevezes}, Vezér: {self.nev}, Módosít: {self.mitad}, Sebzés: {self.sebzes}, Életerő: {self.eletero}, Típus: {self.tipus}"

class Gyujtemeny():
    def __init__(self):
        self.kartyak = []
    def hozzaad(self, kartya):
        self.kartyak.append(kartya)
    def __str__(self):
        if not self.kartyak:
            return "(üres)"
        return ", ".join(k.nev for k in self.kartyak)

# --------------------------------------------------------------------
def sebzes_szamitas(tamado_tipus, vedo_tipus, tamado_sebzes):
    # alapértelmezett sebzés
    sebzes = tamado_sebzes

    # "erős" kapcsolatok – duplázás
    if (tamado_tipus == "levego" and vedo_tipus == "fold") \
       or (tamado_tipus == "fold" and vedo_tipus == "viz") \
       or (tamado_tipus == "viz" and vedo_tipus == "tuz") \
       or (tamado_tipus == "tuz" and vedo_tipus == "levego"):
        sebzes = tamado_sebzes * 2

    # "gyenge" kapcsolatok – felezés (lefelé kerekítve)
    elif (tamado_tipus == "levego" and vedo_tipus == "tuz") \
        or (tamado_tipus == "tuz" and vedo_tipus == "viz") \
        or (tamado_tipus == "viz" and vedo_tipus == "fold") \
        or (tamado_tipus == "fold" and vedo_tipus == "levego"):
        sebzes = tamado_sebzes // 2  # lefelé kerekítés

    # azonos vagy semleges típus – változatlan sebzés
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
                kor_szamlalo+=1
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
    # ...
    pass

def run_automated_test(test_dir_path):
    test_dir = Path(test_dir_path)
    in_file = test_dir / "in.txt"
    if not in_file.exists():
        print(f"Hiba: nem található az input fájl: {in_file}")
        return
    sorszam = 1
    sima_kartyak = []
    vezer_kartyak = []
    kazamatak = []
    gyujtemeny_kartyai = Gyujtemeny()
    pakli = []

    with in_file.open("r", encoding="utf-8") as in_fajl:
        for sor in in_fajl:
            adat = sor.strip().split(";")
            if not adat or adat[0] == "":
                continue
            if adat[0] == "uj kartya":
                uj_s_kartya = Kartya(adat[1], adat[2], adat[3], adat[4], sorszam)
                sorszam += 1
                sima_kartyak.append(uj_s_kartya)
            elif adat[0] == "uj vezer":
                alap_kartya = next((k for k in sima_kartyak if k.nev == adat[2]), None)
                if alap_kartya:
                    dupl = adat[3] if len(adat) > 3 else None
                    uj_vezer = Vezer(adat[1], alap_kartya, dupl)
                    vezer_kartyak.append(uj_vezer)
                else:
                    print("Nincs ilyen alap kártya a vezérhez!")
            elif adat[0] == "uj kazamata":
                tipusa = adat[1]
                elnevezes = adat[2]
                ellenseg = [n.strip() for n in adat[3].split(",")]
                modosit = None
                vezer_nev = None
                if len(adat) > 5:
                    modosit = adat[5]
                    vezer_nev = adat[4]
                else:
                    if len(adat) > 4 and adat[4] in ("sebzes", "eletero"):
                        modosit = adat[4]
                    elif len(adat) > 4:
                        vezer_nev = adat[4]
                for nev in ellenseg:
                    alap_kartya = next((k for k in sima_kartyak if k.nev == nev), None)
                    if alap_kartya:
                        uj_k = Kazamata(tipusa, elnevezes, alap_kartya, modosit)
                        kazamatak.append(uj_k)
                    else:
                        print(f"Nincs ilyen ellenség-kártya a kazamatához")
                if vezer_nev:
                    alap_vezer = next((v for v in vezer_kartyak if v.nev == vezer_nev), None)
                    if alap_vezer:
                        v_kaz = VezerKazamata(elnevezes, alap_vezer, tipusa, modosit)
                        kazamatak.append(v_kaz)
                    else:
                        print(f"Nincs ilyen vezér a kazamata számára")
            elif adat[0] == "felvetel gyujtemenybe":
                kartya = next((k for k in sima_kartyak if k.nev == adat[1]), None)
                if kartya:
                    gyujtemeny_kartyai.hozzaad(kartya)
                else:
                    print(f"Nincs ilyen kártya a gyűjteményhez")
            elif adat[0] == "uj pakli":
                pakli_n = [n.strip() for n in adat[1].split(",")]
                for nev in pakli_n:
                    kartya_p = next((k for k in sima_kartyak if k.nev == nev), None)
                    if kartya_p:
                        if kartya_p not in pakli:
                            pakli.append(kartya_p)
                    else:
                        print(f"Nincs ilyen kártya a paklihoz")
            elif adat[0] == "harc":
                k_nev = adat[1]
                file_nev = test_dir / adat[2]
                harc(pakli, kazamatak, file_nev)
        

if __name__ == "__main__":
    main()