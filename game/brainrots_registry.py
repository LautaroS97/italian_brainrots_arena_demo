from game.brainrots.bombardino_crocodilo import get_brainrot as _bombardino
from game.brainrots.vaca_saturno_saturnita import get_brainrot as _vaca
from game.brainrots.lirili_larila import get_brainrot as _lirili
from game.brainrots.br_br_patapim import get_brainrot as _patapim
from game.brainrots.tralalero_tralala import get_brainrot as _tralalero
from game.brainrots.tung_tung_sahur import get_brainrot as _tung

BRAINROTS = [
    _bombardino(),
    _vaca(),
    _lirili(),
    _patapim(),
    _tralalero(),
    _tung()
]