import os, pygame, random, pytest

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1, 1))

from game.brainrots.bombardino_crocodilo import get_brainrot as croco
from game.brainrots.vaca_saturno_saturnita import get_brainrot as vaca
from game.brainrots.lirili_larila import get_brainrot as lirili
from game.brainrots.br_br_patapim import get_brainrot as patapim
from game.battle import BattleManager


def _stub(br):
    br.load_assets = lambda: None
    br.start_skill_animation = lambda *a, **k: None


@pytest.fixture
def duel_ventarron(monkeypatch):
    p1 = croco()
    p2 = vaca()
    _stub(p1)
    _stub(p2)
    battle = BattleManager(p1, p2, None)
    monkeypatch.setattr(random, "randint", lambda a, b: 20)
    return p1, p2, battle


@pytest.fixture
def duel_past(monkeypatch):
    p1 = vaca()
    p2 = lirili()
    _stub(p1)
    _stub(p2)
    battle = BattleManager(p1, p2, None)
    monkeypatch.setattr(random, "randint", lambda a, b: 15)
    return p1, p2, battle


@pytest.fixture
def duel_arbustote(monkeypatch):
    p1 = patapim()
    p2 = vaca()
    _stub(p1)
    _stub(p2)
    battle = BattleManager(p1, p2, None)
    monkeypatch.setattr(random, "randint", lambda a, b: 25)
    return p1, p2, battle


def test_ventarron_half_damage_same_turn(duel_ventarron):
    croc, vac, battle = duel_ventarron
    ventarron = croc.skills[1]
    bombazo = vac.skills[2]
    battle.apply_action(ventarron)
    energy_before = vac.energy
    battle.apply_action(bombazo)
    cost_event = [e for e in battle.events if e.kind == "cost"][-1]
    pp_spent = int(cost_event.text.split()[1])
    assert vac.energy == energy_before - pp_spent
    assert croc.hp == croc.max_hp - 20


def test_volver_pasado_recupera_pp_exactos(duel_past):
    vac, liri, battle = duel_past
    bombazo = vac.skills[2]
    volver = liri.skills[3]
    battle.apply_action(bombazo)
    lost = liri.last_energy_lost
    pre = liri.energy
    battle.apply_action(volver)
    assert liri.energy == pre + lost


def test_arbustote_nullify(duel_arbustote):
    pata, vac, battle = duel_arbustote
    arbustote = pata.skills[1]
    bombazo = vac.skills[2]
    battle.apply_action(arbustote)
    hp_before = pata.hp
    battle.apply_action(bombazo)
    assert any(e.text.endswith("fue anulado!") for e in battle.events)
    assert pata.hp == hp_before