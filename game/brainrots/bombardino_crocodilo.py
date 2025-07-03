from game.brainrot import Brainrot
from game.skill import Skill
from game.skill_result import SkillResult
from game.skill_effects import (
    deal_damage,
    deal_damage_with_status_both,
    weaken_next_attack,
    extra_energy_cost,
)
from game.status_effects import Radiacion


def _ventarron():
    wk = weaken_next_attack(0.5)
    ec = extra_energy_cost(1.25)

    def fn(att, riv):
        res1 = wk(att, riv)
        res2 = ec(att, riv)
        merged = (res1.states_applied or []) + (res2.states_applied or [])
        return SkillResult(states_applied=merged, state_scope="next_move")

    return fn


def get_brainrot():
    base = "assets/animations/Bombardino_Crocodilo"
    return Brainrot(
        name="Bombardino Crocodilo",
        max_hp=100,
        max_energy=100,
        lore_text="Bestia anfibia de explosivos acordes.",
        portrait_img=f"{base}/portrait.png",
        idle_anim={"file_root": f"{base}/idle", "fps": 5},
        skills=[
            Skill(
                name="Masticada",
                description="Ataque 5-15 PV.",
                energy_cost=5,
                execute=deal_damage(5, 15),
                animation={
                    "file_root": f"{base}/masticada",
                    "fps": 8,
                    "movement": True,
                    "collision": True,
                    "hit_start": 4,
                    "hit_end": 5,
                },
            ),
            Skill(
                name="Ventarrón",
                description="Rival –50 % daño y +25 % PP.",
                energy_cost=15,
                execute=_ventarron(),
                priority=True,
                is_direct_attack=False,
                is_defense=True,
                animation={
                    "file_root": f"{base}/ventarron",
                    "fps": 6,
                },
            ),
            Skill(
                name="Bombazo",
                description="Daño 15-25 PV.",
                energy_cost=10,
                execute=deal_damage(15, 25),
                animation={
                    "file_root": f"{base}/bombazo",
                    "fps": 6,
                    "movement": True,
                    "collision": True,
                    "hit_start": 6,
                    "hit_end": 8,
                },
            ),
            Skill(
                name="Crocomisil",
                description="Golpe 40-50 PV y Radiación a ambos.",
                energy_cost=25,
                execute=deal_damage_with_status_both(40, 50, Radiacion),
                is_direct_attack=False,
                animation={
                    "file_root": f"{base}/crocomisil",
                    "fps": 7,
                    "movement": True,
                    "collision": True,
                    "hit_start": 13,
                    "hit_end": 18,
                },
            ),
        ],
    )