from tkinter import *
from tkinter import simpledialog
from collections import deque
import time
from tkinter import messagebox
from tkinter import colorchooser
import json
import math
from tkinter import filedialog




# Variables globales
places_nouvelles = 0
places = []
transitions_nouvelles = 0
transitions = []
selected_node = None
dragging_node = None
drag_dx = 0
drag_dy = 0
arc_start_node = None
COULEURS_JETONS = ["red", "blue", "green", "orange", "purple", "cyan"]



# Fenêtre Tkinter
root = Tk()
root.title("Réseau de Petri")

# Canvas principal pour le graphe
canvas = Canvas(root, width=900, height=800, bg="white")
canvas.pack(side=LEFT, fill=BOTH, expand=True)

# Canvas pour le panneau de contrôle avec scrollbar
controls_canvas = Canvas(root, width=300, bg="#e4dde9")
controls_canvas.pack(side=RIGHT, fill=Y, expand=False)

# Scrollbar verticale
scrollbar = Scrollbar(root, orient=VERTICAL, command=controls_canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)

controls_canvas.configure(yscrollcommand=scrollbar.set)

# Frame à l'intérieur du canvas pour placer tous les boutons
controls = Frame(controls_canvas, bg="#e4dde9")
controls_window = controls_canvas.create_window((0,0), window=controls, anchor="nw")

# Mettre à jour la zone scrollable à chaque changement de taille
def update_scrollregion(event=None):
    controls_canvas.update_idletasks()
    controls_canvas.configure(scrollregion=controls_canvas.bbox("all"))

controls.bind("<Configure>", update_scrollregion)

# Faire en sorte que le frame prenne la largeur du canvas
def resize_frame(event):
    canvas_width = event.width
    controls_canvas.itemconfig(controls_window, width=canvas_width)

controls_canvas.bind("<Configure>", resize_frame)

# Scroll avec la molette
def _on_mousewheel(event):
    controls_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
controls_canvas.bind_all("<MouseWheel>", _on_mousewheel)



# Titre du panneau
Label(controls, text="CONTROLE DE JETONS", bg="#e4dde9", font=("Montserrat", 15)).pack(pady=5)



