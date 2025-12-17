from tkinter import *

root = Tk()
root.title("Réseau de Petri INGÉNIEUR DESIGNER")
#page de controle violette ou on pourra changer les jetons
controls = Frame(root, padx=20, pady=70, bg="#e4dde9")
controls.pack(side=RIGHT)
#nous l'avons lis à droite
Label(controls, text="CONTROLE DE JETONS", font=("Montserrat", 15)).pack(pady=5)
controls.pack(side=RIGHT, fill=Y)

canvas = Canvas(root, width=900, height=800, bg="white")
canvas.pack()


class Place:
    def _init_(self, name, tokens=0):
        self.name = name
        self.tokens = tokens

place = canvas.create_oval(250, 250, 350, 350, width=3)

# Affichage du nombre de jetons
jetons = 0
jeton_text = None



# Affichage du nombre de jetons
jeton_text = canvas.create_text(300, 300, text=str(jetons), font=("Montserrat", 14))


def ajouter_jeton():
    global jetons
    jetons += 1
    canvas.itemconfig(jeton_text, text=str(jetons))

def retirer_jeton():
    global jetons
    if jetons > 0:
        jetons -= 1
    canvas.itemconfig(jeton_text, text=str(jetons))


Button(controls, text="+ Ajouter un jeton", command=ajouter_jeton).pack(pady=10)
Button(controls, text="- Retirer un jeton", command=retirer_jeton).pack(pady=10)


#on rajoute des places
places_nouvelles = 0
#nous stockons les places ( de jetons ) dans :
#utile pour les retirer par la suite
places=[]

#on rajoute un jeton à une place séparé par 120 pixels
def ajouter_place():
    global places_nouvelles
    places_nouvelles += 1

    x = 150 + (places_nouvelles * 120)
    y = 500

    jetons = 0
    text_jeton = canvas.create_text(x, y, text="0", font=("Montserrat", 14))
    oval = canvas.create_oval(x-40, y-40, x+40, y+40, width=2)

    def ajouter_jeton_place (event):
        nonlocal jetons
        jetons += 1
        canvas.itemconfig(text_jeton, text=str(jetons))
    canvas.tag_bind(oval, "<Button-1>", ajouter_jeton_place)

    # numero des places / jetons
    nom = canvas.create_text(x, y+55, text=f"P{places_nouvelles}", font=("Montserrat", 12))
#stockage des places
    places.append((oval, text_jeton, nom))


def retirer_place():
    global places_nouvelles
    if places:
        oval, text_jeton, label = places.pop()
        canvas.delete(oval)
        canvas.delete(text_jeton)
        canvas.delete(label)
        places_nouvelles -= 1



#nouvelles transitions
transitions_nouvelles = 0
transitions =[]

def ajouter_transition():
    global transitions_nouvelles
    transitions_nouvelles += 1

    x = 200 + (transitions_nouvelles * 60)
    y = 650

    rectangle = canvas.create_rectangle(x-10, y-40, x+10, y+40, width=2, fill="black")
    nom = canvas.create_text(x, y+60, text=f"T{transitions_nouvelles}", font=("Montserrat", 12))

    transitions.append((rectangle, nom))

def retirer_transition():
    global transitions_nouvelles
    if transitions:
        rectangle, nom = transitions.pop()
        canvas.delete(rectangle)
        canvas.delete(nom)
        transitions_nouvelles -= 1


# Boutons d’ajout
Label(controls, text="Édition du réseau", bg="#e4dde9", font=("Montserrat", 13)).pack(pady=20)
Button(controls, text="Ajouter une place", command=ajouter_place).pack(pady=15)
Button(controls, text="Retirer une place", command=retirer_place).pack(pady=15)
Button(controls, text="Ajouter une transition", command=ajouter_transition).pack(pady=8)
Button(controls, text="Retirer une transition", command=retirer_transition).pack(pady=8)

root.mainloop()