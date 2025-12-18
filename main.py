from tkinter import *
from tkinter import simpledialog, messagebox
from collections import deque
import time

# ----------------------------------
# Variables globales
# ----------------------------------
places_nouvelles = 0
places = []
transitions_nouvelles = 0
transitions = []
selected_node = None
dragging_node = None
drag_dx = 0
drag_dy = 0
arc_start_node = None

# ----------------------------------
# Fenêtre Tkinter
# ----------------------------------
root = Tk()
root.title("Réseau de Petri INGÉNIEUR DESIGNER")
controls = Frame(root, padx=20, pady=70, bg="#e4dde9")
controls.pack(side=RIGHT, fill=Y)
Label(controls, text="CONTROLE DE JETONS", bg="#e4dde9", font=("Montserrat", 15)).pack(pady=5)
canvas = Canvas(root, width=900, height=800, bg="white")
canvas.pack()

# ----------------------------------
# Classe du graphe
# ----------------------------------
class graph_dictionnaire:
    def __init__(self):
        self.graph = {}
        self.item_to_node = {}
        self.arcs = []

    # ---------- PLACES ----------
    def ajouter_place(self, jetons=0):
        global places_nouvelles, places
        places_nouvelles += 1
        nom_place = f"P{places_nouvelles}"
        self.graph[nom_place] = {
            "type": "place",
            "x": 150 + (places_nouvelles * 120),
            "y": 500,
            "jetons": jetons,
            "transitions": [],
            "oval": None,
            "text_jeton": None,
            "text_nom": None
        }
        x = self.graph[nom_place]["x"]
        y = self.graph[nom_place]["y"]
        oval = canvas.create_oval(x - 40, y - 40, x + 40, y + 40, width=2)
        text_jeton = canvas.create_text(x, y, text=str(jetons), font=("Montserrat", 14))
        text_nom = canvas.create_text(x, y + 60, text=nom_place, font=("Montserrat", 12))
        self.graph[nom_place]["oval"] = oval
        self.graph[nom_place]["text_jeton"] = text_jeton
        self.graph[nom_place]["text_nom"] = text_nom
        self.item_to_node[oval] = nom_place
        self.item_to_node[text_jeton] = nom_place
        self.item_to_node[text_nom] = nom_place
        places.append({"nom": nom_place, "oval": oval, "text_jeton": text_jeton, "text_nom": text_nom})

    def retirer_place(self):
        global places_nouvelles, places
        if places:
            p = places.pop()
            nom_place = p["nom"]
            oval = p["oval"]
            text_jeton = p["text_jeton"]
            text_nom = p["text_nom"]
            self._supprimer_arcs_du_noeud(nom_place)
            canvas.delete(oval)
            canvas.delete(text_jeton)
            canvas.delete(text_nom)
            for item in [oval, text_jeton, text_nom]:
                if item in self.item_to_node: del self.item_to_node[item]
            if nom_place in self.graph: del self.graph[nom_place]
            places_nouvelles -= 1

    # ---------- TRANSITIONS ----------
    def ajouter_transition(self):
        global transitions_nouvelles, transitions
        transitions_nouvelles += 1
        nom_transition = f"T{transitions_nouvelles}"
        if nom_transition not in self.graph:
            x = 200 + (transitions_nouvelles * 60)
            y = 650
            self.graph[nom_transition] = {
                "type": "transition",
                "x": x,
                "y": y,
                "entrantes": [],
                "sortantes": [],
                "rectangle": None,
                "text_nom": None
            }
        x = self.graph[nom_transition]["x"]
        y = self.graph[nom_transition]["y"]
        rect = canvas.create_rectangle(x - 10, y - 40, x + 10, y + 40, width=2, fill="black")
        text_nom = canvas.create_text(x, y + 60, text=nom_transition, font=("Montserrat", 12))
        self.graph[nom_transition]["rectangle"] = rect
        self.graph[nom_transition]["text_nom"] = text_nom
        self.item_to_node[rect] = nom_transition
        self.item_to_node[text_nom] = nom_transition
        transitions.append({"nom": nom_transition, "rectangle": rect, "text_nom": text_nom})

    def retirer_transition(self):
        global transitions_nouvelles, transitions
        if transitions:
            t = transitions.pop()
            nom_transition = t["nom"]
            for item in [t["rectangle"], t["text_nom"]]:
                canvas.delete(item)
                if item in self.item_to_node: del self.item_to_node[item]
            self._supprimer_arcs_du_noeud(nom_transition)
            if nom_transition in self.graph: del self.graph[nom_transition]
            transitions_nouvelles -= 1

    # ---------- ARCS ----------
    def ajouter_arc(self, noeud1, noeud2):
        if noeud1 not in self.graph or noeud2 not in self.graph: return
        type1, type2 = self.graph[noeud1]["type"], self.graph[noeud2]["type"]
        if type1 == type2: return

        # Demander le poids
        poids = simpledialog.askinteger("Poids arc", f"Poids de l'arc {noeud1} -> {noeud2} :", initialvalue=1, minvalue=1)
        if poids is None: poids = 1

        if type1 == "place" and type2 == "transition":
            place, transition = noeud1, noeud2
            if transition not in self.graph[place]["transitions"]: self.graph[place]["transitions"].append(transition)
            if place not in self.graph[transition]["entrantes"]: self.graph[transition]["entrantes"].append(place)
        elif type1 == "transition" and type2 == "place":
            transition, place = noeud1, noeud2
            if place not in self.graph[transition]["sortantes"]: self.graph[transition]["sortantes"].append(place)

        x1, y1 = self.graph[noeud1]["x"], self.graph[noeud1]["y"]
        x2, y2 = self.graph[noeud2]["x"], self.graph[noeud2]["y"]
        line = canvas.create_line(x1, y1, x2, y2, arrow=LAST, width=2)
        self.arcs.append({"from": noeud1, "to": noeud2, "line": line, "poids": poids})

    def _supprimer_arcs_du_noeud(self, nom_noeud):
        new_arcs = []
        for arc in self.arcs:
            if arc["from"] == nom_noeud or arc["to"] == nom_noeud:
                canvas.delete(arc["line"])
            else:
                new_arcs.append(arc)
        self.arcs = new_arcs
        for nom, data in self.graph.items():
            if data["type"] == "place": data["transitions"] = [t for t in data.get("transitions", []) if t != nom_noeud]
            elif data["type"] == "transition":
                data["entrantes"] = [p for p in data.get("entrantes", []) if p != nom_noeud]
                data["sortantes"] = [p for p in data.get("sortantes", []) if p != nom_noeud]

    def update_arcs_for_node(self, nom_noeud):
        if nom_noeud not in self.graph: return
        for arc in self.arcs:
            n_from, n_to, line = arc["from"], arc["to"], arc["line"]
            x1, y1 = self.graph[n_from]["x"], self.graph[n_from]["y"]
            x2, y2 = self.graph[n_to]["x"], self.graph[n_to]["y"]
            canvas.coords(line, x1, y1, x2, y2)

    # ---------- JETONS ----------
    def ajouter_jeton(self, nom_place):
        if nom_place in self.graph and self.graph[nom_place]["type"] == "place":
            self.graph[nom_place]["jetons"] += 1
            canvas.itemconfig(self.graph[nom_place]["text_jeton"], text=str(self.graph[nom_place]["jetons"]))

    def retirer_jeton(self, nom_place):
        if nom_place in self.graph and self.graph[nom_place]["type"] == "place":
            if self.graph[nom_place]["jetons"] > 0: self.graph[nom_place]["jetons"] -= 1
            canvas.itemconfig(self.graph[nom_place]["text_jeton"], text=str(self.graph[nom_place]["jetons"]))

    # ---------- RENOMMAGE ----------
    def renommer_noeud_visuel(self, nom_noeud, nouveau_texte):
        if nom_noeud not in self.graph: return
        canvas.itemconfig(self.graph[nom_noeud]["text_nom"], text=nouveau_texte)

    # ---------- TIRER TRANSITION ----------
    def tirer_transition(self, nom_transition):
        if nom_transition not in self.graph: return False
        t = self.graph[nom_transition]
        if t["type"] != "transition": return False

        # Vérifier jetons entrantes selon poids
        for p in t.get("entrantes", []):
            arc = next((a for a in self.arcs if a["from"] == p and a["to"] == nom_transition), None)
            if arc and self.graph[p]["jetons"] < arc["poids"]:
                messagebox.showinfo("Impossible", f"Transition {nom_transition} ne peut pas être tirée (place {p} manque de jetons)")
                return False

        # Retirer jetons des entrantes
        for p in t.get("entrantes", []):
            arc = next((a for a in self.arcs if a["from"] == p and a["to"] == nom_transition), None)
            if arc:
                self.graph[p]["jetons"] -= arc["poids"]
                canvas.itemconfig(self.graph[p]["text_jeton"], text=str(self.graph[p]["jetons"]))

        # Ajouter jetons aux sortantes
        for p in t.get("sortantes", []):
            arc = next((a for a in self.arcs if a["from"] == nom_transition and a["to"] == p), None)
            if arc:
                self.graph[p]["jetons"] += arc["poids"]
                canvas.itemconfig(self.graph[p]["text_jeton"], text=str(self.graph[p]["jetons"]))

        return True

