import random
from game.brainrot import Brainrot
from game.skill import Skill
from game.skill_result import SkillResult
from game.skill_effects import (
    deal_damage,
    raise_defense_nullify,
    drain_energy,
)


def _patapum():
    def fn(att, riv):
        dmg = random.randint(15, 20)
        riv.take_damage(dmg)
        riv.pending_effects["damage_mod"] = 0.8
        return SkillResult(damage=dmg, states_applied=["Debilitado 20%"], state_scope="next_move")

    return fn


def get_brainrot():
    base = "assets/animations/Br_Br_Patapim"
    return Brainrot(
        name="Br Br Patapim",
        max_hp=100,
        max_energy=100,
        lore_text="Destructor de ritmos y tamborines, trae caos con cada golpe.",
        portrait_img=f"{base}/portrait.png",
        idle_anim={"file_root": f"{base}/idle", "fps": 6},
        skills=[
            Skill(
                name="Patapimba",
                description="Ataque 10-15 PV.",
                energy_cost=15,
                execute=deal_damage(10, 15),
                animation={
                    "file_root": f"{base}/patapimba",
                    "fps": 8,
                    "movement": True,
                    "collision": True,
                    "hit_start": 7,
                    "hit_end": 10,
                },
            ),
            Skill(
                name="Arbustote",
                description="Muralla que anula el próximo golpe.",
                energy_cost=25,
                execute=raise_defense_nullify(),
                priority=True,
                is_direct_attack=False,
                is_defense=True,
                animation={
                    "file_root": f"{base}/arbustote",
                    "fps": 5,
                },
            ),
            Skill(
                name="Patapum",
                description="Daño 15-20 PV y rival -20 % daño próximo.",
                energy_cost=20,
                execute=_patapum(),
                animation={
                    "file_root": f"{base}/patapum",
                    "fps": 7,
                    "movement": True,
                    "collision": True,
                    "hit_start": 5,
                    "hit_end": 7,
                },
            ),
            Skill(
                name="Drenaje Vital",
                description="Roba 10 PP al rival.",
                energy_cost=0,
                execute=drain_energy(10),
                is_direct_attack=False,
                animation={
                    "file_root": f"{base}/drenaje_vital",
                    "fps": 6,
                },
            ),
        ],
    )