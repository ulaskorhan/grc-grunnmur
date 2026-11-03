"""ISO/IEC 27002:2022: the 93 controls in 4 themes, and how NSM's principles link to them.

ISO text is copyrighted, so only the control numbers are used, each with a short
Norwegian title written in my own words (not a translation of the standard).
ISO 27001:2022 Annex A lists the same 93 controls; ISO 27002 gives the guidance.

The links between NSM and ISO come from NSM's own table (nsm_iso_mapping.py),
never from my own judgement.
"""

from nsm_iso_mapping import MEASURES

# The 4 themes: (chapter number, name, id used in the URL)
THEMES = [
    ("5", "Organisatoriske kontroller", "organisatoriske"),
    ("6", "Personellkontroller", "personell"),
    ("7", "Fysiske kontroller", "fysiske"),
    ("8", "Teknologiske kontroller", "teknologiske"),
]

# Control number -> short title in my own words.
CONTROLS = {
    # 5 Organisatoriske (37)
    "5.1": "Sikkerhetspolicyer",
    "5.2": "Roller og ansvar for sikkerhet",
    "5.3": "Atskillelse av oppgaver",
    "5.4": "Ledelsens ansvar",
    "5.5": "Kontakt med myndigheter",
    "5.6": "Kontakt med faggrupper og nettverk",
    "5.7": "Trusselinformasjon",
    "5.8": "Sikkerhet i prosjekter",
    "5.9": "Oversikt over informasjon og eiendeler",
    "5.10": "Akseptabel bruk av informasjon og eiendeler",
    "5.11": "Tilbakelevering av eiendeler",
    "5.12": "Klassifisering av informasjon",
    "5.13": "Merking av informasjon",
    "5.14": "Overføring av informasjon",
    "5.15": "Tilgangsstyring",
    "5.16": "Identitetsforvaltning",
    "5.17": "Autentiseringsinformasjon",
    "5.18": "Tilgangsrettigheter",
    "5.19": "Sikkerhet i leverandørforhold",
    "5.20": "Sikkerhet i leverandøravtaler",
    "5.21": "Sikkerhet i IKT-leverandørkjeden",
    "5.22": "Oppfølging og endring av leverandørtjenester",
    "5.23": "Sikker bruk av skytjenester",
    "5.24": "Planlegging for hendelseshåndtering",
    "5.25": "Vurdering av sikkerhetshendelser",
    "5.26": "Respons på sikkerhetshendelser",
    "5.27": "Læring etter hendelser",
    "5.28": "Innsamling av bevis",
    "5.29": "Sikkerhet under avbrudd",
    "5.30": "IKT-beredskap for kontinuitet",
    "5.31": "Lovpålagte og avtalefestede krav",
    "5.32": "Immaterielle rettigheter",
    "5.33": "Beskyttelse av arkiv og registre",
    "5.34": "Personvern og personopplysninger",
    "5.35": "Uavhengig gjennomgang av sikkerheten",
    "5.36": "Etterlevelse av policyer og regler",
    "5.37": "Dokumenterte driftsrutiner",
    # 6 Personell (8)
    "6.1": "Bakgrunnssjekk",
    "6.2": "Ansettelsesvilkår",
    "6.3": "Sikkerhetsbevissthet og opplæring",
    "6.4": "Disiplinærprosess",
    "6.5": "Ansvar etter avsluttet eller endret ansettelse",
    "6.6": "Taushetserklæringer",
    "6.7": "Fjernarbeid",
    "6.8": "Rapportering av sikkerhetshendelser",
    # 7 Fysiske (14)
    "7.1": "Fysiske sikkerhetssoner",
    "7.2": "Fysisk adgangskontroll",
    "7.3": "Sikring av kontorer og rom",
    "7.4": "Fysisk overvåking",
    "7.5": "Vern mot fysiske og miljømessige trusler",
    "7.6": "Arbeid i sikrede områder",
    "7.7": "Ryddig pult og låst skjerm",
    "7.8": "Plassering og beskyttelse av utstyr",
    "7.9": "Sikkerhet for utstyr utenfor lokalene",
    "7.10": "Lagringsmedier",
    "7.11": "Strøm og annen infrastruktur",
    "7.12": "Sikring av kabler",
    "7.13": "Vedlikehold av utstyr",
    "7.14": "Sikker avhending og gjenbruk av utstyr",
    # 8 Teknologiske (34)
    "8.1": "Brukerenheter",
    "8.2": "Privilegerte tilganger",
    "8.3": "Begrensning av tilgang til informasjon",
    "8.4": "Tilgang til kildekode",
    "8.5": "Sikker autentisering",
    "8.6": "Kapasitetsstyring",
    "8.7": "Vern mot skadevare",
    "8.8": "Håndtering av tekniske sårbarheter",
    "8.9": "Konfigurasjonsstyring",
    "8.10": "Sletting av informasjon",
    "8.11": "Maskering av data",
    "8.12": "Hindring av datalekkasje",
    "8.13": "Sikkerhetskopiering",
    "8.14": "Redundans",
    "8.15": "Logging",
    "8.16": "Overvåking av aktivitet",
    "8.17": "Klokkesynkronisering",
    "8.18": "Bruk av privilegerte verktøy",
    "8.19": "Installasjon av programvare i drift",
    "8.20": "Nettverkssikkerhet",
    "8.21": "Sikkerhet i nettverkstjenester",
    "8.22": "Segmentering av nettverk",
    "8.23": "Filtrering av nettrafikk",
    "8.24": "Bruk av kryptografi",
    "8.25": "Sikker utviklingslivssyklus",
    "8.26": "Sikkerhetskrav til applikasjoner",
    "8.27": "Sikker systemarkitektur",
    "8.28": "Sikker koding",
    "8.29": "Sikkerhetstesting i utvikling og godkjenning",
    "8.30": "Utsatt utvikling",
    "8.31": "Atskilte utviklings-, test- og produksjonsmiljøer",
    "8.32": "Endringshåndtering",
    "8.33": "Testdata",
    "8.34": "Beskyttelse av systemer under revisjonstesting",
}


def sort_key(control_id):
    """Sort "5.10" after "5.9": compare the numbers, not the text."""
    return [int(part) for part in control_id.split(".")]


def controls_for_principle(principle_id):
    """The ISO 27002 controls NSM links to any measure under one principle, e.g. "2.3"."""
    found = set()
    for measure_id, (_priority, controls) in MEASURES.items():
        if measure_id.rsplit(".", 1)[0] == principle_id:   # "2.3.7" -> "2.3"
            found.update(controls)
    return sorted(found, key=sort_key)


def principles_for_control(control_id):
    """The NSM principles with at least one measure NSM links to this control."""
    found = {measure_id.rsplit(".", 1)[0]
             for measure_id, (_priority, controls) in MEASURES.items()
             if control_id in controls}
    return sorted(found, key=sort_key)


def themes_with_controls():
    """Everything the ISO 27002 page needs: each theme with its controls and NSM links."""
    themes = []
    for number, name, theme_id in THEMES:
        controls = [
            {"id": cid, "title": title, "principles": principles_for_control(cid)}
            for cid, title in CONTROLS.items()
            if cid.split(".")[0] == number
        ]
        covered = sum(1 for c in controls if c["principles"])
        themes.append({"number": number, "name": name, "id": theme_id,
                       "controls": controls, "covered": covered})
    return themes
