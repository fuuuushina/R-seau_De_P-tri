#!/usr/bin/env python3
# petri_tool_cpn.py
# Éditeur & analyseur de réseaux de Petri colorés (CPN)

import tkinter as tk
from tkinter import simpledialog, messagebox
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from collections import deque
import time

# =========================================================
# STYLE GRAPHIQUE
# =========================================================

BG_PANEL = "#e4dde9"
BG_CANVAS = "white"
BTN_BG = "#c9bdd3"
BTN_ACTIVE = "#b3a4c2"
TXT = "#2e2a32"

FONT_TITLE = ("Montserrat", 15, "bold")
FONT_BTN = ("Montserrat", 11)
FONT_LABEL = ("Montserrat", 11)
FONT_TOKEN = ("Montserrat", 13, "bold")
FONT_TRANS = ("Montserrat", 10, "bold")

# =========================================================
# MODELE
# =========================================================

@dataclass
class Place:
    id: str
    label: str
    x: int
    y: int
    tokens: Dict[str, int] = field(default_factory=dict)  # jetons colorés
    r: int = 60

@dataclass
class Transition:
    id: str
    label: str
    x: int
    y: int
    cost: int = 1
    w: int = 60
    h: int = 40
    guard: str = ""  # expression de garde pour CPN

@dataclass
class Arc:
    id: str
    src: str
    dst: str
    weight: Dict[str, int] = field(default_factory=dict)  # jetons colorés

@dataclass
class PetriNet:
    places: Dict[str, Place] = field(default_factory=dict)
    transitions: Dict[str, Transition] = field(default_factory=dict)
    arcs: Dict[str, Arc] = field(default_factory=dict)

    # vérifie si transition tirable pour toutes les couleurs
    def enabled(self, tid):
        t = self.transitions[tid]
        for a in self.arcs.values():
            if a.dst == tid and a.src in self.places:
                place = self.places[a.src]
                for color, w in a.weight.items():
                    if place.tokens.get(color, 0) < w * t.cost:
                        return False
        return True

    # tir d'une transition
    def fire(self, tid):
        if not self.enabled(tid):
            return False
        t = self.transitions[tid]
        # consommer jetons
        for a in self.arcs.values():
            if a.dst == tid and a.src in self.places:
                place = self.places[a.src]
                for color, w in a.weight.items():
                    place.tokens[color] = place.tokens.get(color, 0) - w * t.cost
        # produire jetons
        for a in self.arcs.values():
            if a.src == tid and a.dst in self.places:
                place = self.places[a.dst]
                for color, w in a.weight.items():
                    place.tokens[color] = place.tokens.get(color, 0) + w
        return True

# =========================================================
# ANALYSE
# =========================================================

def explore(net, bound=20):
    def marking():
        return tuple(tuple(p.tokens.items()) for p in net.places.values())

    seen = set()
    q = deque([marking()])
    seen.add(marking())
    deadlock = False
    unbounded = False

    while q:
        m = q.popleft()
        for i, pid in enumerate(net.places):
            net.places[pid].tokens = dict(m[i])

        enabled = [t for t in net.transitions if net.enabled(t)]
        if not enabled:
            deadlock = True

        for t in enabled:
            net.fire(t)
            m2 = marking()
            if any(sum(v for k, v in mv) > bound for mv in m2):
                unbounded = True
            if m2 not in seen:
                seen.add(m2)
                q.append(m2)
            for i, pid in enumerate(net.places):
                net.places[pid].tokens = dict(m[i])

    return deadlock, unbounded, len(seen)

# =========================================================
# INTERFACE
# =========================================================

