from game.brainrot import Brainrot
from game.skill import Skill
from game.skill_result import SkillResult
from game.skill_effects import (
    deal_damage,
    weaken_next_attack,
    extra_energy_cost,
)


def _arenas_movedizas():
    wk = weaken_next_attack(0.5)
    ec = extra_energy_cost(1.25)

    def fn(att, riv):
        res1 = wk(att, riv)
        res2 = ec(att, riv)
        merged = (res1.states_applied or []) + (res2.states_applied or [])
        return SkillResult(states_applied=merged, state_scope="next_move")

    return fn


def _volver_al_pasado():
    def fn(att, _):
        gained = att.restore_energy(att.last_energy_lost)
        return SkillResult(pp_steal=-gained)

    return fn


def get_brainrot():
    base = "assets/animations/Lirili_Larila"
    return Brainrot(
        name="Lirili Larila",
        max_hp=100,
        max_energy=100,
        lore_text="Criatura melódica que encanta y aturde con su ritmo.",
        portrait_img=f"{base}/portrait.png",
        idle_anim={"file_root": f"{base}/idle", "fps": 5},
        skills=[
            Skill(
                name="Patadón",
                description="Ataque 5-10 PV.",
                energy_cost=5,
                execute=deal_damage(5, 10),
                animation={
                    "file_root": f"{base}/patadon",
                    "fps": 7,
                    "movement": True,
                    "collision": True,
                    "hit_start": 4,
                    "hit_end": 6,
                },
            ),
            Skill(
                name="Arenas Movedizas",
                description="Próx. ataque rival –50 % daño y +25 % PP.",
                energy_cost=20,
                execute=_arenas_movedizas(),
                priority=True,
                is_direct_attack=False,
                is_defense=True,
                animation={
                    "file_root": f"{base}/arenas_movedizas",
                    "fps": 6,
                },
            ),
            Skill(
                name="Bomba de Espinas",
                description="Daño 20-25 PV.",
                energy_cost=15,
                execute=deal_damage(20, 25),
                animation={
                    "file_root": f"{base}/bomba_de_espinas",
                    "fps": 6,
                    "movement": True,
                    "collision": True,
                    "hit_start": 10,
                    "hit_end": 11,
                },
            ),
            Skill(
                name="Volver al Pasado",
                description="Recupera toda la energía perdida en el último golpe.",
                energy_cost=30,
                execute=_volver_al_pasado(),
                is_direct_attack=False,
                animation={
                    "file_root": f"{base}/volver_al_pasado",
                    "fps": 5,
                },
            ),
        ],
    )