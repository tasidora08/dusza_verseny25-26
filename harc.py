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
    def __init__(self, uj_nev, alap_kartya, duplazas):
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
    def __init__(self, tipusa, elnevezes, nev, mitad, alap_kartya):
        super().__init__(
            alap_kartya.nev,
            alap_kartya.sebzes,
            alap_kartya.eletero,
            alap_kartya.tipus,
            alap_kartya.sorszam
    )
        self.tipusa = tipusa
        self.elnevezes = elnevezes
        self.nev = nev
        self.mitad = mitad
    def szep_kiiras(self):
        return f"Típus: {self.tipus}, {self.elnevezes}, {self.nev}, {self.mitad}"

class Gyujtemeny():
    def __init__(self, nev):
        self.nev = nev
    def __str__(self):
        return f"{self.nev}"



#BEOLVASÁS
sorszam = 1
sima_kartyak = []
vezer_kartyak = []
kazamatak = []
gyujtemeny_kartyai = []
pakli = []
with open("01\in.txt", "r", encoding="utf-8") as in_fajl:
    for sor in in_fajl:
        adat = sor.strip().split(";")
        if adat[0] == "uj kartya":
            uj_s_kartya = Kartya(adat[1], adat[2], adat[3], adat[4], sorszam)
            sorszam += 1
            sima_kartyak.append(uj_s_kartya)
        elif adat[0] == "uj vezer":
            for i in sima_kartyak:
                if i.nev == adat[2]:
                    alap_kartya = i
            if alap_kartya:
                uj_vezer = Vezer(adat[1], alap_kartya, adat[3])
                vezer_kartyak.append(uj_vezer)
        elif adat[0] == "uj kazamata":
            alap_kartya = next((k for k in sima_kartyak if k.nev == adat[3]), None)
            if alap_kartya:
                uj_kazamata = Kazamata(adat[1], adat[2], alap_kartya, adat[4])
                kazamatak.append(uj_kazamata)
        elif adat[0] == "felvetel gyujtemenybe":
            gyujtemeny_resze = Gyujtemeny(adat[1])
            gyujtemeny_kartyai.append(gyujtemeny_resze)
        elif adat[0] == "uj pakli":
            pakli_n = adat[1].split(",")
            for i in pakli_n:
                for j in sima_kartyak:
                    if j.nev == i:
                        pakli.append(j)




#harc
def harc(pakli,kazamata):
    kor_szamlalo=0
    akt_kazamata = kazamata[0]      
    print(f"harc kezdődik: {akt_kazamata.nev}") 
    while pakli and kazamata:
        
        akt_jatekos=pakli[0]
        akt_kazamata = kazamata[0]
        akcio_j= "kijatszas"
        akcio_k="kijatszas"
        while pakli and kazamata:
            kor_szamlalo+=1
            print(f"{kor_szamlalo}.kor;kazamata;{akcio_k};{akt_kazamata.nev};{akt_kazamata.sebzes};{akt_kazamata.eletero};{akt_kazamata.tipus}")
            print(f"{kor_szamlalo}.kor;jatekos;{akcio_j};{akt_jatekos.nev};{akt_jatekos.sebzes};{akt_jatekos.eletero};{akt_jatekos.tipus}")
            akcio_j="tamad"
            akcio_k="tamad"
            akt_jatekos.eletero -= sebzes_szamitas(akt_kazamata.tipus,akt_jatekos.tipus,akt_kazamata.sebzes) 
            if akt_jatekos.eletero <=0:             
                pakli.pop(0)
                akcio_j="kijatszas"
                
                if not pakli :
                    print(f"kazamata nyert;{akt_kazamata.eletero};{akt_kazamata.nev}")
                    break
                else:akt_jatekos=pakli[0]
            akt_kazamata.eletero -= sebzes_szamitas( akt_jatekos.tipus,akt_kazamata.tipus,akt_jatekos.sebzes)
            if akt_kazamata.eletero <=0:
                kazamata.pop(0)
                akcio_k="kijatszas"
                
                if not kazamata:
                    print(f"jatekos nyert;{akt_jatekos.eletero};{akt_jatekos.nev}")
                    break
                else: akt_kazamata=kazamata[0]
                    
                        
            
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