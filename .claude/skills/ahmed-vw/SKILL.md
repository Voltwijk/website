---
name: ahmed-vw
description: Ahmed VW, de vaste werkwijze van Voltwijk voor offertes op maat (thuisbatterij, warmtepomp, zonnepanelen, airco), korte appjes, klantmails, schouwrapporten voor de installateurs en "Schouw op afstand"-mails, inclusief het CRM bijwerken. Gebruik dit bij elke vraag als "maak een offerte voor ...", "kort appje", "maak de mail", "installatiepapieren", "schouwrapport", klantgegevens die worden doorgegeven, of vragen over prijzen en producten van Voltwijk.
---

# Ahmed VW (doorverwijzing)

De echte skill, met alle regels, prijzen, het gereedschap en de voorbeelden, staat in de repository **Voltwijk/CRM** in
`.claude/skills/ahmed-vw/`. Deze chat draait op Voltwijk/website; haal de CRM-repository er dus eerst bij:

1. Staat `Voltwijk/CRM` nog niet in deze sessie: koppel hem met de tool `add_repo` (owner `Voltwijk`, repo `CRM`, access `read`),
   clone hem zoals de tool aangeeft (bijv. naar `/home/user/CRM`) en meld hem aan met `register_repo_root`.
2. Installeer de afhankelijkheden als `node_modules` ontbreekt: `cd <CRM-map> && npm ci`.
3. Lees `<CRM-map>/.claude/skills/ahmed-vw/SKILL.md` en volg die letterlijk, inclusief `regels.md`, `prijzen-en-producten.md`,
   `kennis.md` en de voorbeelden. Alle paden in die skill zijn relatief aan de CRM-map.
4. Antwoord in het Nederlands, zonder emoji's.

Lukt koppelen niet, zeg dan dat de gebruiker een nieuwe chat start met de repository **Voltwijk/CRM**.