# ----------------------------------
# Instance graphe
# ----------------------------------
graph = graph_dictionnaire()

# ----------------------------------
# Fonctions UI
# ----------------------------------
def ui_ajouter_place(): graph.ajouter_place()
def ui_retirer_place(): graph.retirer_place()
def ui_ajouter_transition(): graph.ajouter_transition()
def ui_retirer_transition(): graph.retirer_transition()
def ui_ajouter_jeton_derniere_place():
    if places: graph.ajouter_jeton(selected_node)
def ui_retirer_jeton_derniere_place():
    if places: graph.retirer_jeton(selected_node)
def ui_ajouter_arc_depuis_inputs():
    src, dst = entry_arc_from.get().strip(), entry_arc_to.get().strip()
    if src and dst: graph.ajouter_arc(src, dst)
def ui_tirer_transition():
    if not transitions: return
    noms = [t["nom"] for t in transitions]
    nom_transition = simpledialog.askstring("Tirer Transition", f"Nom de la transition à tirer:\nDisponibles: {', '.join(noms)}")
    if nom_transition: graph.tirer_transition(nom_transition)

# ----------------------------------
# Gestion des événements souris
# ----------------------------------
def on_left_press(event):
    global dragging_node, selected_node, drag_dx, drag_dy
    items = canvas.find_closest(event.x, event.y)
    if not items: dragging_node = selected_node = None; return
    item = items[0]
    if item in graph.item_to_node:
        node = graph.item_to_node[item]
        selected_node = dragging_node = node
        data = graph.graph[node]
        drag_dx = event.x - data["x"]
        drag_dy = event.y - data["y"]
    else: dragging_node = selected_node = None