# Classe du graphe
class graph_dictionnaire:
    def __init__(self):
        self.graph = {}
        self.item_to_node = {}
        self.arcs = []

    #PLACES
    def ajouter_place(self, jetons=0):
        global places_nouvelles, places
        places_nouvelles += 1
        nom_place = f"P{places_nouvelles}"
        self.graph[nom_place] = {
            "type": "place",
            "x": 150 + (places_nouvelles * 120),
            "y": 500,
            "jetons": jetons,
            "jetons_couleurs": ["red"] * jetons,   # ← AJOUT
            "jetons_visuels": [],
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

    def retirer_place(self, nom_place=None):
        global places_nouvelles, places
        if not places:
            return

        # Si aucun nom spécifié, supprimer la dernière
        if nom_place is None:
            p = places.pop()
        else:
            # trouver la place dans la liste
            for i, p_item in enumerate(places):
                if p_item["nom"] == nom_place:
                    p = places.pop(i)
                    break
            else:
                return  # place introuvable

        nom_place = p["nom"]
        oval = p["oval"]
        text_jeton = p["text_jeton"]
        text_nom = p["text_nom"]

        self._supprimer_arcs_du_noeud(nom_place)

        for item in [oval, text_jeton, text_nom]:
            canvas.delete(item)
            if item in self.item_to_node:
                del self.item_to_node[item]

        if nom_place in self.graph:
            del self.graph[nom_place]

        places_nouvelles -= 1

    #TRANSITIONS
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

    #ARCS
    def ajouter_arc(self, noeud1, noeud2):
        if noeud1 not in self.graph or noeud2 not in self.graph: return
        type1, type2 = self.graph[noeud1]["type"], self.graph[noeud2]["type"]
        if type1 == type2: return

        poids = simpledialog.askinteger("Poids arc", f"Poids de l'arc {noeud1} -> {noeud2} :", initialvalue=1,
                                        minvalue=1)
        if poids is None: poids = 1

        if type1 == "place" and type2 == "transition":
            place, transition = noeud1, noeud2
            if transition not in self.graph[place]["transitions"]:
                self.graph[place]["transitions"].append(transition)
            if place not in self.graph[transition]["entrantes"]:
                self.graph[transition]["entrantes"].append(place)
        elif type1 == "transition" and type2 == "place":
            transition, place = noeud1, noeud2
            if place not in self.graph[transition]["sortantes"]:
                self.graph[transition]["sortantes"].append(place)

        x1, y1 = self.graph[noeud1]["x"], self.graph[noeud1]["y"]
        x2, y2 = self.graph[noeud2]["x"], self.graph[noeud2]["y"]

       #décallage pour que la flèche soit pas au centre
        if type1 == "place":     # cercle rayon 40
            dx = x2 - x1
            dy = y2 - y1
            dist = math.sqrt(dx**2 + dy**2)
            if dist != 0:
                x1 += dx/dist * 40
                y1 += dy/dist * 40
        elif type1 == "transition":  # rectangle demi-hauteur 40
            dx = x2 - x1
            dy = y2 - y1
            dist = math.sqrt(dx**2 + dy**2)
            if dist != 0:
                x1 += dx/dist * 40
                y1 += dy/dist * 40

        if type2 == "place":
            dx = x1 - x2
            dy = y1 - y2
            dist = math.sqrt(dx**2 + dy**2)
            if dist != 0:
                x2 += dx/dist * 40
                y2 += dy/dist * 40
        elif type2 == "transition":
            dx = x1 - x2
            dy = y1 - y2
            dist = math.sqrt(dx**2 + dy**2)
            if dist != 0:
                x2 += dx/dist * 40
                y2 += dy/dist * 40
        # -------------------------------------------------------------------

        # Création de la ligne avec une pointe plus grande
        line = canvas.create_line(x1, y1, x2, y2, arrow=LAST, width=2, arrowshape=(16,20,6))
        self.arcs.append({"from": noeud1, "to": noeud2, "line": line, "poids": poids})



    def update_arcs_for_node(self, nom_noeud):
        if nom_noeud not in self.graph: return
        for arc in self.arcs:
            n_from, n_to, line = arc["from"], arc["to"], arc["line"]

            x1, y1 = self.graph[n_from]["x"], self.graph[n_from]["y"]
            x2, y2 = self.graph[n_to]["x"], self.graph[n_to]["y"]

            #Même décalage qu'à la création
            for i, t in [(n_from, n_to), (n_to, n_from)]:
                node_type = self.graph[i]["type"]
                dx = x2 - x1
                dy = y2 - y1
                dist = math.sqrt(dx**2 + dy**2)
                if dist != 0:
                    if i == n_from:
                        if node_type == "place": x1 += dx/dist*40; y1 += dy/dist*40
                        elif node_type == "transition": x1 += dx/dist*40; y1 += dy/dist*40
                    else:  # n_to
                        if node_type == "place": x2 -= dx/dist*40; y2 -= dy/dist*40
                        elif node_type == "transition": x2 -= dx/dist*40; y2 -= dy/dist*40
            # --------------------------------------

            canvas.coords(line, x1, y1, x2, y2)

    def _supprimer_arcs_du_noeud(self, nom_noeud):
        # Supprimer les arcs sur le canvas et de la liste
        arcs_a_supprimer = [arc for arc in self.arcs if arc["from"] == nom_noeud or arc["to"] == nom_noeud]
        for arc in arcs_a_supprimer:
            canvas.delete(arc["line"])
            self.arcs.remove(arc)

        # Supprimer les références dans le graphe
        if nom_noeud in self.graph:
            noeud = self.graph[nom_noeud]
            if noeud["type"] == "place":
                # Retirer ce noeud des entrantes des transitions
                for t in noeud.get("transitions", []):
                    if t in self.graph and "entrantes" in self.graph[t]:
                        if nom_noeud in self.graph[t]["entrantes"]:
                            self.graph[t]["entrantes"].remove(nom_noeud)
            elif noeud["type"] == "transition":
                # Retirer ce noeud des listes des places entrantes
                for p in noeud.get("entrantes", []):
                    if p in self.graph and "transitions" in self.graph[p]:
                        if nom_noeud in self.graph[p]["transitions"]:
                            self.graph[p]["transitions"].remove(nom_noeud)
                # Les sortantes sont déjà gérées via les arcs supprimés

    #JETONS
    def synchroniser_jetons(self, nom_place):
        data = self.graph[nom_place]
        while len(data["jetons_couleurs"]) < data["jetons"]:
            data["jetons_couleurs"].append("red")
        while len(data["jetons_couleurs"]) > data["jetons"]:
            data["jetons_couleurs"].pop()

    def redessiner_jetons(self, nom_place):
        data = self.graph[nom_place]

        self.synchroniser_jetons(nom_place)

        for j in data["jetons_visuels"]:
            canvas.delete(j)
        data["jetons_visuels"].clear()

        x, y = data["x"], data["y"]
        r = 6
        spacing = 14

        for i, couleur in enumerate(data["jetons_couleurs"]):
            dx = (i % 3 - 1) * spacing
            dy = (i // 3 - 1) * spacing
            jeton = canvas.create_oval(
                x + dx - r, y + dy - r,
                x + dx + r, y + dy + r,
                fill=couleur,
                outline="black"
            )
            data["jetons_visuels"].append(jeton)

    def ajouter_jeton(self, nom_place):
        if nom_place in self.graph and self.graph[nom_place]["type"] == "place":

            couleur = colorchooser.askcolor(title="Choisir la couleur du jeton")[1]

            # Si l'utilisateur annule
            if couleur is None:
                return

            self.graph[nom_place]["jetons"] += 1
            self.graph[nom_place]["jetons_couleurs"].append(couleur)

            canvas.itemconfig(
                self.graph[nom_place]["text_jeton"],
                text=str(self.graph[nom_place]["jetons"])
            )

            self.redessiner_jetons(nom_place)

    def retirer_jeton(self, nom_place):
        if nom_place in self.graph and self.graph[nom_place]["type"] == "place":
            if self.graph[nom_place]["jetons"] > 0:
                self.graph[nom_place]["jetons"] -= 1
                self.graph[nom_place]["jetons_couleurs"].pop()
                canvas.itemconfig(
                    self.graph[nom_place]["text_jeton"],
                    text=str(self.graph[nom_place]["jetons"])
                )
                self.redessiner_jetons(nom_place)

    #RENOMMAGE
    def renommer_noeud_visuel(self, nom_noeud, nouveau_texte):
        if nom_noeud not in self.graph: return
        canvas.itemconfig(self.graph[nom_noeud]["text_nom"], text=nouveau_texte)

    #TIRER TRANSITION
    def tirer_transition(self, nom_transition):
        if nom_transition not in self.graph:
            return False
        t = self.graph[nom_transition]
        if t["type"] != "transition":
            return False

        # Vérifier jetons entrantes selon poids
        for p in t.get("entrantes", []):
            arc = next((a for a in self.arcs if a["from"] == p and a["to"] == nom_transition), None)
            if arc and self.graph[p]["jetons"] < arc["poids"]:
                messagebox.showinfo(
                    "Impossible",
                    f"Transition {nom_transition} ne peut pas être tirée (place {p} manque de jetons)"
                )
                return False

        # Retirer jetons des places entrantes et récupérer leurs couleurs
        couleurs_a_distribuer = []
        for p in t.get("entrantes", []):
            arc = next((a for a in self.arcs if a["from"] == p and a["to"] == nom_transition), None)
            if arc:
                for _ in range(arc["poids"]):
                    if self.graph[p]["jetons"] > 0:
                        self.graph[p]["jetons"] -= 1
                        if self.graph[p]["jetons_couleurs"]:
                            couleur = self.graph[p]["jetons_couleurs"].pop(0)
                            couleurs_a_distribuer.append(couleur)
                canvas.itemconfig(self.graph[p]["text_jeton"], text=str(self.graph[p]["jetons"]))
                self.redessiner_jetons(p)

        # Ajouter jetons aux places sortantes en utilisant les couleurs retirées
        for p in t.get("sortantes", []):
            arc = next((a for a in self.arcs if a["from"] == nom_transition and a["to"] == p), None)
            if arc:
                for _ in range(arc["poids"]):
                    self.graph[p]["jetons"] += 1
                    # Utiliser la couleur d'un jeton entrante si disponible, sinon rouge
                    couleur = couleurs_a_distribuer.pop(0) if couleurs_a_distribuer else "red"
                    self.graph[p]["jetons_couleurs"].append(couleur)
                canvas.itemconfig(self.graph[p]["text_jeton"], text=str(self.graph[p]["jetons"]))
                self.redessiner_jetons(p)

        return True

    #EXPORT JSON
    def to_json_dict(self):
        data = {
            "meta": {
                "type": "PetriNet",
                "version": "1.0"
            },
            "places": [],
            "transitions": [],
            "arcs": []
        }
        for nom, noeud in self.graph.items():
            if noeud["type"] == "place":
                data["places"].append({
                    "id": nom,
                    "x": noeud["x"],
                    "y": noeud["y"],
                    "jetons": noeud["jetons"]
                })
            elif noeud["type"] == "transition":
                data["transitions"].append({
                    "id": nom,
                    "x": noeud["x"],
                    "y": noeud["y"],
                    "entrantes": noeud.get("entrantes", []),
                    "sortantes": noeud.get("sortantes", [])
                })
        for arc in self.arcs:
            data["arcs"].append({
                "from": arc["from"],
                "to": arc["to"],
                "poids": arc["poids"]
            })
        return data



# Instance graphe
graph = graph_dictionnaire()


# Fonction globale pour exporter JSON
def exporter_json():
    data = graph.to_json_dict()
    fichier = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("Fichier JSON", "*.json")],
        title="Exporter le réseau de Petri"
    )
    messagebox.showinfo("Export réussi", "Le réseau a été exporté en JSON.")



