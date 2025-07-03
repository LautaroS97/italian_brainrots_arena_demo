import random
from game.brainrot import Brainrot
from game.skill import Skill
from game.skill_result import SkillResult
from game.skill_effects import deal_damage, deal_damage_with_status
from game.status_effects import Mareado


def _anillo_proteccion():
    def fn(att, _):
        lost_hp = att.max_hp - att.hp
        lost_pp = att.max_energy - att.energy
        heal_amt = int(lost_hp * 0.5)
        pp_gain = int(lost_pp * 0.5)
        att.heal(heal_amt)
        att.restore_energy(pp_gain)
        return SkillResult(self_damage=-heal_amt, pp_steal=-pp_gain)

    return fn


def _disco_acrecion():
    def fn(att, riv):
        dmg = random.randint(25, 30)
        riv.take_damage(dmg)
        att.take_damage(6)
        return SkillResult(damage=dmg, self_damage=6)

    return fn


def get_brainrot():
    base = "assets/animations/Vaca_Saturno_Saturnita"
    return Brainrot(
        name="Vaca Saturno Saturnita",
        max_hp=100,
        max_energy=100,
        lore_text="Una entidad cósmica de cuatro estómagos y una misión intergaláctica.",
        portrait_img=f"{base}/portrait.png",
        idle_anim={"file_root": f"{base}/idle", "fps": 4},
        skills=[
            Skill(
                name="Patadón",
                description="Ataque físico 5-10 PV.",
                energy_cost=5,
                execute=deal_damage(5, 10),
                animation={
                    "file_root": f"{base}/patadon",
                    "fps": 8,
                    "hit_start": 6,
                    "hit_end": 9,
                },
            ),
            Skill(
                name="Anillo de Protección",
                description="Recupera 50 % de PV y PP perdidos.",
                energy_cost=10,
                execute=_anillo_proteccion(),
                is_direct_attack=False,
                is_defense=True,
                animation={
                    "file_root": f"{base}/anillo_de_proteccion",
                    "fps": 6,
                },
            ),
            Skill(
                name="Disco de Acreción",
                description="Causa 25-30 PV y 6 PV al usuario.",
                energy_cost=18,
                execute=_disco_acrecion(),
                render_behind_rival=True,
                animation={
                    "file_root": f"{base}/disco_de_acrecion",
                    "fps": 5,
                    "hit_start": 6,
                    "hit_end": 8,
                },
            ),
            Skill(
                name="Polvo Estelar",
                description="Daño 6-18 PV y 'Mareado'.",
                energy_cost=25,
                execute=deal_damage_with_status(6, 18, Mareado),
                is_direct_attack=False,
                animation={
                    "file_root": f"{base}/polvo_estelar",
                    "fps": 6,
                    "hit_start": 6,
                    "hit_end": 8,
                },
            ),
        ],
    )