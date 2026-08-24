# -*- coding: utf-8 -*-
"""
Variantes rédactionnelles des sections fixes, assignées par hash du slug
(stables d'un build à l'autre, pas de rotation visible par index).
Chaque variante porte la même information — seule la rédaction change.
`{name}`, `{prov}` etc. sont remplis par le générateur.
"""

import hashlib


def pick(slug, section, options):
    """Choix stable d'une variante pour (ville, section)."""
    h = int(hashlib.md5(f"{slug}:{section}".encode()).hexdigest(), 16)
    return options[h % len(options)]


HERO_SUBTITLE = [
    "Installazione pensiline fotovoltaiche per parcheggi aziendali a {name}{prov_virgola}",
    "Pensiline fotovoltaiche chiavi in mano per i parcheggi delle aziende di {name}",
    "Progettiamo e installiamo pensiline fotovoltaiche per le aziende di {name}{prov_virgola}",
    "Il parcheggio della tua azienda a {name} può produrre energia solare",
]

INTRO_P1 = [
    ("<strong>Rossini Energy</strong> installa <strong>pensiline fotovoltaiche per parcheggi aziendali a {name}</strong>{prov_parentesi}: "
     "sopralluogo gratuito, progettazione e cantiere chiavi in mano in 8-12 settimane."),
    ("A {name}{prov_parentesi}, <strong>Rossini Energy</strong> realizza <strong>pensiline fotovoltaiche per parcheggi aziendali</strong> "
     "con formula chiavi in mano: sopralluogo gratuito e attivazione in 8-12 settimane dalla firma."),
    ("Installare una <strong>pensilina fotovoltaica sul parcheggio aziendale a {name}</strong> richiede 8-12 settimane con "
     "<strong>Rossini Energy</strong>: sopralluogo gratuito, progetto e cantiere gestiti da un unico interlocutore."),
    ("<strong>Rossini Energy</strong> porta le <strong>pensiline fotovoltaiche per parcheggi aziendali</strong> alle imprese di "
     "{name}{prov_parentesi}: dal sopralluogo gratuito all'attivazione, tutto chiavi in mano in 8-12 settimane."),
]

INTRO_P2 = [
    ("La soluzione si basa sulle <a href=\"https://rossinienergy.it/pensilina-fotovoltaica-in-legno/\">pensiline fotovoltaiche TOSSO® in legno</a>: "
     "struttura in legno Douglas, pannelli fotovoltaici bifacciali e punti di ricarica integrati direttamente nella tettoia."),
    ("Il cuore dell'offerta sono le <a href=\"https://rossinienergy.it/pensilina-fotovoltaica-in-legno/\">pensiline fotovoltaiche TOSSO® in legno</a>, "
     "con struttura in Douglas, moduli bifacciali e punti di ricarica già integrati nella tettoia."),
    ("Usiamo le <a href=\"https://rossinienergy.it/pensilina-fotovoltaica-in-legno/\">pensiline fotovoltaiche TOSSO® in legno</a>: "
     "Douglas lamellare, pannelli bifacciali e ricarica dei veicoli integrata nella struttura stessa."),
]

BENEFITS = [
    ("I vantaggi per la tua azienda: autoconsumo dell'energia solare, riduzione dei costi energetici, "
     "protezione dei veicoli e accesso agli incentivi fiscali per le imprese (iperammortamento)."),
    ("Per l'azienda significa: bolletta più leggera grazie all'autoconsumo, veicoli protetti da sole e grandine, "
     "e incentivi fiscali dedicati alle imprese (iperammortamento)."),
    ("Tre benefici concreti: energia solare autoconsumata, parcheggio riparato tutto l'anno, "
     "investimento agevolato dagli incentivi per le imprese (iperammortamento)."),
    ("Il risultato: costi energetici ridotti dall'autoconsumo, auto protette sotto la tettoia, "
     "e un investimento che le imprese possono agevolare con l'iperammortamento."),
]