def on_left_drag(event):
    global dragging_node
    if not dragging_node: return
    node = dragging_node
    data = graph.graph[node]
    x, y = event.x - drag_dx, event.y - drag_dy
    data["x"], data["y"] = x, y
    if data["type"] == "place":
        canvas.coords(data["oval"], x-40, y-40, x+40, y+40)
        canvas.coords(data["text_jeton"], x, y)
        canvas.coords(data["text_nom"], x, y+60)
    elif data["type"] == "transition":
        canvas.coords(data["rectangle"], x-10, y-40, x+10, y+40)
        canvas.coords(data["text_nom"], x, y+60)
    graph.update_arcs_for_node(node)

def on_left_release(event): global dragging_node; dragging_node = None

def on_right_click(event):
    global arc_start_node
    items = canvas.find_closest(event.x, event.y)
    if not items: return
    item = items[0]
    if item not in graph.item_to_node: return
    node = graph.item_to_node[item]
    if arc_start_node is None: arc_start_node = node; print("Départ arc :", node)
    else:
        if node != arc_start_node: graph.ajouter_arc(arc_start_node, node); print("Arc créé :", arc_start_node, "->", node)
        arc_start_node = None

def on_double_click(event):
    items = canvas.find_closest(event.x, event.y)
    if not items: return
    item = items[0]
    if item in graph.item_to_node:
        node = graph.item_to_node[item]
        data = graph.graph[node]
        if data["type"] == "place":
            new_name = simpledialog.askstring("Modifier Place", "Nom :", initialvalue=canvas.itemcget(data["text_nom"], "text"))
            if new_name: graph.renommer_noeud_visuel(node, new_name)
            new_tokens = simpledialog.askinteger("Modifier Place", "Nombre de jetons :", initialvalue=data["jetons"], minvalue=0)
            if new_tokens is not None:
                data["jetons"] = new_tokens
                canvas.itemconfig(data["text_jeton"], text=str(new_tokens))
        elif data["type"] == "transition":
            new_name = simpledialog.askstring("Modifier Transition", "Nom :", initialvalue=canvas.itemcget(data["text_nom"], "text"))
            if new_name: graph.renommer_noeud_visuel(node, new_name)
    else:
        for arc in graph.arcs:
            if arc["line"] == item:
                new_poids = simpledialog.askinteger("Modifier arc", "Poids de l'arc :", initialvalue=arc["poids"], minvalue=1)
                if new_poids is not None:
                    arc["poids"] = new_poids
                break

