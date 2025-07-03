from game.brainrot import Brainrot
from game.skill import Skill
from game.skill_effects import (
    deal_damage,
    deal_damage_with_status,
    weaken_next_attack,
)
from game.status_effects import Mojado


def get_brainrot():
    base = "assets/animations/Tralalero_Tralala"
    return Brainrot(
        name="Tralalero Tralala",
        max_hp=100,
        max_energy=100,
        lore_text="Híbrido entre cantante de ópera y surfista de cloacas.",
        portrait_img=f"{base}/portrait.png",
        idle_anim={"file_root": f"{base}/idle", "fps": 5},
        skills=[
            Skill(
                name="Altas Llantas",
                description="Ataque 5-10 PV.",
                energy_cost=5,
                execute=deal_damage(5, 10),
                animation={
                    "file_root": f"{base}/altas_llantas",
                    "fps": 6,
                    "hit_start": 5,
                    "hit_end": 7,
                },
            ),
            Skill(
                name="Piel de Tiburón",
                description="Próximo ataque rival a 25 %.",
                energy_cost=20,
                execute=weaken_next_attack(0.25),
                priority=True,
                is_direct_attack=False,
                is_defense=True,
                animation={
                    "file_root": f"{base}/piel_de_tiburon",
                    "fps": 6,
                },
            ),
            Skill(
                name="Chupetón",
                description="Mordida 10-20 PV.",
                energy_cost=10,
                execute=deal_damage(10, 20),
                animation={
                    "file_root": f"{base}/chupeton",
                    "fps": 7,
                    "collision": True,
                    "hit_start": 7,
                    "hit_end": 10,
                },
            ),
            Skill(
                name="Manguerazo",
                description="Daño 10-20 PV y Mojado.",
                energy_cost=25,
                execute=deal_damage_with_status(10, 20, Mojado),
                is_direct_attack=False,
                animation={
                    "file_root": f"{base}/manguerazo",
                    "fps": 8,
                    "movement": True,
                    "collision": True,
                    "hit_start": 8,
                    "hit_end": 10,
                },
            ),
        ],
    )