SOLAR_P = [
    ("Un impianto fotovoltaico da <strong>30 kWp</strong> installato su una pensilina a {name} produce circa "
     "<strong>{annual} kWh/anno</strong> secondo i dati del sistema europeo PVGIS. Questo equivale a un "
     "<strong>risparmio stimato di 8.000-9.000 € l'anno</strong> sulle bollette energetiche, con un ritorno "
     "sull'investimento in 6-8 anni."),
    ("A {name}, i dati PVGIS indicano per un impianto da <strong>30 kWp</strong> su pensilina una produzione di circa "
     "<strong>{annual} kWh all'anno</strong>: in bolletta vale un <strong>risparmio stimato di 8.000-9.000 € annui</strong>, "
     "con rientro dell'investimento in 6-8 anni."),
    ("Secondo PVGIS, una pensilina da <strong>30 kWp</strong> a {name} genera circa <strong>{annual} kWh/anno</strong>. "
     "Tradotto: <strong>8.000-9.000 € di risparmio stimato ogni anno</strong> e un investimento che rientra in 6-8 anni."),
]

SOLAR_MONTHLY = [
    ("La produzione varia durante l'anno: da circa <strong>{mmin} kWh a {mmin_name}</strong> a "
     "<strong>{mmax} kWh a {mmax_name}</strong> — un profilo che si sposa bene con i consumi diurni di un'azienda."),
    ("Il profilo mensile va da <strong>{mmin} kWh a {mmin_name}</strong> fino a <strong>{mmax} kWh a {mmax_name}</strong>: "
     "la curva segue bene i consumi diurni delle attività produttive."),
    ("Tra il minimo di <strong>{mmin} kWh a {mmin_name}</strong> e il picco di <strong>{mmax} kWh a {mmax_name}</strong>, "
     "la produzione accompagna l'orario di lavoro tipico di un'azienda."),
]

POIS_P1_FEW = [
    ("A {name} sono attualmente censiti <strong>{ev}</strong> punti di ricarica per veicoli elettrici e "
     "<strong>{parking}</strong> parcheggi pubblici. Il territorio presenta un potenziale significativo per "
     "l'espansione della rete di ricarica elettrica."),
    ("I dati OpenStreetMap contano a {name} <strong>{ev}</strong> punti di ricarica EV e <strong>{parking}</strong> "
     "parcheggi pubblici: margini ampi per nuova infrastruttura di ricarica."),
    ("Oggi {name} conta <strong>{ev}</strong> punti di ricarica per veicoli elettrici su <strong>{parking}</strong> "
     "parcheggi censiti — la rete locale ha ancora molto spazio per crescere."),
]

POIS_P1_MANY = [
    ("A {name} sono attualmente censiti <strong>{ev}</strong> punti di ricarica per veicoli elettrici e "
     "<strong>{parking}</strong> parcheggi pubblici. La domanda di ricarica è in costante crescita e richiede "
     "nuove infrastrutture."),
    ("Con <strong>{ev}</strong> punti di ricarica EV e <strong>{parking}</strong> parcheggi censiti, {name} mostra "
     "una domanda di mobilità elettrica già matura e in crescita."),
    ("{name} conta già <strong>{ev}</strong> punti di ricarica e <strong>{parking}</strong> parcheggi pubblici: "
     "una rete viva, che continua ad aver bisogno di nuova capacità."),
]

POIS_P2 = [
    ("Rossini Energy può coprire i parcheggi esistenti di {name} con pensiline fotovoltaiche TOSSO®, "
     "trasformandoli in parcheggi solari con punti di ricarica integrati."),
    ("Coprendo questi parcheggi con pensiline TOSSO®, Rossini Energy li trasforma in parcheggi solari "
     "con ricarica integrata per i veicoli."),
    ("Ogni parcheggio esistente a {name} è un candidato: con una pensilina TOSSO® diventa un parcheggio "
     "solare, con la ricarica dei veicoli già integrata."),
]

NEARBY_INTRO = [
    "Operiamo anche nelle seguenti città della Lombardia vicine a {name}:",
    "Il servizio copre anche queste città lombarde vicino a {name}:",
    "Interveniamo inoltre in queste città della zona di {name}:",
]

CTA_P = [
    ("Sei un'azienda o PMI a {name} e vuoi ridurre i costi energetici? Installa una pensilina fotovoltaica "
     "sul parcheggio aziendale e produci energia pulita. Contattaci per un sopralluogo e preventivo gratuito."),
    ("La tua azienda è a {name}? Trasforma il parcheggio in una fonte di energia con una pensilina "
     "fotovoltaica: sopralluogo e preventivo sono gratuiti."),
    ("Riduci le bollette della tua impresa a {name}: una pensilina fotovoltaica sul parcheggio produce "
     "energia pulita da subito. Il sopralluogo e il preventivo non costano nulla."),
]

