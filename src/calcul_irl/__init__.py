"""calcul_irl : révision annuelle d'un loyer d'habitation avec l'IRL.

Nouveau loyer = loyer actuel × IRL du trimestre de référence de l'année de
révision / IRL du même trimestre de l'année précédente. Le trimestre de
référence est indiqué dans le bail. Pour un logement classé F ou G au DPE,
le loyer ne peut pas être augmenté.

Valeurs : IRL France métropolitaine publié par l'INSEE (base 100 au
4e trimestre 1998).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Optional, Union

__version__ = "0.1.0"

Montant = Union[int, float, str, Decimal]

#: IRL France métropolitaine, clé (année, trimestre). Source : INSEE.
IRL = {
    (2022, 1): Decimal("133.93"), (2022, 2): Decimal("135.84"), (2022, 3): Decimal("136.27"), (2022, 4): Decimal("137.26"),
    (2023, 1): Decimal("138.61"), (2023, 2): Decimal("140.59"), (2023, 3): Decimal("141.03"), (2023, 4): Decimal("142.06"),
    (2024, 1): Decimal("143.46"), (2024, 2): Decimal("145.17"), (2024, 3): Decimal("144.51"), (2024, 4): Decimal("144.64"),
    (2025, 1): Decimal("145.47"), (2025, 2): Decimal("146.68"), (2025, 3): Decimal("145.77"), (2025, 4): Decimal("145.78"),
    (2026, 1): Decimal("146.60"), (2026, 2): Decimal("148.37"), (2026, 3): Decimal("148.06"),
}


def _d(x: Montant) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x).replace(",", ".").replace(" ", ""))


def dernier_irl() -> tuple:
    """(année, trimestre, valeur) du dernier indice connu par le paquet."""
    cle = max(IRL)
    return cle[0], cle[1], IRL[cle]


def indice(annee: int, trimestre: int) -> Decimal:
    if trimestre not in (1, 2, 3, 4):
        raise ValueError("le trimestre va de 1 à 4")
    try:
        return IRL[(annee, trimestre)]
    except KeyError:
        a, t, _ = dernier_irl()
        raise ValueError(f"IRL du {trimestre}e trimestre {annee} inconnu (dernier connu : T{t} {a}) ; "
                         "indiquez les indices vous-même") from None


@dataclass(frozen=True)
class Revision:
    loyer_actuel: Decimal
    nouveau_loyer: Decimal
    irl_ancien: Decimal
    irl_nouveau: Decimal
    variation_pct: Decimal
    bloque_dpe: bool

    @property
    def hausse_mensuelle(self) -> Decimal:
        return self.nouveau_loyer - self.loyer_actuel


def reviser(loyer: Montant, irl_ancien: Montant, irl_nouveau: Montant, dpe: Optional[str] = None) -> Revision:
    """Révision à partir de deux indices. ``dpe`` : classe énergétique (A à G), facultative."""
    l, a, n = _d(loyer), _d(irl_ancien), _d(irl_nouveau)
    if l <= 0 or a <= 0 or n <= 0:
        raise ValueError("loyer et indices doivent être positifs")
    variation = ((n / a - 1) * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    bloque = dpe is not None and dpe.strip().upper() in ("F", "G") and n > a
    nouveau = l if bloque else (l * n / a).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Revision(l, nouveau, a, n, variation, bloque)


def reviser_loyer(loyer: Montant, trimestre: int, annee: int, dpe: Optional[str] = None) -> Revision:
    """Révision avec l'IRL du trimestre de référence de l'année ``annee`` et de l'année précédente."""
    return reviser(loyer, indice(annee - 1, trimestre), indice(annee, trimestre), dpe)


def _fr(x: Decimal) -> str:
    return f"{x:,.2f}".replace(",", " ").replace(".", ",")


def main(argv=None) -> int:
    a, t, v = dernier_irl()
    p = argparse.ArgumentParser(prog="calcul-irl", description="Révision d'un loyer d'habitation avec l'IRL.")
    p.add_argument("--version", action="version", version=f"calcul-irl {__version__}")
    p.add_argument("loyer", help="loyer mensuel actuel hors charges")
    p.add_argument("--trimestre", type=int, default=t, help=f"trimestre de référence du bail (défaut : {t})")
    p.add_argument("--annee", type=int, default=a, help=f"année du nouvel indice (défaut : {a})")
    p.add_argument("--irl", nargs=2, metavar=("ANCIEN", "NOUVEAU"), help="indiquer les deux indices directement")
    p.add_argument("--dpe", help="classe DPE du logement (A à G)")
    p.add_argument("--liste", action="store_true", help="afficher les indices connus")
    args = p.parse_args(argv)
    if args.liste:
        for (an, tr), val in sorted(IRL.items()):
            print(f"T{tr} {an} : {str(val).replace('.', ',')}")
        return 0
    try:
        if args.irl:
            r = reviser(args.loyer, args.irl[0], args.irl[1], args.dpe)
        else:
            r = reviser_loyer(args.loyer, args.trimestre, args.annee, args.dpe)
    except (ValueError, InvalidOperation) as exc:
        print(f"calcul-irl : {exc}", file=sys.stderr)
        return 2
    print(f"Indices         : {str(r.irl_ancien).replace('.', ',')} → {str(r.irl_nouveau).replace('.', ',')} ({str(r.variation_pct).replace('.', ',')} %)")
    print(f"Loyer actuel    : {_fr(r.loyer_actuel)} €")
    print(f"Nouveau loyer   : {_fr(r.nouveau_loyer)} € (+{_fr(r.hausse_mensuelle)} € par mois)")
    if r.bloque_dpe:
        print("Logement classé F ou G : le loyer ne peut pas être augmenté.")
    return 0


__all__ = ["IRL", "Revision", "dernier_irl", "indice", "main", "reviser", "reviser_loyer"]
