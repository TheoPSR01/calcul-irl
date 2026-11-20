from decimal import Decimal

import pytest

from calcul_irl import IRL, dernier_irl, indice, main, reviser, reviser_loyer


def test_variations_publiees_par_l_insee():
    # Glissements annuels publiés : +1,57 % au T3 2026, +0,78 % au T1 2026, +3,50 % au T4 2022
    assert reviser_loyer(1000, 3, 2026).variation_pct == Decimal("1.57")
    assert reviser_loyer(1000, 1, 2026).variation_pct == Decimal("0.78")
    assert reviser_loyer(1000, 4, 2023).variation_pct == Decimal("3.50")


def test_nouveau_loyer():
    r = reviser_loyer(750, 3, 2026)
    assert r.irl_ancien == Decimal("145.77") and r.irl_nouveau == Decimal("148.06")
    assert r.nouveau_loyer == Decimal("761.78")
    assert r.hausse_mensuelle == Decimal("11.78")


def test_dpe_f_ou_g_bloque_la_hausse():
    r = reviser_loyer(750, 3, 2026, dpe="g")
    assert r.bloque_dpe and r.nouveau_loyer == Decimal(750)
    assert not reviser_loyer(750, 3, 2026, dpe="D").bloque_dpe


def test_indices_manuels():
    assert reviser("800,00", "100", "102").nouveau_loyer == Decimal("816.00")


def test_indice_inconnu():
    with pytest.raises(ValueError):
        indice(2030, 1)
    with pytest.raises(ValueError):
        indice(2025, 5)


def test_serie_complete():
    assert dernier_irl() == (2026, 3, Decimal("148.06"))
    assert len(IRL) == 19


def test_cli(capsys):
    assert main(["750", "--trimestre", "3", "--annee", "2026"]) == 0
    assert "Nouveau loyer   : 761,78 € (+11,78 € par mois)" in capsys.readouterr().out
    assert main(["750", "--dpe", "F"]) == 0
    assert "ne peut pas être augmenté" in capsys.readouterr().out
    assert main(["750", "--annee", "2031"]) == 2


def test_cli_aide():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