SERVICES = [
    # Variante 1 (l'attuale)
    [
        ("☀️", "Pensiline Fotovoltaiche TOSSO®",
         "Tettoie per parcheggi aziendali con pannelli fotovoltaici bifacciali, struttura in legno Douglas sostenibile. Producono energia solare e proteggono i veicoli."),
        ("🔑", "Servizio Chiavi in Mano",
         "Sopralluogo, progettazione, pratiche edilizie (CILA), installazione e allaccio alla rete: gestiamo ogni fase, dalla firma all'attivazione in 8-12 settimane."),
        ("💻", "Software di Gestione Energia",
         "Piattaforma di pilotaggio dinamico per ottimizzare l'autoconsumo dell'energia solare prodotta e gestire la ricarica dei veicoli elettrici."),
    ],
    # Variante 2
    [
        ("☀️", "Pensiline Fotovoltaiche TOSSO®",
         "Strutture in legno Douglas con moduli bifacciali: il parcheggio produce energia e ripara i veicoli da sole, pioggia e grandine."),
        ("🔑", "Servizio Chiavi in Mano",
         "Un solo interlocutore dal sopralluogo all'allaccio: progetto, CILA, cantiere e collaudo, con attivazione in 8-12 settimane."),
        ("💻", "Software di Gestione Energia",
         "Il pilotaggio dinamico massimizza l'autoconsumo e coordina la ricarica dei veicoli con la produzione solare del momento."),
    ],
    # Variante 3
    [
        ("☀️", "Pensiline Fotovoltaiche TOSSO®",
         "Legno lamellare Douglas certificato e pannelli bifacciali ad alta resa: la copertura del parcheggio diventa un impianto fotovoltaico."),
        ("🔑", "Servizio Chiavi in Mano",
         "Gestiamo noi l'intero percorso — sopralluogo, progettazione, pratiche CILA, installazione, allaccio — in 8-12 settimane."),
        ("💻", "Software di Gestione Energia",
         "Monitoraggio e pilotaggio intelligente: l'energia prodotta va prima all'autoconsumo e alla ricarica dei veicoli aziendali."),
    ],
]

# --- FAQ : pool élargi. Réponses socle en 3 variantes chacune. ---

FAQ_PRODUZIONE = [
    ("Quanto produce una pensilina fotovoltaica a {name}?",
     "A {name}, un impianto da 30 kWp installato su pensilina produce circa {annual} kWh all'anno secondo i dati PVGIS, con un risparmio stimato di 8.000-9.000 € l'anno sulla bolletta energetica."),
    ("Quanta energia genera una pensilina fotovoltaica a {name}?",
     "I dati PVGIS indicano circa {annual} kWh all'anno per un impianto da 30 kWp a {name}: in bolletta, un risparmio stimato di 8.000-9.000 € annui."),
    ("Che produzione ci si può aspettare a {name}?",
     "Circa {annual} kWh all'anno con 30 kWp su pensilina (fonte PVGIS): per un'azienda significa risparmiare 8.000-9.000 € l'anno di energia."),
]

FAQ_TEMPI = [
    ("Quanto tempo serve per l'installazione?",
     "Dalla firma del contratto all'attivazione servono 8-12 settimane. Rossini Energy gestisce progettazione, pratiche edilizie, installazione e allaccio alla rete."),
    ("In quanto tempo la pensilina è operativa?",
     "8-12 settimane dalla firma: progettazione, pratiche edilizie, cantiere e allaccio sono gestiti interamente da Rossini Energy."),
    ("Quali sono i tempi di realizzazione?",
     "Il percorso completo — progetto, permessi, installazione, allaccio — richiede 8-12 settimane, tutto seguito da Rossini Energy."),
]

FAQ_INCENTIVI = [
    ("Quali incentivi fiscali esistono per le aziende?",
     "Le imprese possono ammortizzare l'investimento con gli incentivi in vigore, come l'iperammortamento previsto dalla Legge di Bilancio 2026; Rossini Energy vi supporta nella pratica."),
    ("L'investimento è agevolato fiscalmente?",
     "Sì: le imprese accedono agli incentivi in vigore, a partire dall'iperammortamento della Legge di Bilancio 2026. La pratica la seguiamo insieme."),
    ("Come si riduce il costo dell'investimento?",
     "Con gli incentivi per le imprese — in primis l'iperammortamento (Legge di Bilancio 2026) — e con il risparmio in bolletta generato dall'autoconsumo."),
]

