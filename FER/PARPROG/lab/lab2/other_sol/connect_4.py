# mpiexec -hostfile hostfile -n 5 python dz2.py -- za specificiranje racunala
# mpiexec -rankfile rankfile -n 5 python dz2.py -- za mapiranje na jezgre
# moguca i kombinacija
from mpi4py import MPI
from ploca import *
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

OZNAKA_PODACI = 1
OZNAKA_ZAHTJEV = 2
OZNAKA_ZADATAK = 3
OZNAKA_REZULTAT = 4
OZNAKA_CEKAJ = 5
OZNAKA_KRAJ = 6

BROJ_RAZINA = 8
BROJ_RAZINA_MASTER = 3
BROJ_RAZINA_WORKER = BROJ_RAZINA - BROJ_RAZINA_MASTER

comm.Barrier()

if rank == 0:  # master

    def _dohvati_neki_zadatak():  # funkcija koja dohvaca neki slobodan zadatak
        for k, v in zadaci.items():
            if v == None: return k
        return None


    def _izracunaj_kvalitetu_poteza():  # funkcija koja racuna kvalitetu poteza (djecu korijena)
        kvaliteta = {}
        for x in range(1, 8):
            suma = 0.0
            for y in range(1, 8):
                suma += zadaci[(x, y)]
            kvaliteta[x] = suma / 7

        return kvaliteta


    def  _salji_kraj():
        for x in range(1, size):
            poruka = {'vrsta': OZNAKA_KRAJ}
            comm.send(poruka, dest=x)


    def _ucitaj_potez_igraca():
        while True:
            tekst = input("Tvoj potez (unesi stupac): ")
            try:
                stupac = int(tekst)
                if stupac >= 0 and stupac <= 7:
                    return stupac
                else:
                    raise ValueError()
            except ValueError:
                print("Unos mora biti između 1 i 7!")


    def _provjeri_kraj_igre_sve():
        for x in range(1, 8):
            ishod = _provjeri_kraj_igre(x)
            if ishod != None:
                return ishod
        return None


    def _provjeri_kraj_igre(stupac):
        ishod = ploca.provjeri_kraj(stupac)
        if ishod[0] == True:
            return ishod[1]
        else:
            return None


    # inicijaliziraj plocu
    ploca = Ploca()

    # ploca = Ploca.ucitaj()
    # ploca.ispisi_polje()

    ishod = _provjeri_kraj_igre_sve()
    if ishod != None:
        _salji_kraj
        print("Pobjednik: ", ishod)
        exit()

    # za jedan ciklus izracuna zadataka
    while True:

        t_start = time.time()

        # napravi 7*7 zadataka
        # zadaci su ostvareni u rjecniku
        # oznake - zadatak koji se ne obraduje - None
        #        - zadatak koji se obraduje - True
        #        - obavljeni zadatak - broj
        zadaci = {}

        for x in range(1, 8):
            for y in range(1, 8):
                zadaci[(x, y)] = None

        # podjeli podatke
        for x in range(1, size):
            # ploca ce se predati kao deep copy
            poruka = {'vrsta': OZNAKA_PODACI, 'ploca': ploca}
            comm.send(poruka, dest=x)

        # salji zadatke na zahtjev
        aktivnih_radnika = size - 1  # broj radnika koji nisu dobili poruku za cekanje
        gotovo = False
        while not gotovo:

            stat = MPI.Status()
            poruka = comm.recv(source=MPI.ANY_SOURCE, status=stat)
            src = stat.Get_source()

            if poruka['vrsta'] == OZNAKA_ZAHTJEV:

                zadatak = _dohvati_neki_zadatak()

                if zadatak != None:
                    zadaci[zadatak] = True
                    odgovor = {'vrsta': OZNAKA_ZADATAK, 'zadatak': zadatak}
                    comm.send(odgovor, dest=src)
                else:
                    aktivnih_radnika -= 1
                    if aktivnih_radnika == 0:
                        gotovo = True
                    odgovor = {'vrsta': OZNAKA_CEKAJ}
                    comm.send(odgovor, dest=src)

            if poruka['vrsta'] == OZNAKA_REZULTAT:
                zadaci[poruka['zadatak']] = poruka['rezultat']

        kvaliteta = _izracunaj_kvalitetu_poteza()
        stupac = max(kvaliteta, key=lambda a: kvaliteta.get(a))

        t_end = time.time()

        for k, v in kvaliteta.items():
            print(f'Kvaliteta poteza {k} je {v}')
        print(f'Stupac s najboljim ishodom: {stupac}')
        print(f'Proteklo vrijeme: {t_end - t_start} s')

        ploca.odigraj_potez(Ploca.OZNAKA_CPU, stupac)
        ploca.ispisi_polje()
        ishod = _provjeri_kraj_igre(stupac)
        if ishod != None:
            print("CPU je pobjedio!")
            _salji_kraj()
            break

        potez_igraca = _ucitaj_potez_igraca()
        if potez_igraca == 0:
            print('Igra prekinuta')
            _salji_kraj()
            break
        else:
            ploca.odigraj_potez(Ploca.OZNAKA_IGRAC, potez_igraca)
            ploca.ispisi_polje()
            ishod = _provjeri_kraj_igre(potez_igraca)
            if ishod != None:
                print("Ti si pobjednik!")
                _salji_kraj()
                break

