from tkinter import *

# ----------------------------------
# Variables globales pour le dessin
# ----------------------------------
places_nouvelles = 0     # compteur de places
places = []              # liste des places dessinées (pile LIFO)

transitions_nouvelles = 0
transitions = []


# ----------------------------------
# Fenêtre Tkinter
# ----------------------------------
root = Tk()
root.title("Réseau de Petri INGÉNIEUR DESIGNER")

controls = Frame(root, padx=20, pady=70, bg="#e4dde9")
controls.pack(side=RIGHT, fill=Y)

Label(controls, text="CONTROLE DE JETONS", bg="#e4dde9",
      font=("Montserrat", 15)).pack(pady=5)

canvas = Canvas(root, width=900, height=800, bg="white")
canvas.pack()


# ----------------------------------
# Classe du graphe
# ----------------------------------
class graph_dictionnaire:
    def __init__(self):
        self.graph = {}

    def ajouter_place(self, jetons=0):
        global places_nouvelles, places
        places_nouvelles += 1

        # nom automatique de la place : P1, P2, P3...
        nom_place = f"P{places_nouvelles}"

        # 1) structure logique
        self.graph[nom_place] = {
            "jetons": jetons,
            "transitions": [],
            "text_jeton": None
        }

        # 2) dessin sur le canvas
        x = 150 + (places_nouvelles * 120)
        y = 500

        oval = canvas.create_oval(x - 40, y - 40, x + 40, y + 40, width=2)
        text_jeton = canvas.create_text(x, y, text=str(jetons),
                                        font=("Montserrat", 14))

        # on mémorise l'id du texte dans le graphe
        self.graph[nom_place]["text_jeton"] = text_jeton

        # on mémorise ce qu'on a dessiné + le nom
        places.append({
            "nom": nom_place,
            "oval": oval,
            "text_jeton": text_jeton
        })

    def retirer_place(self):
        global places_nouvelles, places

        if places:
            p = places.pop()
            nom_place = p["nom"]
            oval = p["oval"]
            text_jeton = p["text_jeton"]

            # 1) suppression graphique
            canvas.delete(oval)
            canvas.delete(text_jeton)

            # 2) suppression logique
            if nom_place in self.graph:
                del self.graph[nom_place]

            # 3) décrémenter le compteur
            places_nouvelles -= 1

    def ajouter_transition(self, cout=1):
        global transitions_nouvelles, transitions
        transitions_nouvelles += 1

        nom_transition = f"T{transitions_nouvelles}"

        # structure du graphe
        if nom_transition not in self.graph:
            self.graph[nom_transition] = {
                "type": "transition",
                "entrantes": [],
                "sortantes": [],
                "cout": cout
            }

        # dessin sur canvas
        x = 200 + (transitions_nouvelles * 60)
        y = 650

        rectangle = canvas.create_rectangle(x - 10, y - 40, x + 10, y + 40,
                                            width=2, fill="black")
        texte = canvas.create_text(x, y + 60, text=nom_transition,
                                   font=("Montserrat", 12))

        transitions.append({
            "nom": nom_transition,
            "rectangle": rectangle,
            "texte": texte
        })

    def retirer_transition(self):
        global transitions_nouvelles, transitions
        if transitions:
            t = transitions.pop()
            rectangle = t["rectangle"]
            texte = t["texte"]
            nom_transition = t["nom"]

            # suppression graphique
            canvas.delete(rectangle)
            canvas.delete(texte)

            # suppression logique
            if nom_transition in self.graph:
                del self.graph[nom_transition]

            transitions_nouvelles -= 1

    def ajouter_arc(self, place, transition):
        if place in self.graph and transition in self.graph:
            # côté place
            if "transitions" in self.graph[place]:
                self.graph[place]["transitions"].append(transition)
            # côté transition
            if "entrantes" in self.graph[transition]:
                self.graph[transition]["entrantes"].append(place)

    def supprimer_arc(self, place, transition):
        if place in self.graph and transition in self.graph:
            # côté place
            if "transitions" in self.graph[place]:
                if transition in self.graph[place]["transitions"]:
                    self.graph[place]["transitions"].remove(transition)
            # côté transition
            if "entrantes" in self.graph[transition]:
                if place in self.graph[transition]["entrantes"]:
                    self.graph[transition]["entrantes"].remove(place)

    def ajouter_jeton(self, nom_place):
        if nom_place in self.graph:
            self.graph[nom_place]["jetons"] += 1
            nb = self.graph[nom_place]["jetons"]
            text_id = self.graph[nom_place]["text_jeton"]
            canvas.itemconfig(text_id, text=str(nb))

    def retirer_jeton(self, nom_place):
        if nom_place in self.graph and self.graph[nom_place]["jetons"] > 0:
            self.graph[nom_place]["jetons"] -= 1
            nb = self.graph[nom_place]["jetons"]
            text_id = self.graph[nom_place]["text_jeton"]
            canvas.itemconfig(text_id, text=str(nb))


# instance du graphe
graph = graph_dictionnaire()


# ----------------------------------
# Fonctions UI pour les boutons
# ----------------------------------
def ui_ajouter_place():
    graph.ajouter_place()


def ui_retirer_place():
    graph.retirer_place()


def ui_ajouter_transition():
    graph.ajouter_transition()


def ui_retirer_transition():
    graph.retirer_transition()


def ui_ajouter_jeton_derniere_place():
    if places:
        nom = places[-1]["nom"]
        graph.ajouter_jeton(nom)


def ui_retirer_jeton_derniere_place():
    if places:
        nom = places[-1]["nom"]
        graph.retirer_jeton(nom)


# ----------------------------------
# Boutons de contrôle
# ----------------------------------
Button(controls, text="+ Ajouter un jeton",
       command=ui_ajouter_jeton_derniere_place).pack(pady=10)
Button(controls, text="- Retirer un jeton",
       command=ui_retirer_jeton_derniere_place).pack(pady=10)

Label(controls, text="Édition du réseau", bg="#e4dde9",
      font=("Montserrat", 13)).pack(pady=20)

Button(controls, text="Ajouter une place",
       command=ui_ajouter_place).pack(pady=15)
Button(controls, text="Retirer une place",
       command=ui_retirer_place).pack(pady=15)
Button(controls, text="Ajouter une transition",
       command=ui_ajouter_transition).pack(pady=8)
Button(controls, text="Retirer une transition",
       command=ui_retirer_transition).pack(pady=8)

root.mainloop()