class App:
    def __init__(self, root):
        self.root = root
        root.title("Réseau de Petri Coloré — Éditeur")
        root.configure(bg=BG_PANEL)

        self.net = PetriNet()
        self.mode = "select"
        self.arc_start = None
        self.drag = None

        self.canvas = tk.Canvas(root, bg=BG_CANVAS, width=900, height=700)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        panel = tk.Frame(root, bg=BG_PANEL, padx=20, pady=40)
        panel.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(panel, text="ÉDITION DU RÉSEAU",
                 bg=BG_PANEL, fg=TXT,
                 font=FONT_TITLE).pack(pady=10)

        for m in ["select", "place", "transition", "arc", "delete"]:
            tk.Button(panel, text=m.capitalize(),
                      font=FONT_BTN,
                      bg=BTN_BG, activebackground=BTN_ACTIVE,
                      relief="flat",
                      command=lambda x=m: self.set_mode(x)
                      ).pack(fill=tk.X, pady=4)

        tk.Button(panel, text="DFS",
                  font=FONT_BTN,
                  bg=BTN_BG, relief="flat",
                  command=self.dfs_dialog).pack(fill=tk.X, pady=4)

        tk.Button(panel, text="BFS",
                  font=FONT_BTN,
                  bg=BTN_BG, relief="flat",
                  command=self.bfs_dialog).pack(fill=tk.X, pady=4)

        tk.Button(panel, text="Tirer une transition",
                  font=FONT_BTN,
                  bg=BTN_BG, relief="flat",
                  command=self.fire_dialog).pack(fill=tk.X, pady=10)

        tk.Button(panel, text="Analyse formelle",
                  font=FONT_BTN,
                  bg=BTN_BG, relief="flat",
                  command=self.analyse).pack(fill=tk.X)

        self.status = tk.Label(panel, text="Prêt",
                               bg=BG_PANEL, fg=TXT,
                               font=("Montserrat", 10))
        self.status.pack(fill=tk.X, pady=15)

        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<B1-Motion>", self.dragging)
        self.canvas.bind("<Double-Button-1>", self.edit)

    # -----------------------------
    # LOGIQUE EDITION
    # -----------------------------
    def set_mode(self, m):
        self.mode = m
        self.arc_start = None
        self.status.config(text=f"Mode : {m}")

    def click(self, e):
        x, y = e.x, e.y
        el = self.find(x, y)

        if self.mode == "delete" and el:
            self.delete(el)
            self.draw()
            return

        if self.mode == "place":
            name = simpledialog.askstring("Nouvelle place", "Nom de la place :")
            if name:
                pid = f"P{len(self.net.places)+1}"
                tokens = {}
                # Demander couleur et quantité
                color = simpledialog.askstring("Couleur du jeton", "Entrez la couleur du jeton :")
                if color:
                    qty = simpledialog.askinteger("Quantité", "Nombre de jetons :", minvalue=0)
                    tokens[color] = qty or 0
                self.net.places[pid] = Place(pid, name, x, y, tokens)
            self.draw()
            return

        if self.mode == "transition":
            name = simpledialog.askstring("Nouvelle transition", "Nom de la transition :")
            cost = simpledialog.askinteger("Coût", "Coût de la transition :", minvalue=1)
            if name and cost:
                tid = f"T{len(self.net.transitions)+1}"
                self.net.transitions[tid] = Transition(tid, name, x, y, cost)
            self.draw()
            return

        if self.mode == "arc" and el:
            if not self.arc_start:
                self.arc_start = el
                return
            if ((self.arc_start in self.net.places and el in self.net.transitions) or
                (self.arc_start in self.net.transitions and el in self.net.places)):
                aid = f"A{len(self.net.arcs)+1}"
                weight = {}
                color = simpledialog.askstring("Couleur de l'arc", "Couleur du jeton :")
                if color:
                    w = simpledialog.askinteger("Poids", "Nombre de jetons :", minvalue=1)
                    weight[color] = w or 1
                self.net.arcs[aid] = Arc(aid, self.arc_start, el, weight)
            else:
                messagebox.showerror("Arc invalide", "Place ↔ Transition uniquement")
            self.arc_start = None
            self.draw()
            return

        if el:
            self.drag = (el, x, y)

    def delete(self, el):
        self.net.places.pop(el, None)
        self.net.transitions.pop(el, None)
        self.net.arcs = {k: a for k, a in self.net.arcs.items() if a.src != el and a.dst != el}

    def dragging(self, e):
        if not self.drag:
            return
        el, ox, oy = self.drag
        dx, dy = e.x - ox, e.y - oy
        if el in self.net.places:
            self.net.places[el].x += dx
            self.net.places[el].y += dy
        if el in self.net.transitions:
            self.net.transitions[el].x += dx
            self.net.transitions[el].y += dy
        self.drag = (el, e.x, e.y)
        self.draw()

    def edit(self, e):
        el = self.find(e.x, e.y)
        if el in self.net.places:
            p = self.net.places[el]
            p.label = simpledialog.askstring("Nom", "Nom :", initialvalue=p.label)
        if el in self.net.transitions:
            t = self.net.transitions[el]
            t.label = simpledialog.askstring("Nom", "Nom :", initialvalue=t.label)
        self.draw()

    def fire_dialog(self):
        tid = simpledialog.askstring("Tir", "ID transition :")
        if tid in self.net.transitions:
            self.net.fire(tid)
            self.draw()

    def analyse(self):
        dead, unb, n = explore(self.net)
        messagebox.showinfo("Analyse",
                            f"États atteignables : {n}\nBloquant : {dead}\nNon borné : {unb}")

    def find(self, x, y):
        for p in self.net.places.values():
            if (x - p.x) ** 2 + (y - p.y) ** 2 <= p.r ** 2:
                return p.id
        for t in self.net.transitions.values():
            if t.x - t.w <= x <= t.x + t.w and t.y - t.h <= y <= t.y + t.h:
                return t.id
        return None

    def draw(self):
        self.canvas.delete("all")
        for a in self.net.arcs.values():
            s = self.net.places.get(a.src) or self.net.transitions.get(a.src)
            d = self.net.places.get(a.dst) or self.net.transitions.get(a.dst)
            self.canvas.create_line(s.x, s.y, d.x, d.y, arrow=tk.LAST, width=2)
        for p in self.net.places.values():
            self.canvas.create_oval(p.x - p.r, p.y - p.r, p.x + p.r, p.y + p.r,
                                    fill="#f6f3f9", outline=TXT, width=2)
            self.canvas.create_text(p.x, p.y - 6, text=p.label, font=FONT_LABEL, fill=TXT)
            # affichage jetons colorés
            y_offset = 0
            for color, nb in p.tokens.items():
                self.canvas.create_text(p.x, p.y + 10 + y_offset, text=f"{nb} ({color})", font=FONT_TOKEN, fill=TXT)
                y_offset += 15
        for tid, t in self.net.transitions.items():
            color = "#5cb85c" if self.net.enabled(tid) else "#d9534f"
            self.canvas.create_rectangle(t.x - t.w, t.y - t.h, t.x + t.w, t.y + t.h,
                                         fill=color, outline=TXT, width=2)
            self.canvas.create_text(t.x, t.y, text=f"{t.label}\n({t.cost})", font=FONT_TRANS, fill="white")

    # ==========================
    # DFS / BFS
    # ==========================
    def get_pos(self, name):
        if name in self.net.places:
            p = self.net.places[name]
            return p.x, p.y
        if name in self.net.transitions:
            t = self.net.transitions[name]
            return t.x, t.y
        return 0, 0

    def visit_node(self, name):
        pos = self.get_pos(name)
        if name in self.net.places:
            self.canvas.create_oval(pos[0] - 20, pos[1] - 20, pos[0] + 20, pos[1] + 20, fill="yellow")
            self.canvas.create_text(pos[0], pos[1] - 5, text=name)
        if name in self.net.transitions:
            self.canvas.create_rectangle(pos[0] - 20, pos[1] - 10, pos[0] + 20, pos[1] + 10, fill="yellow")
            self.canvas.create_text(pos[0], pos[1], text=name)
        self.canvas.update()
        time.sleep(0.5)
        self.draw()

    def dfs_algo(self, start_name):
        visited = set()
        def dfs(name):
            visited.add(name)
            self.visit_node(name)
            neighbors = [a.dst for a in self.net.arcs.values() if a.src == name]
            for n in neighbors:
                if n not in visited:
                    dfs(n)
        dfs(start_name)

    def bfs_algo(self, start_name):
        visited = set()
        q = deque([start_name])
        visited.add(start_name)
        while q:
            name = q.popleft()
            self.visit_node(name)
            neighbors = [a.dst for a in self.net.arcs.values() if a.src == name]
            for n in neighbors:
                if n not in visited:
                    visited.add(n)
                    q.append(n)

    def dfs_dialog(self):
        start = simpledialog.askstring("DFS", "Nom du noeud de départ :")
        if start:
            # rechercher le nom exact
            nid = None
            for p in self.net.places.values():
                if p.label == start:
                    nid = p.id
            for t in self.net.transitions.values():
                if t.label == start:
                    nid = t.id
            if nid:
                self.dfs_algo(nid)
            else:
                messagebox.showerror("Erreur", f"Noeud '{start}' non trouvé")

    def bfs_dialog(self):
        start = simpledialog.askstring("BFS", "Nom du noeud de départ :")
        if start:
            nid = None
            for p in self.net.places.values():
                if p.label == start:
                    nid = p.id
            for t in self.net.transitions.values():
                if t.label == start:
                    nid = t.id
            if nid:
                self.bfs_algo(nid)
            else:
                messagebox.showerror("Erreur", f"Noeud '{start}' non trouvé")

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
