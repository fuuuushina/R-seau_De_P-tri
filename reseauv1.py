# Classes de base pour réseau de Petri
class Place:
    def __init__(self, name, tokens=0):
        self.name = name
        self.tokens = tokens

    def __str__(self):
        return f"{self.name} [{self.tokens}]"

class Transition:
    def __init__(self, name):
        self.name = name
        self.input_places = []
        self.output_places = []

    def add_input(self, place):
        self.input_places.append(place)

    def add_output(self, place):
        self.output_places.append(place)

    def is_enabled(self):
        return all(p.tokens > 0 for p in self.input_places)

    def fire(self):
        if not self.is_enabled():
            print(f"Transition {self.name} non activée")
            return False
        for p in self.input_places:
            p.tokens -= 1
        for p in self.output_places:
            p.tokens += 1
        print(f"Transition {self.name} activée")
        return True

# Création des places (compétences et qualités personnelles)
places_qualites = [
    Place("observation"),
    Place("émerveillement"),
    Place("curiosité"),
    Place("communication"),
    Place("créativité"),
    Place("ouverture"),
    Place("technique"),
    Place("ouverture d'esprit"),
    Place("empathie"),
    Place("synthèse"),
    Place("analyse"),
    Place("liberté"),
    Place("spontanéité"),
    Place("précision")
]

# Ajoutons les étapes (rectangles centraux du schéma)
p_redef = Place("(re)définir le cahier des charges")
p_problem = Place("problématiser")
p_innover = Place("innover")
p_realiser = Place("réaliser")
p_presenter = Place("présenter")

# Place finale
p_finale = Place("ingénieur designer accomplit")

# Création des transitions (correspondant aux flèches du schéma, entre compétences et étapes)
# Pour chaque qualité, créer une transition vers l'étape concernée :
def link_quality_to_step(quality, step):
    t = Transition(f"{quality.name} -> {step.name}")
    t.add_input(quality)
    t.add_output(step)
    return t

transitions = []
# Suivant schéma : associer chaque qualité à chaque étape correspondante (flèches)
qualites_p1 = ["observation", "émerveillement", "curiosité", "communication", "créativité", "ouverture", "technique", "ouverture d'esprit"]
qualites_p2 = ["communication", "empathie", "synthèse", "analyse", "ouverture d'esprit"]
qualites_p3 = ["créativité", "liberté", "spontanéité", "synthèse", "analyse", "ouverture d'esprit"]
qualites_p4 = ["technique", "précision", "analyse"]
qualites_p5 = ["communication", "synthèse", "précision", "ouverture d'esprit"]

name_to_place = {p.name: p for p in places_qualites}

for q in qualites_p1:
    transitions.append(link_quality_to_step(name_to_place[q], p_redef))
for q in qualites_p2:
    transitions.append(link_quality_to_step(name_to_place[q], p_problem))
for q in qualites_p3:
    transitions.append(link_quality_to_step(name_to_place[q], p_innover))
for q in qualites_p4:
    transitions.append(link_quality_to_step(name_to_place[q], p_realiser))
for q in qualites_p5:
    transitions.append(link_quality_to_step(name_to_place[q], p_presenter))

# Transitions entre étapes (verticales dans le schéma)
def link_step_to_step(input_step, output_step):
    t = Transition(f"{input_step.name} -> {output_step.name}")
    t.add_input(input_step)
    t.add_output(output_step)
    return t

transitions.append(link_step_to_step(p_redef, p_problem))
transitions.append(link_step_to_step(p_problem, p_innover))
transitions.append(link_step_to_step(p_innover, p_realiser))
transitions.append(link_step_to_step(p_realiser, p_presenter))
transitions.append(link_step_to_step(p_presenter, p_finale))

# Exemple d’affichage du marquage initial
print("Marquage initial :")
for place in places_qualites + [p_redef, p_problem, p_innover, p_realiser, p_presenter, p_finale]:
    print(place)
