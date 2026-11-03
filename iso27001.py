"""ISO/IEC 27001:2022 clauses 4-10: the management system (styringssystem) requirements.

ISO text is copyrighted, so only the clause numbers are used, each with a short
Norwegian title written in my own words. The examples are my own, written for a
small business or home lab, not text from the standard.

Clauses 4-10 are often grouped in the Plan-Do-Check-Act cycle (PDCA):
Plan = 4-7, Do = 8, Check = 9, Act = 10.
"""

# The PDCA phases: (id, name, clause numbers in this phase)
PHASES = [
    ("planlegge", "Planlegge", ["4", "5", "6", "7"]),
    ("utfore", "Utføre", ["8"]),
    ("kontrollere", "Kontrollere", ["9"]),
    ("forbedre", "Forbedre", ["10"]),
]

# Each clause: number, name, and its requirements as (number, title in my own words).
CLAUSES = [
    {"number": "4", "name": "Organisasjonens kontekst", "items": [
        ("4.1", "Forstå virksomheten og omgivelsene"),
        ("4.2", "Interessenter og deres krav"),
        ("4.3", "Omfanget av styringssystemet"),
        ("4.4", "Etablere og forbedre styringssystemet"),
    ]},
    {"number": "5", "name": "Lederskap", "items": [
        ("5.1", "Ledelsens engasjement"),
        ("5.2", "Sikkerhetspolicy"),
        ("5.3", "Roller, ansvar og myndighet"),
    ]},
    {"number": "6", "name": "Planlegging", "items": [
        ("6.1.1", "Risikoer og muligheter"),
        ("6.1.2", "Risikovurdering"),
        ("6.1.3", "Risikobehandling og anvendelseserklæring"),
        ("6.2", "Sikkerhetsmål og plan for å nå dem"),
        ("6.3", "Planlegging av endringer"),
    ]},
    {"number": "7", "name": "Støtte", "items": [
        ("7.1", "Ressurser"),
        ("7.2", "Kompetanse"),
        ("7.3", "Bevissthet"),
        ("7.4", "Kommunikasjon"),
        ("7.5", "Dokumentert informasjon"),
    ]},
    {"number": "8", "name": "Drift", "items": [
        ("8.1", "Planlegging og styring av driften"),
        ("8.2", "Gjennomføre risikovurderinger"),
        ("8.3", "Gjennomføre risikobehandling"),
    ]},
    {"number": "9", "name": "Evaluering av ytelse", "items": [
        ("9.1", "Overvåking, måling og evaluering"),
        ("9.2", "Internrevisjon"),
        ("9.3", "Ledelsens gjennomgang"),
    ]},
    {"number": "10", "name": "Forbedring", "items": [
        ("10.1", "Kontinuerlig forbedring"),
        ("10.2", "Avvik og korrigerende tiltak"),
    ]},
]

# Every valid requirement number, e.g. {"4.1", ..., "6.1.2", ..., "10.2"}. Used to validate forms.
ITEM_IDS = {number for clause in CLAUSES for number, _title in clause["items"]}

# Links to other parts of the app: requirement -> list of (endpoint name, link text).
# Only where the connection is direct: the risk register is 6.1.2/6.1.3 and 8.2/8.3 in practice,
# and the statement of applicability (SoA) is part of 6.1.3.
LINKS = {
    "6.1.2": [("risk_list", "Risikoregisteret")],
    "6.1.3": [("risk_list", "Risikoregisteret"), ("iso_page", "Anvendelseserklæring (SoA)")],
    "8.2": [("risk_list", "Risikoregisteret")],
    "8.3": [("risk_list", "Risikoregisteret")],
}