FAQ_PERMESSI = [
    ("Servono permessi edilizi?",
     "In genere è sufficiente una CILA (Comunicazione di Inizio Lavori Asseverata). Rossini Energy gestisce l'intera pratica burocratica."),
    ("Che autorizzazioni servono per una pensilina fotovoltaica?",
     "Nella maggior parte dei casi basta una CILA. La pratica burocratica è inclusa nel servizio Rossini Energy."),
    ("La burocrazia è complicata?",
     "No: di norma è sufficiente una CILA, e se ne occupa direttamente Rossini Energy all'interno del servizio chiavi in mano."),
]

FAQ_MANUTENZIONE = [
    ("Chi si occupa della manutenzione?",
     "Rossini Energy offre contratti di manutenzione pluriennali con monitoraggio remoto dell'impianto e interventi programmati."),
    ("Come funziona la manutenzione dell'impianto?",
     "Con un contratto pluriennale Rossini Energy: monitoraggio remoto continuo e interventi programmati quando servono."),
    ("L'impianto va seguito nel tempo?",
     "Sì, ma se ne occupa Rossini Energy: contratti pluriennali con monitoraggio remoto e manutenzione programmata."),
]

FAQ_ENTI = [
    ("Anche enti pubblici possono installare pensiline fotovoltaiche?",
     "Sì. A {name} sedi comunali, scuole e ASL possono coprire i propri parcheggi con pensiline fotovoltaiche; Rossini Energy partecipa anche a procedure di gara pubblica."),
    ("Il servizio è disponibile per il settore pubblico?",
     "Sì: a {name} lavoriamo anche con comuni, scuole e strutture sanitarie, incluse le procedure di gara pubblica."),
]

FAQ_INDUSTRIA = [
    ("Le pensiline sono adatte alle aree industriali?",
     "Sì. Le strutture TOSSO® in legno lamellare Douglas classe GL24h hanno certificazione statica per neve e vento e coprono anche grandi parcheggi industriali."),
    ("Una struttura in legno regge in ambiente industriale?",
     "Sì: il Douglas lamellare GL24h delle pensiline TOSSO® è certificato staticamente per neve e vento, anche su grandi superfici industriali."),
]

FAQ_COMMERCIO = [
    ("Cosa cambia per un centro commerciale?",
     "La pensilina offre riparo ai clienti, riduce la temperatura estiva delle auto e alimenta illuminazione e ricarica dei veicoli con l'energia prodotta dal parcheggio stesso."),
    ("Che vantaggi ha un'attività commerciale?",
     "Clienti riparati, auto meno roventi d'estate, e l'energia del parcheggio che alimenta illuminazione e colonnine: il parcheggio diventa un servizio."),
]

FAQ_TURISMO = [
    ("Una struttura ricettiva può beneficiarne?",
     "Sì. Hotel e ristoranti a {name} possono coprire una parte del fabbisogno con l'energia della pensilina e comunicare agli ospiti una scelta green visibile."),
    ("Ha senso per hotel e ristoranti?",
     "Sì: a {name} una pensilina copre parte del fabbisogno della struttura e mostra agli ospiti un impegno green concreto."),
]

FAQ_PMI = [
    ("Anche una piccola azienda può permettersi una pensilina fotovoltaica?",
     "Sì: anche PMI con 10-20 dipendenti possono installare una pensilina da 10-15 kWp. Con gli incentivi e il risparmio in bolletta, l'investimento si ammortizza in pochi anni."),
    ("Serve essere una grande azienda?",
     "No: una PMI con 10-20 dipendenti può partire da una pensilina di 10-15 kWp, con investimento agevolato dagli incentivi e ripagato dal risparmio in bolletta."),
]

FAQ_SPAZIO = [
    ("Quanto spazio serve nel parcheggio?",
     "Una pensilina da 30 kWp copre circa 200-300 m² di parcheggio, ovvero 10-15 posti auto. Le strutture sono modulari e si adattano allo spazio disponibile."),
    ("Quanti posti auto servono per l'impianto?",
     "Con 10-15 posti auto (200-300 m²) si arriva a circa 30 kWp. La struttura è modulare: si parte anche da superfici più piccole."),
]