# Bind événements
canvas.bind("<Button-1>", on_left_press)
canvas.bind("<B1-Motion>", on_left_drag)
canvas.bind("<ButtonRelease-1>", on_left_release)
canvas.bind("<Button-3>", on_right_click)
canvas.bind("<Double-Button-1>", on_double_click)

# ----------------------------------
# Boutons de contrôle
# ----------------------------------
Button(controls, text="+ Ajouter un jeton", command=ui_ajouter_jeton_derniere_place).pack(pady=10)
Button(controls, text="- Retirer un jeton", command=ui_retirer_jeton_derniere_place).pack(pady=10)
Label(controls, text="Édition du réseau", bg="#e4dde9", font=("Montserrat", 13)).pack(pady=20)
Button(controls, text="Ajouter une place", command=ui_ajouter_place).pack(pady=15)
Button(controls, text="Retirer une place", command=ui_retirer_place).pack(pady=15)
Button(controls, text="Ajouter une transition", command=ui_ajouter_transition).pack(pady=8)
Button(controls, text="Retirer une transition", command=ui_retirer_transition).pack(pady=8)
Button(controls, text="Tirer une transition", command=ui_tirer_transition).pack(pady=10)
Label(controls, text="Créer un arc (nom -> nom)", bg="#e4dde9", font=("Montserrat", 11)).pack(pady=10)
entry_arc_from = Entry(controls); entry_arc_from.pack(pady=2); entry_arc_from.insert(0,"P1")
entry_arc_to = Entry(controls); entry_arc_to.pack(pady=2); entry_arc_to.insert(0,"T1")
Button(controls, text="Ajouter arc", command=ui_ajouter_arc_depuis_inputs).pack(pady=5)

#bontons dfs et bfs
Label(controls, text="Exploration du graph", bg="#e4dde9", font=("Montserrat", 13)).pack(pady=20)
dfs_button = Button(controls, text="DFS", command=lambda: dfs_algo(selected_node)).pack(pady=5)
bfs_button = Button(controls, text="BFS", command=lambda: bfs_algo(selected_node)).pack(pady=5)



# Fonction pour colorer les noeuds visités
def color_node(nom_noeud, couleur="yellow"):
    if nom_noeud not in graph.graph:
        return
    data = graph.graph[nom_noeud]
    if data["type"] == "place":
        canvas.itemconfig(data["oval"], fill=couleur)
    elif data["type"] == "transition":
        canvas.itemconfig(data["rectangle"], fill=couleur)
    canvas.update()
    time.sleep(0.4)


# dfs
def dfs_algo(start):
    visited = set()

    def dfs(nom_noeud):
        visited.add(nom_noeud)
        color_node(nom_noeud)

        data = graph.graph[nom_noeud]

        if data["type"] == "place":
            neighbors = data["transitions"]
        elif data["type"] == "transition":
            neighbors = data["sortantes"]

        for neighbor in neighbors:
            if neighbor not in visited:
                dfs(neighbor)

    dfs(start)

# bfs
def bfs_algo(start):
    visited = set()
    queue = deque([start])
    visited.add(start)

    while queue:
        nom_noeud = queue.popleft()
        color_node(nom_noeud, "orange")

        data = graph.graph[nom_noeud]

        if data["type"] == "place":
            neighbors = data["transitions"]
        elif data["type"] == "transition":
            neighbors = data["sortantes"]

        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

root.mainloop()