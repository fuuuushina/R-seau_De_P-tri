class graph_dictionnaire:
    def __init__(self):
        self.graph = {}

    def ajouter_sommet(self, sommet):
        if sommet not in self.graph:
            self.graph[sommet] = {}

    def ajouter_arrete(self, sommet1, sommet2, poids):
        if sommet1 in self.graph and sommet2 in self.graph:
            self.graph[sommet1][sommet2] = poids

    def supprimer_arrete(self, sommet1, sommet2):
        if sommet1 in self.graph and sommet2 in self.graph[sommet1]:
            del self.graph[sommet1][sommet2]

    def supprimer_sommet(self, sommet):
        if sommet in self.graph:
            del self.graph[sommet]
            for s in self.graph:
                del self.graph[s][sommet]

    def recherche(self, sommet1, sommet2):
        if sommet1 in self.graph and sommet2 in self.graph[sommet1]:
            return self.graph[sommet1][sommet2]
        return None


graph = graph_dictionnaire()