# One example per requirement, for a small business or home lab (my own words).
EXAMPLES = {
    "4.1": "Skriv ned hva som er viktig å beskytte (familiebilder, kundedata, hjemmeserveren) "
           "og hva som påvirker det, f.eks. at mye kjører i skyen og at nivået for cyberrisiko er høyt.",
    "4.2": "List opp hvem som har krav eller forventninger: kunder, Datatilsynet (GDPR), "
           "leverandøren av nettskyen og familien som bruker nettverket.",
    "4.3": "Avgrens hva styringssystemet dekker, f.eks. «hjemmelab, NAS og to laptoper, "
           "men ikke jobbmaskinen», og skriv ned hvorfor.",
    "4.4": "Bestem hvordan arbeidet skal gå i ring: planlegge, gjøre, sjekke og forbedre. "
           "Denne appen er et enkelt eksempel på et slikt system.",
    "5.1": "Den som bestemmer (deg selv eller daglig leder) setter av tid og penger til sikkerhet "
           "og følger opp at det blir gjort.",
    "5.2": "En halv side om hva du vil oppnå: f.eks. «MFA overalt, sikkerhetskopi hver natt, "
           "oppdateringer innen 14 dager». Signer og datér den.",
    "5.3": "Avklar hvem som eier hva: hvem har ansvar for ruteren, sikkerhetskopiene og "
           "hvem som får varsel ved en hendelse.",
    "6.1.1": "Tenk gjennom hva som kan gå galt eller bli bedre før du setter mål, "
             "f.eks. løsepengevirus på NAS eller muligheten til å automatisere oppdateringer.",
    "6.1.2": "Bestem én fast metode for å vurdere risiko, f.eks. sannsynlighet × konsekvens på "
             "skala 1–5, slik at vurderingene kan sammenlignes over tid.",
    "6.1.3": "Velg behandling for hver risiko (redusere, akseptere, unngå, overføre) og marker "
             "hvilke ISO 27002-kontroller som gjelder i anvendelseserklæringen.",
    "6.2": "Sett målbare mål, f.eks. «100 % av kontoene har MFA innen mars» og "
           "«gjenoppretting testet hvert kvartal», med ansvarlig og frist.",
    "6.3": "Før store endringer, som ny brannmur eller flytting til skyen, planlegg dem og "
           "vurder hva som kan gå galt underveis.",
    "7.1": "Sørg for nok tid, penger og utstyr, f.eks. en ekstra disk til sikkerhetskopier "
           "og et par timer i måneden til vedlikehold.",
    "7.2": "Finn ut hva du må kunne og lær det, f.eks. et kurs i nettverkssikkerhet. "
           "Ta vare på kursbevis som dokumentasjon.",
    "7.3": "Alle som bruker systemene skal vite hvorfor reglene finnes, f.eks. "
           "en kort prat med familien om phishing og passordhåndterer.",
    "7.4": "Bestem hva som skal kommuniseres, til hvem og når, f.eks. hvem som "
           "varsles ved et innbrudd og hvordan.",
    "7.5": "Hold policy, risikovurderinger og logger samlet ett sted med versjon og dato, "
           "f.eks. i et privat Git-repo.",
    "8.1": "Gjennomfør det som er planlagt og hold styr på endringer, "
           "f.eks. en enkel endringslogg for ruteren og serveren.",
    "8.2": "Gå gjennom risikoene med jevne mellomrom og etter store endringer, "
           "f.eks. hvert halvår og etter at ny tjeneste er åpnet mot internett.",
    "8.3": "Gjennomfør tiltakene i risikobehandlingsplanen og noter hva som er gjort "
           "og når, f.eks. «MFA på e-post aktivert 12.03».",
    "9.1": "Bestem hva som måles og hvor ofte, f.eks. andel enheter med siste oppdatering "
           "og om nattens sikkerhetskopi gikk bra.",
    "9.2": "Sjekk en gang i året om du faktisk følger egne regler, gjerne med en "
           "sjekkliste. Noter funn som avvik.",
    "9.3": "Én gang i året: se på mål, hendelser, risikoer og revisjonsfunn, "
           "og bestem hva som skal endres. Skriv et kort referat.",
    "10.1": "Bruk funn, hendelser og målinger til å gjøre systemet litt bedre hver gang, "
            "f.eks. automatisere noe som ofte glipper.",
    "10.2": "Når noe ikke er som det skal (f.eks. en feilet sikkerhetskopi): rett det, finn "
            "årsaken, gjør et tiltak så det ikke skjer igjen, og noter det.",
}
