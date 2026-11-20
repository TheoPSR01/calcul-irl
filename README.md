# calcul-irl

Calculer la révision annuelle d'un loyer d'habitation avec l'indice de référence des loyers (IRL) publié par l'INSEE. Pour les locataires qui veulent vérifier une hausse et les propriétaires qui doivent l'appliquer. Aucune dépendance.

## Installation

```bash
pip install git+https://github.com/TheoPSR01/calcul-irl.git
```

Python 3.10 ou plus récent.

## En ligne de commande

Loyer de 750 € hors charges, bail qui prend le 3e trimestre comme référence, révision en 2026 :

```bash
calcul-irl 750 --trimestre 3 --annee 2026
```

```
Indices         : 145,77 → 148,06 (1,57 %)
Loyer actuel    : 750,00 €
Nouveau loyer   : 761,78 € (+11,78 € par mois)
```

```bash
calcul-irl 750                       # dernier indice connu
calcul-irl 750 --dpe G               # logement F ou G : pas de hausse
calcul-irl 750 --irl 145,77 148,06   # indices saisis à la main
calcul-irl 0 --liste                 # indices connus par l'outil
```

## En Python

```python
from calcul_irl import reviser_loyer, reviser

r = reviser_loyer(750, trimestre=3, annee=2026)
print(r.nouveau_loyer, r.variation_pct)   # 761.78 1.57

reviser(800, irl_ancien=100, irl_nouveau=102).nouveau_loyer   # 816.00
```

## Règles appliquées

Nouveau loyer = loyer actuel × IRL du trimestre de référence de l'année de révision / IRL du même trimestre un an plus tôt. Le trimestre de référence est celui indiqué dans le bail ; à défaut, c'est le dernier indice publié à la signature. La révision n'est possible que si le bail contient une clause de révision.

Logements classés F ou G au diagnostic de performance énergétique : le loyer ne peut pas être augmenté.

Indices inclus : IRL France métropolitaine de l'INSEE, du 1er trimestre 2022 au 3e trimestre 2026 (base 100 au 4e trimestre 1998).

## Limites

Les IRL spécifiques à l'Outre-mer et à la Corse ne sont pas inclus (utilisez `--irl`). Le propriétaire qui tarde à demander la révision perd la hausse au-delà d'un an ; l'outil ne vérifie pas les délais. Les règles d'encadrement des loyers de certaines villes et les baux commerciaux (ILC, ILAT) ne sont pas traités.

Chaque trimestre, l'INSEE publie un nouvel indice : il suffit de l'ajouter au dictionnaire `IRL`.

## Contribuer

```bash
git clone https://github.com/TheoPSR01/calcul-irl.git
cd calcul-irl
pip install -e ".[dev]"
pytest
```

## Licence

MIT