# Fonctions UI
def ui_ajouter_place(): graph.ajouter_place()
def ui_retirer_place():
    if selected_node and graph.graph[selected_node]["type"] == "place":
        graph.retirer_place(selected_node)
    else:
        graph.retirer_place()  # supprime la dernière par défaut

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


# Graphe d'état (accessibilité)
def _get_places_order():
    lst = [n for n, d in graph.graph.items() if d["type"] == "place"]
    # tri P1,P2,... si possible
    def keyp(x):
        try:
            return int(x[1:])
        except:
            return 10**9
    return sorted(lst, key=keyp)

def _get_transitions_order():
    lst = [n for n, d in graph.graph.items() if d["type"] == "transition"]
    def keyt(x):
        try:
            return int(x[1:])
        except:
            return 10**9
    return sorted(lst, key=keyt)

def _arc_weight(src, dst):
    a = next((x for x in graph.arcs if x["from"] == src and x["to"] == dst), None)
    return a["poids"] if a else 1

def _marking_tuple(places_order):
    return tuple(graph.graph[p]["jetons"] for p in places_order)

def _marking_str(marking, places_order):
    return "(" + ", ".join(f"{p}={marking[i]}" for i, p in enumerate(places_order)) + ")"

def _enabled(marking, places_order, tname):
    t = graph.graph[tname]
    # entrantes
    for p in t.get("entrantes", []):
        w = _arc_weight(p, tname)
        idx = places_order.index(p)
        if marking[idx] < w:
            return False
    return True
