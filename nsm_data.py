"""The NSM basic principles for ICT security (Grunnprinsipper for IKT-sikkerhet).

Source:  https://nsm.no/regelverk-og-hjelp/rad-og-anbefalinger/grunnprinsipper-for-ikt-sikkerhet/
Version: 2.1 (published 04.06.2024, updated 28.10.2024)
Fetched: 28.10.2026

The numbers and titles are copied exactly from NSM's website. Each principle
links to its own page on nsm.no, which has the full text and the measures (tiltak).
"""

BASE = "https://nsm.no/regelverk-og-hjelp/rad-og-anbefalinger/"
SOURCE_URL = BASE + "grunnprinsipper-for-ikt-sikkerhet/"
VERSION = "2.1"

# Each category has an id (used in the URL), a number, a name and its principles.
# Each principle is a tuple: (number, title, link path on nsm.no).
CATEGORIES = [
    {
        "id": "identifisere",
        "number": "1",
        "name": "Identifisere og kartlegge",
        "principles": [
            ("1.1", "Kartlegg styringsstrukturer, leveranser og understøttende systemer",
             "identifisere-og-kartlegge/kartlegg-styringsstrukturer-leveranser-og-understottende-systemer/"),
            ("1.2", "Kartlegg enheter og programvare",
             "identifisere-og-kartlegge/kartlegg-enheter-og-programvare/"),
            ("1.3", "Kartlegg brukere og behov for tilgang",
             "identifisere-og-kartlegge/kartlegg-brukere-og-behov-for-tilgang/"),
        ],
    },
    {
        "id": "beskytte",
        "number": "2",
        "name": "Beskytte og opprettholde",
        "principles": [
            ("2.1", "Ivareta sikkerhet i anskaffelses- og utviklingsprosesser",
             "beskytte-og-opprettholde/ivareta-sikkerhet-i-anskaffelses-og-utviklingsprosesser/"),
            ("2.2", "Etabler en sikker IKT-arkitektur",
             "beskytte-og-opprettholde/etabler-en-sikker-ikt-arkitektur/"),
            ("2.3", "Ivareta en sikker konfigurasjon",
             "beskytte-og-opprettholde/ivareta-en-sikker-konfigurasjon/"),
            ("2.4", "Beskytt virksomhetens nettverk",
             "beskytte-og-opprettholde/beskytt-virksomhetens-nettverk/"),
            ("2.5", "Kontroller dataflyt",
             "beskytte-og-opprettholde/kontroller-dataflyt/"),
            ("2.6", "Ha kontroll på identiteter og tilganger",
             "beskytte-og-opprettholde/ha-kontroll-pa-identiteter-og-tilganger/"),
            ("2.7", "Beskytt data i ro og i transitt",
             "beskytte-og-opprettholde/beskytt-data-i-ro-og-i-transitt/"),
            ("2.8", "Beskytt e-post og nettleser",
             "beskytte-og-opprettholde/beskytt-e-post-og-nettleser/"),
            ("2.9", "Etabler evne til gjenoppretting av data",
             "beskytte-og-opprettholde/etabler-evne-til-gjenoppretting-av-data/"),
            ("2.10", "Integrer sikkerhet i prosess for endringshåndtering",
             "beskytte-og-opprettholde/integrer-sikkerhet-i-prosess-for-endringshandtering/"),
        ],
    },
    {
        "id": "oppdage",
        "number": "3",
        "name": "Oppdage",
        "principles": [
            ("3.1", "Oppdag og fjern kjente sårbarheter og trusler",
             "oppdage/oppdag-og-fjern-kjente-sarbarheter-og-trusler/"),
            ("3.2", "Etabler sikkerhetsovervåkning",
             "oppdage/etabler-sikkerhetsovervakning/"),
            ("3.3", "Analyser data fra sikkerhetsovervåkning",
             "oppdage/analyser-data-fra-sikkerhetsovervakning/"),
            ("3.4", "Gjennomfør inntrengningstester",
             "oppdage/gjennomfor-inntrengningstester/"),
        ],
    },
    {
        "id": "handtere",
        "number": "4",
        "name": "Håndtere og gjenopprette",
        "principles": [
            ("4.1", "Forbered virksomheten på håndtering av hendelser",
             "handtere-og-gjenopprette/forbered-virksomheten-pa-handtering-av-hendelser/"),
            ("4.2", "Vurder og klassifiser hendelser",
             "handtere-og-gjenopprette/vurder-og-klassifiser-hendelser/"),
            ("4.3", "Kontroller og håndter hendelser",
             "handtere-og-gjenopprette/kontroller-og-handter-hendelser/"),
            ("4.4", "Evaluer og lær av hendelser",
             "handtere-og-gjenopprette/evaluer-og-laer-av-hendelser/"),
        ],
    },
]


def find_category(category_id):
    """Return the category with this id, or None if it does not exist."""
    for category in CATEGORIES:
        if category["id"] == category_id:
            return category
    return None
