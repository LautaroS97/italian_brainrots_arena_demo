import random
from game.brainrot import Brainrot
from game.skill import Skill
from game.skill_result import SkillResult
from game.skill_effects import (
    deal_damage,
    deal_damage_with_status,
    raise_defense_nullify,
    reflect_damage_if_direct,
)
from game.status_effects import Veneno


def _palo_borracho():
    nul = raise_defense_nullify()
    ref = reflect_damage_if_direct(2, 5)

    def fn(att, riv):
        nul(att, riv)
        ref(att, riv)
        return SkillResult(states_applied=["Anulado"], state_scope="next_move", nullify=True)

    return fn


def _cabezazo():
    def fn(att, riv):
        dmg = random.randint(10, 20)
        riv.take_damage(dmg)
        att.take_damage(2)
        return SkillResult(damage=dmg, self_damage=2)

    return fn


def get_brainrot():
    base = "assets/animations/Tung_Tung_Sahur"
    return Brainrot(
        name="Tung Tung Sahur",
        max_hp=100,
        max_energy=100,
        lore_text="Forjado entre fábricas, humo y lucha de clases.",
        portrait_img=f"{base}/portrait.png",
        idle_anim={"file_root": f"{base}/idle", "fps": 6},
        skills=[
            Skill(
                name="Palazo",
                description="Ataque 4-8 PV.",
                energy_cost=3,
                execute=deal_damage(4, 8),
                animation={
                    "file_root": f"{base}/palazo",
                    "fps": 5,
                    "hit_start": 6,
                    "hit_end": 7,
                },
            ),
            Skill(
                name="Palo Borracho",
                description="Muralla total y reflejo 2-5 PV.",
                energy_cost=15,
                execute=_palo_borracho(),
                priority=True,
                is_direct_attack=False,
                is_defense=True,
                animation={
                    "file_root": f"{base}/palo_borracho",
                    "fps": 6,
                },
            ),
            Skill(
                name="Cabezazo",
                description="Golpe 10-20 PV, +2 PV al usuario.",
                energy_cost=8,
                execute=_cabezazo(),
                animation={
                    "file_root": f"{base}/cabezazo",
                    "fps": 8,
                    "movement": True,
                    "collision": True,
                    "hit_start": 8,
                    "hit_end": 9,
                },
            ),
            Skill(
                name="Palo Santo",
                description="Daño 5-10 PV y Veneno.",
                energy_cost=25,
                execute=deal_damage_with_status(5, 10, Veneno),
                is_direct_attack=False,
                animation={
                    "file_root": f"{base}/palo_santo",
                    "fps": 6,
                    "hit_start": 7,
                    "hit_end": 10,
                },
            ),
        ],
    )