def _fire(marking, places_order, tname):
    t = graph.graph[tname]
    new = list(marking)
    # consomme
    for p in t.get("entrantes", []):
        w = _arc_weight(p, tname)
        idx = places_order.index(p)
        new[idx] -= w
    # produit
    for p in t.get("sortantes", []):
        w = _arc_weight(tname, p)
        idx = places_order.index(p)
        new[idx] += w
    return tuple(new)

def build_state_graph(max_states=50):
    places_order = _get_places_order()
    transitions_order = _get_transitions_order()

    if not places_order:
        messagebox.showinfo("Graphe d'état", "Ajoute au moins 1 place.")
        return None

    if not transitions_order:
        messagebox.showinfo("Graphe d'état", "Ajoute au moins 1 transition.")
        return None

    start = _marking_tuple(places_order)

    seen = {start: 0}
    states = [start]
    edges = []  # (from_idx, to_idx, Tname)

    q = deque([start])

    while q and len(states) < max_states:
        m = q.popleft()
        m_idx = seen[m]

        for t in transitions_order:
            if _enabled(m, places_order, t):
                m2 = _fire(m, places_order, t)
                if m2 not in seen:
                    seen[m2] = len(states)
                    states.append(m2)
                    q.append(m2)
                edges.append((m_idx, seen[m2], t))

    return places_order, states, edges