else:  # radnik

    def ocijeni(potezCPU, zadnjiStupac, dubina):
        '''
        
        :param potezCPU: je li cpu na redu
        :param zadnjiStupac: 
        :param dubina: 
        :return: 
        '''

        provjera_kraja = ploca.provjeri_kraj(zadnjiStupac)
        if provjera_kraja[0]:
            if provjera_kraja[1] == Ploca.OZNAKA_CPU:
                return 1
            else:  # provjera_kraja[1] == OZNAKA_IGRAC
                return -1

        # ako igra nije gotova
        if dubina == 0:
            return 0

        oznaka = Ploca.OZNAKA_CPU if potezCPU else Ploca.OZNAKA_IGRAC

        ukupno = 0.0
        sva_djeca_gubici = True
        sva_djeca_pobjede = True
        for idx_stupca in range(1, 8):

            ploca.odigraj_potez(oznaka, idx_stupca)
            rezultat = ocijeni(not potezCPU, idx_stupca, dubina - 1)
            ploca.ponisti_potez(idx_stupca)

            if rezultat > -1:
                sva_djeca_gubici = False
            if rezultat != 1:
                sva_djeca_pobjede = False
            if rezultat == 1 and potezCPU == False:
                return 1  # ako je pobjeda otkrivena prije poteza igraca
            if rezultat == -1 and potezCPU == True:
                return -1
            ukupno += rezultat

        if sva_djeca_pobjede: return 1
        if sva_djeca_gubici: return -1
        return ukupno / 7


    while True:

        poruka = comm.recv(source=0)

        if poruka['vrsta'] == OZNAKA_KRAJ:
            time.sleep(1)
            break

        # novi ciklus racunanja poteza
        if poruka['vrsta'] == OZNAKA_PODACI:
            ploca = poruka['ploca']

        gotovo = False
        while True:
            zahtjev = {'vrsta': OZNAKA_ZAHTJEV}
            comm.send(zahtjev, dest=0)

            # provjeri ima li jos zadataka u ciklusu
            odgovor = comm.recv(source=0)
            if odgovor['vrsta'] == OZNAKA_CEKAJ:
                break

            # zadatak je definiran ntorkom(potez racunala, potez igraca)
            zadatak = odgovor['zadatak']

            # dovedi plocu u odgovarajuce stanje
            # tu se nalaze i inicijalne provjere

            # prvi potez zadatka izvodi racunalo
            ploca.odigraj_potez(Ploca.OZNAKA_CPU, zadatak[0])
            if ploca.provjeri_kraj(zadatak[0])[0] == True:
                rezultat = 1
                ploca.ponisti_potez(zadatak[0])
                poruka = {'vrsta': OZNAKA_REZULTAT, 'zadatak': zadatak, 'rezultat': rezultat}
                comm.send(poruka, dest=0)
                continue

            # drugi potez izvodi igrac
            ploca.odigraj_potez(Ploca.OZNAKA_IGRAC, zadatak[1])
            if ploca.provjeri_kraj(zadatak[1])[0] == True:
                rezultat = -1
                ploca.ponisti_potez(zadatak[1])
                ploca.ponisti_potez(zadatak[0])
                poruka = {'vrsta': OZNAKA_REZULTAT, 'zadatak': zadatak, 'rezultat': rezultat}
                comm.send(poruka, dest=0)
                continue

            # ako u prva dva poteza nije gotovo
            # racunaj
            rezultat = ocijeni(True, zadatak[1], BROJ_RAZINA_WORKER)

            # vrati plocu u prvobitno stanje
            ploca.ponisti_potez(zadatak[1])
            ploca.ponisti_potez(zadatak[0])

            # vrati rezultat
            poruka = {'vrsta': OZNAKA_REZULTAT, 'zadatak': zadatak, 'rezultat': rezultat}
            comm.send(poruka, dest=0)
