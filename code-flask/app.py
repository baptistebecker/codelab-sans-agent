from flask import Flask, redirect, render_template, request

from base import ouvrir_base
from calculi import *

app = Flask(__name__)


# Page d'accueil : lit les membres et affiche PAGE.
@app.get("/")
def accueil():
    with ouvrir_base() as conn:
        membres = conn.execute("SELECT nom FROM membres").fetchall()
        groupes = conn.execute("SELECT nom FROM groupes").fetchall()
    return render_template('page.html', membres=membres, groupes=groupes)


# Exemple : reçoit le formulaire et ajoute un membre au groupe 1.
@app.post("/membres")
def ajouter_membre():
    nom = request.form["nom"]
    with ouvrir_base() as conn:
        conn.execute("INSERT INTO membres (groupe_id, nom) VALUES (1, ?)", [nom])
    return redirect("/")



@app.post("/groupes")
def ajouter_groupe():
    nom_groupe = request.form["nom"]
    date_debut = request.form["date_debut"]
    date_fin = request.form["date_fin"]
    
    with ouvrir_base() as conn:
        conn.execute("INSERT INTO groupes (nom, date_debut, date_fin) VALUES (?, ?, ?)", [nom_groupe, date_debut, date_fin])
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