def show_state_graph():
    res = build_state_graph(max_states=50)
    if res is None:
        return

    places_order, states, edges = res  # edges: (from_state_idx, to_state_idx, Tname)

    win = Toplevel(root)
    win.title("Graphe d'état (style réseau de Petri)")

    c = Canvas(win, width=1200, height=850, bg="white")
    c.pack(fill="both", expand=True)


    # Helpers dessin
    def draw_state_circle(cx, cy, text, r=40, thick=2):
        oval = c.create_oval(cx - r, cy - r, cx + r, cy + r, width=thick, fill="white")
        c.create_text(cx, cy, text=text, font=("Montserrat", 9), width=160)
        return oval

    def draw_transition_rect(cx, cy, text, w=26, h=70, thick=2):
        rect = c.create_rectangle(cx - w/2, cy - h/2, cx + w/2, cy + h/2, width=thick, fill="black")
        c.create_text(cx, cy + h/2 + 14, text=text, font=("Montserrat", 9))
        return rect

    # Placement des états (ronds)
    padding = 80
    cols = 4
    cell_w = 260
    cell_h = 190

    state_pos = {}
    for i, m in enumerate(states):
        row = i // cols
        col = i % cols
        cx = padding + col * cell_w
        cy = padding + row * cell_h

        label = f"S{i}\n{_marking_str(m, places_order)}"
        thick = 3 if i == 0 else 2
        draw_state_circle(cx, cy, label, r=45, thick=thick)
        state_pos[i] = (cx, cy)


    # Création des "noeuds transitions" (rectangles)
    # 1 rectangle par arc "tir possible" : (Tname@Sfrom)
    trans_node_pos = {}  # key = (from_idx, tname, to_idx) -> (x,y)
    for (a, b, tname) in edges:
        ax, ay = state_pos[a]
        bx, by = state_pos[b]

        # placer le rectangle au milieu, légèrement décalé pour éviter superposition
        mx = (ax + bx) / 2
        my = (ay + by) / 2

        # petit décalage basé sur hash pour séparer si plusieurs transitions entre mêmes états
        shift = (hash((a, b, tname)) % 31) - 15
        mx += shift
        my -= 25

        draw_transition_rect(mx, my, tname)
        trans_node_pos[(a, tname, b)] = (mx, my)

    # Arcs : S -> Trect -> S
    for (a, b, tname) in edges:
        ax, ay = state_pos[a]
        bx, by = state_pos[b]
        tx, ty = trans_node_pos[(a, tname, b)]

        # état -> transition (sans flèche)
        c.create_line(ax, ay, tx, ty, width=2)

        # transition -> état (avec flèche)
        c.create_line(tx, ty, bx, by, arrow=LAST, width=2)

    info = f"États (ronds): {len(states)} | Transitions (rectangles): {len(edges)} | Limite: 200"
    c.create_text(10, 835, text=info, anchor="w", font=("Montserrat", 11))


# Gestion des événements souris
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
            new_tokens = simpledialog.askinteger(
                "Modifier Place", "Nombre de jetons :",
                initialvalue=data["jetons"], minvalue=0
            )
            if new_tokens is not None:
                diff = new_tokens - data["jetons"]
                data["jetons"] = new_tokens
                if diff > 0:  # ajout de jetons
                    for _ in range(diff):
                        couleur = colorchooser.askcolor(title="Couleur du jeton")[1]
                        if couleur is None:
                            couleur = "red"
                        data["jetons_couleurs"].append(couleur)
                elif diff < 0:  # suppression de jetons
                    for _ in range(-diff):
                        if data["jetons_couleurs"]:
                            data["jetons_couleurs"].pop()
                canvas.itemconfig(data["text_jeton"], text=str(new_tokens))
                graph.redessiner_jetons(node)

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


# Boutons de contrôle
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

#bontons export
Label(controls, text="Exporter le graph", bg="#e4dde9", font=("Montserrat", 13)).pack(pady=20)
Button(controls,text="Télécharger le réseau (JSON)", command=exporter_json).pack(pady=10)

#bouton graphe d'état
Label(controls, text="Analyse", bg="#e4dde9", font=("Montserrat", 13)).pack(pady=20)
Button(controls, text="Graphe d'état", command=show_state_graph).pack(pady=10)



# Fonction pour colorer les noeuds visités
def color_node(nom_noeud, couleur="#FF8CFF"):
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
    if start is None:
        messagebox.showwarning(
            "DFS",
            "Veuillez sélectionner une place ou une transition avant de lancer le DFS."
        )
        return

    if start not in graph.graph:
        messagebox.showerror("DFS", "Nœud invalide.")
        return

    visited = set()

    def dfs(nom_noeud):
        visited.add(nom_noeud)
        color_node(nom_noeud)

        data = graph.graph[nom_noeud]

        if data["type"] == "place":
            neighbors = data["transitions"]
        elif data["type"] == "transition":
            neighbors = data["sortantes"]
        else:
            neighbors = []

        for neighbor in neighbors:
            if neighbor not in visited:
                dfs(neighbor)

    dfs(start)


# bfs
def bfs_algo(start):
    if start is None:
        messagebox.showwarning(
            "BFS",
            "Veuillez sélectionner une place ou une transition avant de lancer le BFS."
        )
        return

    if start not in graph.graph:
        messagebox.showerror("BFS", "Nœud invalide.")
        return

    visited = set()
    queue = deque([start])
    visited.add(start)

    while queue:
        nom_noeud = queue.popleft()
        color_node(nom_noeud, "#8C9DFF")

        data = graph.graph[nom_noeud]

        if data["type"] == "place":
            neighbors = data["transitions"]
        elif data["type"] == "transition":
            neighbors = data["sortantes"]
        else:
            neighbors = []

        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)


root.mainloop()