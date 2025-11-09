import sys
from pathlib import Path
import copy

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
        """Visszaadja a vezér kártya szépen formázott adatait."""
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
        
        if self.mitad == "sebzes":
            self.sebzes *= 2
        elif self.mitad == "eletero":
            self.eletero *= 2
            
    def szep_kiiras(self):
        """Visszaadja a kazamata kártya szépen formázott adatait."""
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
        
        if self.mitad == "sebzes":
            self.sebzes *= 2
        elif self.mitad == "eletero":
            self.eletero *= 2
            
    def szep_kiiras(self):
        """Visszaadja a vezér kazamata szépen formázott adatait."""
        return f"Vezér Kazamata típusa: {self.tipusa}: {self.elnevezes}, Vezér: {self.nev}, Módosít: {self.mitad}, Sebzés: {self.sebzes}, Életerő: {self.eletero}, Típus: {self.tipus}"


# --------------------------------------------------------------------

def sebzes_szamitas(tamado_tipus, vedo_tipus, tamado_sebzes):
    """Kiszámítja a sebzést a típusok alapján (2x, 0.5x, vagy normál)."""
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

def harc(pakli, kazamata_lista, file_helye, gyujtemeny_kartyai):
    """
    Szimulálja a kártyacsatát. Létrehozza a harcra vonatkozó mély másolatokat,
    és naplózza az eredményt a megadott fájlba a feladatkiírásnak megfelelően.
    """
    
    try:
        harc_pakli = copy.deepcopy(pakli)
        harc_kazamatak = copy.deepcopy(kazamata_lista)
    except Exception as e:
        print(f"Hiba a harc előkészítésekor (másolás): {e}")
        return

    kazamata_nev = file_helye.name.replace("out.harc", "").replace(".txt", "")
    akt_kazamata_lista = [k for k in harc_kazamatak if k.elnevezes.endswith(kazamata_nev)]
    
    if not akt_kazamata_lista:
        akt_kazamata_lista = harc_kazamatak

    file_helye = Path(file_helye)
    file_helye.parent.mkdir(parents=True, exist_ok=True)
    kor_szamlalo = 0
    
    if not harc_pakli:
        print("Hiba: A pakli üres, nincs mivel harcolni.")
        return
    if not akt_kazamata_lista:
        print("Hiba: Nincsenek kazamaták (ellenfél hiányzik).")
        return

    with file_helye.open("w", encoding="utf-8") as f:
        akt_jatekos = harc_pakli[0]
        akt_kazamata = akt_kazamata_lista[0]
        
        f.write(f"harc kezdodik;{akt_kazamata.elnevezes}\n")
        
        akcio_j = "kijatszik"
        akcio_k = "kijatszik"
        
        while harc_pakli and akt_kazamata_lista:
            kor_szamlalo += 1
            
            if akcio_k == "kijatszik":
                f.write(f"{kor_szamlalo}.kor;kazamata;{akcio_k};{akt_kazamata.nev};{akt_kazamata.sebzes};{akt_kazamata.eletero};{akt_kazamata.tipus}\n")
            else:
                f.write(f"{kor_szamlalo}.kor;kazamata;{akcio_k};{akt_kazamata.nev};{akt_kazamata.eletero};{akt_jatekos.nev};{akt_jatekos.eletero}\n")
            
            if akcio_j == "kijatszik":
                f.write(f"{kor_szamlalo}.kor;jatekos;{akcio_j};{akt_jatekos.nev};{akt_jatekos.sebzes};{akt_jatekos.eletero};{akt_jatekos.tipus}\n")
            else:
                f.write(f"{kor_szamlalo}.kor;jatekos;{akcio_j};{akt_jatekos.nev};{akt_jatekos.eletero};{akt_kazamata.nev};{akt_kazamata.eletero}\n")
            
            f.write("\n")
            
            akcio_j = "tamad"
            akcio_k = "tamad"
            
            tamado_sebzes_k = sebzes_szamitas(akt_kazamata.tipus, akt_jatekos.tipus, akt_kazamata.sebzes)
            akt_jatekos.eletero -= tamado_sebzes_k
            
            if akt_jatekos.eletero <= 0:
                harc_pakli.pop(0)
                
                if not harc_pakli:
                    f.write(f"kazamata nyert;{akt_kazamata.nev};{akt_kazamata.eletero}\n")
                    break
                else:
                    akt_jatekos = harc_pakli[0]
                    akcio_j = "kijatszik"
                    continue 
            
            tamado_sebzes_j = sebzes_szamitas(akt_jatekos.tipus, akt_kazamata.tipus, akt_jatekos.sebzes)
            akt_kazamata.eletero -= tamado_sebzes_j
            
            if akt_kazamata.eletero <= 0:
                akt_kazamata_lista.pop(0)
                
                if not akt_kazamata_lista:
                    f.write(f"jatekos nyert;{akt_jatekos.nev};{akt_jatekos.eletero}\n")
                    break
                else:
                    akt_kazamata = akt_kazamata_lista[0]
                    akcio_k = "kijatszik"
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
    """Játék üzemmód (nem implementált)."""
    pass

def run_automated_test(test_dir_path):
    """Futtatja az automatizált teszteket a megadott könyvtárból."""
    test_dir = Path(test_dir_path)
    in_file = test_dir / "in.txt"
    if not in_file.exists():
        print(f"Hiba: nem található az input fájl: {in_file}")
        return
    kazamata_vilag = []
    sorszam = 1
    sima_kartyak = []
    vezer_kartyak = []
    kazamatak = [] 
    gyujtemeny_kartyai = []
    pakli = [] 

    with in_file.open("r", encoding="utf-8") as in_fajl:
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
                with out_file.open("w", encoding="utf-8") as file:
                    for i in sima_kartyak:
                        file.write(f"kartya;{i.nev};{i.sebzes};{i.eletero};{i.tipus}\n")
                    file.write("\n")
                    for i in vezer_kartyak:
                        file.write(f"vezer;{i.nev};{i.sebzes};{i.eletero};{i.tipus}\n")
                    file.write("\n")
                    for i in kazamata_vilag:
                        file.write(f"kazamata;{i}\n")
                    file.write("\n")
            elif parancs == "export jatekos":
                out_file = test_dir / adat[1]
                with out_file.open("w", encoding="utf-8") as file:
                    for i in gyujtemeny_kartyai:
                        file.write(f"gyujtemeny;{i.nev};{i.sebzes};{i.eletero};{i.tipus}\n")
                    file.write(f"\n")
                    for i in pakli:
                        file.write(f"pakli;{i.nev}\n")
            elif parancs == "harc":
                file_nev = test_dir / adat[2]
                harc(pakli, kazamatak, file_nev, gyujtemeny_kartyai)
            
if __name__ == "__main__":
    main()
