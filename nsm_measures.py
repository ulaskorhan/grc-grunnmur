"""NSM's 118 measures (tiltak) under the 21 basic principles, with NSM's priority (v5).

Source:  NSM, "Regneark med tiltak fra NSMs grunnprinsipper for IKT-sikkerhet" (xlsx),
         sheet "01 NSM GP-IKT 2.1", columns "Tiltak ID" and "Tiltaksoverskrift".
         https://nsm.no/regelverk-og-hjelp/rad-og-anbefalinger/stotteprodukter/stotteprodukter-til-nsms-grunnprinsipper-for-ikt-sikkerhet
Fetched: 03.11.2026 (the sheet says it was last changed 2026-04)

The headings are copied exactly from NSM, like the principle titles in nsm_data.py.
The full description of each measure is on the principle's own page on nsm.no.
The priority comes from nsm_iso_mapping.py (same spreadsheet).
"""

import nsm_iso_mapping

SOURCE_URL = ("https://nsm.no/regelverk-og-hjelp/rad-og-anbefalinger/stotteprodukter/"
              "stotteprodukter-til-nsms-grunnprinsipper-for-ikt-sikkerhet")

# NSM's three priority groups (sheet "02 Om prioritering av tiltak"), in my own short words:
# group 1 is what NSM sees as most urgent, and the root cause of most successful attacks.
GROUPS = {
    1: ("Gruppe 1", "Haster mest"),
    2: ("Gruppe 2", "Viderekommende"),
    3: ("Gruppe 3", "Resten av tiltakene"),
}

