"""Example answers for each NSM principle, shown behind the "Eksempel" button.

These examples are NOT from NSM. They were written for Grunnmur to show what
a finished answer could look like for a personal home lab. Change them freely
to fit your own setup.
"""

EXAMPLES = {
    # 1. Identifisere og kartlegge
    "1.1": "Jeg eier og drifter hjemmelabben alene. Det viktigste å beskytte er "
           "privat e-post, bilder i skylagring, NAS med sikkerhetskopier og lab-miljøet. "
           "Disse er avhengige av ruteren fra internettleverandøren, NAS-en, "
           "Proxmox-serveren og e-postkontoen min. Oversikten ligger i labbens README.",
    "1.2": "Liste over alle enheter: laptop (macOS), mobil, ruter, NAS, Raspberry Pi "
           "og to virtuelle maskiner. For hver enhet: operativsystem, versjon og formål. "
           "Listen sjekkes med et nmap-skann av hjemmenettet når noe nytt kobles til.",
    "1.3": "Brukere: meg (administrator) og ett familiemedlem (vanlig bruker på NAS). "
           "Kun min egen konto har admin-rettigheter, og ingen passord deles. "
           "Tilgangene gjennomgås hver sjette måned.",

    # 2. Beskytte og opprettholde
    "2.1": "Før jeg kjøper nytt utstyr sjekker jeg at leverandøren gir "
           "sikkerhetsoppdateringer i flere år. Egen kode ligger på GitHub med "
           "Dependabot slått på, så sårbare avhengigheter blir varslet.",
    "2.2": "Nettet er delt i soner: hovednett, gjestenett for IoT-enheter og et eget "
           "VLAN for labben. Lab-maskinene når ikke hovednettet. En enkel "
           "nettverkstegning ligger i dokumentasjonen.",
    "2.3": "Standardpassord er byttet på ruter og NAS. Unødvendige funksjoner som UPnP "
           "og WPS er slått av. Linux-serverne herdes med et Ansible-playbook basert på "
           "CIS Benchmark nivå 1.",
    "2.4": "Brannmuren på ruteren blokkerer all innkommende trafikk. Ingen porter er "
           "åpne mot internett; fjerntilgang skjer kun via WireGuard VPN. "
           "Wi-Fi bruker WPA3.",
    "2.5": "Lab-VLAN-et kan bare nå internett, ikke hovednettet. IoT-enheter er "
           "blokkert fra å kommunisere med laptop og NAS. DNS-oppslag filtreres "
           "gjennom Pi-hole.",
    "2.6": "MFA er slått på for e-post, skylagring, GitHub og passordhåndtereren. "
           "Alle passord er unike og ligger i passordhåndtereren. Jeg bruker en "
           "vanlig konto til daglig og admin-kontoen bare ved behov.",
    "2.7": "Disken på laptopen er kryptert (FileVault), og NAS-volumet er kryptert. "
           "Tjenestene i labben brukes kun over HTTPS eller SSH. "
           "Sikkerhetskopier i skyen krypteres før opplasting.",
    "2.8": "Nettleseren oppdateres automatisk og har en reklameblokkering. "
           "E-postleverandøren filtrerer spam, og mitt eget domene har SPF, "
           "DKIM og DMARC satt opp.",
    "2.9": "3-2-1-backup: originalen på laptopen, én kopi på NAS og én kryptert kopi "
           "i skyen. Gjenoppretting testes hvert kvartal ved å hente tilbake en mappe "
           "og sjekke at filene åpner.",
    "2.10": "Endringer i labben føres i en enkel endringslogg: hva, når, hvorfor og "
            "hvordan rulle tilbake. Ansible-oppsettet ligger i Git, så en endring "
            "kan reverseres.",

    # 3. Oppdage
    "3.1": "Automatiske oppdateringer er på for laptop og mobil. Fastvaren på ruter "
           "og NAS sjekkes hver måned. Labben skannes for sårbarheter med Greenbone "
           "(OpenVAS) én gang i måneden.",
    "3.2": "Logger fra ruter, servere og Windows-VM sendes til en SIEM i labben "
           "(f.eks. Splunk eller Wazuh). Det går et varsel ved mange mislykkede "
           "innlogginger på kort tid.",
    "3.3": "Hver søndag bruker jeg 15 minutter på å gå gjennom varsler og dashbord. "
           "Falske alarmer justeres, og funn noteres i en logg.",
    "3.4": "To ganger i året tester jeg labben selv med nmap, Nikto og verktøy fra "
           "Kali Linux, kun mot egne systemer. Funn blir oppgaver som følges opp.",

    # 4. Håndtere og gjenopprette
    "4.1": "En hendelsesplan på én side: hvem jeg kontakter (bank, e-postleverandør), "
           "hvordan jeg isolerer en enhet og hvor sikkerhetskopiene ligger. "
           "Planen finnes også utskrevet.",
    "4.2": "Tre nivåer: Lav (phishing-e-post uten klikk), Middels (skadevare på én "
           "enhet) og Høy (kompromittert konto med personopplysninger, mulig "
           "avvik etter GDPR).",
    "4.3": "Ved mistanke om innbrudd: koble enheten fra nettet, bytt passord fra en "
           "annen ren enhet, sjekk innloggingshistorikken og gjenopprett fra backup "
           "om nødvendig.",
    "4.4": "Etter hver hendelse skriver jeg et kort notat: hva skjedde, hva fungerte "
           "og hva jeg endrer. Deretter oppdateres hendelsesplanen og denne trackeren.",
}