# Measure id -> NSM's heading. The first two numbers are the principle: "2.6.4" is under 2.6.
TITLES = {
    "1.1.1": "Identifiser virksomhetens strategi og prioriterte mål",
    "1.1.2": "Identifiser virksomhetens strukturer og prosesser for sikkerhetsstyring.",
    "1.1.3": "Identifiser virksomhetens prosesser for risikostyring knyttet til IKT",
    "1.1.4": "Identifiser virksomhetens toleransegrenser for risiko knyttet til IKT",
    "1.1.5": "Kartlegg virksomhetens leveranser, informasjonssystemer og understøttende IKT-funksjoner",
    "1.1.6": "Kartlegg informasjonsbehandling og dataflyt i virksomheten",
    "1.2.1": "Etabler en prosess for å kartlegge enheter og programvare som er i bruk i virksomheten",
    "1.2.2": "Fastsett retningslinjer for godkjente enheter og programvare i virksomheten",
    "1.2.3": "Kartlegg enheter i bruk i virksomheten",
    "1.2.4": "Kartlegg programvare i bruk i virksomheten",
    "1.3.1": "Kartlegg brukere i informasjonssystemene, inkludert",
    "1.3.2": "Kartlegg og definer de ulike brukerkategoriene",
    "1.3.3": "Kartlegg ansvar og roller spesielt knyttet til IKT-sikkerhet",
    "2.1.1": "Integrer sikkerhet i virksomhetens prosess for anskaffelser",
    "2.1.2": "Kjøp moderne og oppdatert maskin- og programvare",
    "2.1.3": "Foretrekk IKT-produkter som er sertifiserte og evaluert av en tiltrodd tredjepart",
    "2.1.4": "Reduser risiko for målrettet manipulasjon av IKT-produkter i leverandørkjeden",
    "2.1.5": "Benytt en metode for sikker utvikling av programvare",
    "2.1.6": "Benytt separate miljøer for utvikling, test og produksjon",
    "2.1.7": "Gjennomfør tilstrekkelig med testing gjennom hele utviklingsprosessen",
    "2.1.8": "Vedlikehold programvarekode som utvikles/benyttes i virksomheten",
    "2.1.9": "Ta ansvar for virksomhetens sikkerhet også ved tjenesteutsetting",
    "2.1.10": "Undersøk sikkerheten hos tjenesteleverandør ved tjenesteutsetting",
    "2.2.1": "Etabler og vedlikehold en helhetlig sikkerhetsarkitektur",
    "2.2.2": "Bygg IKT-systemet med IKT-produkter som fungerer godt sammen sikkerhetsmessig",
    "2.2.3": "Del opp virksomhetens nettverk etter virksomhetens risikoprofil",
    "2.2.4": "Skill fysisk de mest kritiske del-nettverkene",
    "2.2.5": "Del opp domenearkitekturen iht. virksomhetens behov",
    "2.2.6": "Reguler tilgang til tjenester basert på kjennskap til både brukere og enhet",
    "2.2.7": "Etabler en robust og motstandsdyktig IKT-arkitektur",
    "2.3.1": "Etabler et sentralt styrt regime for sikkerhetsoppdatering",
    "2.3.2": "Konfigurer klienter slik at kun kjent programvare kjører på dem",
    "2.3.3": "Deaktiver unødvendig funksjonalitet",
    "2.3.4": "Etabler og vedlikehold standard sikkerhetskonfigurasjoner",
    "2.3.5": "Verifiser at aktivert sikkerhetskonfigurasjon er i henhold til virksomhetens godkjente sikkerhetskonfigurasjon",
    "2.3.6": "Utfør all konfigurasjon, installasjon, og drift for øvrig på en trygg måte",
    "2.3.7": "Endre alle standardpassord på IKT-produktene før produksjonssetting",
    "2.3.8": "Ikke deaktiver kodebeskyttelsesfunksjoner",
    "2.3.9": "Etabler sikker tid i virksomheten",
    "2.3.10": "Reduser risiko med IoT-enheter",
    "2.4.1": "Etabler tilgangskontroll på flest mulige nettverksporter",
    "2.4.2": "Krypter alle trådløse og kablede forbindelser",
    "2.4.3": "Kartlegg fysisk tilgjengelighet for svitsjer og kabler",
    "2.4.4": "Aktiver brannmur på alle klienter og servere",
    "2.5.1": "Styr dataflyt mellom nettverks-soner",
    "2.5.2": "Begrens tilgangen til interne tjenester fra eksterne lokasjoner",
    "2.5.3": "Sperr all direkte-trafikk mellom klienter",
    "2.5.4": "Isoler utstyr som er sårbart og har lav tillitt",
    "2.5.5": "Styr dataflyten til spesielt eksponerte tjenester",
    "2.5.6": "Beskytt spesielt kritiske tjenester med egen dataflyt",
    "2.5.7": "Ha kontroll på trafikk mellom virksomheten og samarbeidspartnere/ tjenesteleverandører",
    "2.5.8": "Styr all trafikk (ikke bare interne tjenester) til og fra forvaltede mobile klienter via virksomhetens nett",
    "2.6.1": "Etabler retningslinjer for tilgangskontroll",
    "2.6.2": "Etabler en formell prosess for administrasjon av kontoer, tilganger og rettigheter",
    "2.6.3": "Benytt et sentralisert og automatiserbart verktøy for å styre kontoer, tilganger og rettigheter",
    "2.6.4": "Minimer rettigheter til sluttbrukere og spesialbrukere",
    "2.6.5": "Minimer rettigheter på drifts-kontoer",
    "2.6.6": "Styr tilganger til enheter",
    "2.6.7": "Bruk multi-faktor autentisering",
    "2.7.1": "Etabler en strategi for håndtering av kryptografi i virksomheten",
    "2.7.2": "Aktiver kryptering i de tjenestene som tilbyr slik funksjonalitet",
    "2.7.3": "Krypter lagringsmedier som holder konfidensiell data og som lett kan mistes eller kompromitteres",
    "2.7.4": "Benytt kryptering når konfidensiell informasjon overføres eller når tilliten til informasjonskanalen er lav",
    "2.7.5": "Definer krav til sikringsnivå for ulike typer informasjon",
    "2.8.1": "Verifiser at innkommende e-post er fra en legitim avsender-adresse",
    "2.8.2": "Aktiver STARTTLS på virksomhetens e-postserver",
    "2.8.3": "Bruk kun støttede e-postklienter, nettlesere og programtillegg",
    "2.8.4": "Tillat kun virksomhetsgodkjente programtillegg",
    "2.9.1": "Legg en plan for regelmessig sikkerhetskopiering av alle virksomhetsdata",
    "2.9.2": "Inkluder sikkerhetskopier av programvare",
    "2.9.3": "Test sikkerhetskopier regelmessig",
    "2.9.4": "Beskytt sikkerhetskopier mot tilsiktet og utilsiktet sletting, manipulering og avlesning",
    "2.10.1": "Integrer sikkerhet i virksomhetens prosess for endringshåndtering",
    "2.10.2": "Involver nødvendig IKT-sikkerhetspersonell i forbindelse med endringer",
    "2.10.3": "Gjennomfør nødvendig endring, konfigurering og testing av påvirkede sikkerhetsfunksjoner",
    "2.10.4": "Integrer sikkerhet i virksomhetens prosess for hasteendringer",
    "3.1.1": "Gjennomfør jevnlig sårbarhetskartlegging",
    "3.1.2": "Abonner på tjenester relatert til sårbarhetsetterretning",
    "3.1.3": "Benytt automatisert og sentralisert verktøy for å håndtere kjente trusler (som skadevare)",
    "3.2.1": "Fastsett virksomhetens strategi og retningslinjer for sikkerhetsovervåkning",
    "3.2.2": "Følg lover, reguleringer og virksomhetens retningslinjer for sikkerhetsovervåkning",
    "3.2.3": "Avgjør hvilke deler av IKT-systemet som skal overvåkes",
    "3.2.4": "Beslutt hvilke data som er sikkerhetsrelevant og bør samles inn",
    "3.2.5": "Verifiser at innsamling fungerer etter hensikt",
    "3.2.6": "Påse at innsamlet data ikke kan manipuleres",
    "3.2.7": "Gjennomgå og konfigurer innhenting av sikkerhetsrelevant data og den sentrale loggdatabasen jevnlig",
    "3.3.1": "Lage en plan for analyse av data fra sikkerhetsovervåkning",
    "3.3.2": "Etabler og vedlikehold kompetanse om normaltilstanden i virksomhetens informasjonssystemer",
    "3.3.3": "Ta i bruk verktøy som muliggjør manuelle og automatiske søk, samt alarmering basert på kriterier",
    "3.3.4": "Innhent og bearbeid trusselinformasjon fra relevante kilder",
    "3.3.5": "Vurder fortløpende om innhentet data er tilstrekkelig relevant og detaljert",
    "3.3.6": "Etabler rutine for eskalering av alarmer",
    "3.3.7": "Benytt analyseverktøy, teknologi og algoritmer",
    "3.4.1": "Planlegg inntrengingstester med tydelig mål og omfang",
    "3.4.2": "Involver relevante interesseparter i forkant",
    "3.4.3": "Benytt verktøy for sårbarhetskartlegging og angrepsverktøy",
    "3.4.4": "Gjennomfør jevnlige inntrengingstester (minst årlige) for å identifisere sårbarheter",
    "3.4.5": "Test rutiner for deteksjon og beredskap",
    "3.4.6": "Kommuniser resultater fra inntrengingstester til relevante interesseparter",
    "4.1.1": "Etabler et planverk for hendelseshåndtering",
    "4.1.2": "Gjennomfør en analyse av virksomhetskritiske effekter",
    "4.1.3": "Utarbeid rolle- og ansvarsbeskrivelse for personell som skal involveres i hendelseshåndtering",
    "4.1.4": "Utarbeid avtaler med relevante tredjeparter",
    "4.1.5": "Fastsett hvilke kommunikasjonskanaler som skal benyttes i forbindelse med hendelser",
    "4.1.6": "Test og øv på planer jevnlig slik at disse er godt innøvd",
    "4.2.1": "Gjennomgå loggdata og samle relevante data om hendelsen for å oppnå et godt beslutningsgrunnlag",
    "4.2.2": "Avgjør alvorlighetsgrad for hendelsen",
    "4.2.3": "Informer relevante interesseparter",
    "4.3.1": "Kartlegg omfang og påvirkning på forretningsprosesser",
    "4.3.2": "Undersøk om hendelsen er under kontroll og gjennomfør nødvendige reaktive tiltak",
    "4.3.3": "Loggfør alle aktiviteter, resultater og relevante avgjørelser",
    "4.3.4": "Iverksett gjenopprettingsplan i løpet av, eller i etterkant av hendelsen",
    "4.3.5": "Koordiner og kommuniser med interne og eksterne interessenter underveis i hendelseshåndteringen",
    "4.3.6": "Gjennomfør nødvendige aktiviteter i etterkant av hendelsen",
    "4.4.1": "Identifiser erfaringer og læringspunkter («lessons learned») fra hendelser",
    "4.4.2": "Kartlegg og gjennomgå identifiserte, kompromitterte sikkerhetstiltak",
    "4.4.3": "Vurdere effektiviteten av prosesser, prosedyrer, rapporteringsformater og organisatoriske strukturer med tanke på å respondere på hendelser",
    "4.4.4": "Kommuniser og del erfaringsresultatene med (relevante) interessenter",
}


def principle_of(measure_id):
    """ "2.6.4" -> "2.6" """
    return measure_id.rsplit(".", 1)[0]


def sort_key(measure_id):
    """Sort by number, so 2.10.1 comes after 2.9.1 (plain text sorting would not)."""
    return [int(part) for part in measure_id.split(".")]


def measure(measure_id):
    """One measure as a dict: id, title, principle and priority."""
    return {
        "id": measure_id,
        "title": TITLES[measure_id],
        "principle": principle_of(measure_id),
        "priority": nsm_iso_mapping.MEASURES[measure_id][0],
    }


def for_principle(principle_id):
    """The measures under one principle, in NSM's order."""
    ids = [m for m in TITLES if principle_of(m) == principle_id]
    return [measure(m) for m in sorted(ids, key=sort_key)]


def by_group():
    """All measures split into NSM's priority groups: {1: [...], 2: [...], 3: [...]}."""
    groups = {number: [] for number in GROUPS}
    for measure_id in sorted(TITLES, key=sort_key):
        item = measure(measure_id)
        groups[item["priority"]].append(item)
    return groups


def suggestions(principle_id):
    """Measures to suggest for a risk linked to this principle: NSM's most urgent first."""
    return sorted(for_principle(principle_id), key=lambda m: (m["priority"], sort_key(m["id"])))
