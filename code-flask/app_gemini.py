from flask import Flask, flash, redirect, render_template_string, request, url_for

from base import ouvrir_base
from calculi import DepenseInvalideError, calculer_soldes, valider_depense

app = Flask(__name__)
app.secret_key = "secret-key-codelab"

# HTML & CSS intégrés dans la variable PAGE
PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Partage de Frais</title>
    <style>
        :root {
            --bg: #0f172a;
            --card-bg: #1e293b;
            --accent: #6366f1;
            --accent-hover: #4f46e5;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
            --danger: #ef4444;
            --success: #10b981;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 2rem;
            display: flex;
            justify-content: center;
        }
        .container {
            width: 100%;
            max-width: 900px;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--border);
            padding-bottom: 1rem;
        }
        h1, h2, h3 { margin: 0; }
        .flash-error {
            background-color: rgba(239, 68, 68, 0.15);
            border: 1px solid var(--danger);
            color: var(--danger);
            padding: 1rem;
            border-radius: 8px;
            font-weight: 500;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
        }
        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        label {
            font-size: 0.875rem;
            color: var(--text-muted);
        }
        input, select {
            background-color: var(--bg);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 0.75rem;
            border-radius: 6px;
            font-size: 1rem;
        }
        input:focus, select:focus {
            outline: 2px solid var(--accent);
        }
        button {
            background-color: var(--accent);
            color: white;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover { background-color: var(--accent-hover); }
        .btn-danger {
            background-color: transparent;
            color: var(--danger);
            border: 1px solid var(--danger);
            padding: 0.4rem 0.8rem;
            font-size: 0.85rem;
        }
        .btn-danger:hover {
            background-color: var(--danger);
            color: white;
        }
        .badge {
            padding: 0.25rem 0.6rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        .badge-positive { background-color: rgba(16, 185, 129, 0.2); color: var(--success); }
        .badge-negative { background-color: rgba(239, 68, 68, 0.2); color: var(--danger); }
        .badge-zero { background-color: rgba(148, 163, 184, 0.2); color: var(--text-muted); }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        th, td {
            text-align: left;
            padding: 0.75rem;
            border-bottom: 1px solid var(--border);
        }
        th { color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; }
        .checkbox-group {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
        }
        .checkbox-label {
            display: flex;
            align-items: center;
            gap: 0.3rem;
            background: var(--bg);
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            border: 1px solid var(--border);
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>✈️ Partage de Frais</h1>
            {% if groupe %}
                <div>
                    <strong style="font-size: 1.2rem;">{{ groupe.nom }}</strong>
                    <div style="color: var(--text-muted); font-size: 0.85rem;">
                        Du {{ groupe.date_debut }} au {{ groupe.date_fin }}
                    </div>
                </div>
            {% endif %}
        </header>

        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for msg in messages %}
              <div class="flash-error">⚠️ {{ msg }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <!-- SECTION 1 : CHOISIR OU CRÉER UN GROUPE -->
        <div class="grid">
            <div class="card">
                <h2>📁 Vos Groupes</h2>
                <form method="get" action="/" style="margin-top: 1rem;">
                    <div class="form-group">
                        <select name="groupe_id" onchange="this.form.submit()">
                            {% for g in groupes %}
                                <option value="{{ g.id }}" {% if groupe and g.id == groupe.id %}selected{% endif %}>
                                    {{ g.nom }}
                                </option>
                            {% endfor %}
                        </select>
                    </div>
                </form>
            </div>

            <div class="card">
                <h2>➕ Créer un groupe</h2>
                <form method="post" action="/groupes" style="margin-top: 1rem;">
                    <div class="form-group">
                        <input name="nom" placeholder="Nom (ex: Vacances à Spa)" required>
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                        <div class="form-group" style="flex:1;">
                            <label>Début</label>
                            <input type="date" name="date_debut" required>
                        </div>
                        <div class="form-group" style="flex:1;">
                            <label>Fin</label>
                            <input type="date" name="date_fin" required>
                        </div>
                    </div>
                    <button type="submit" style="width: 100%;">Créer le groupe</button>
                </form>
            </div>
        </div>

        {% if groupe %}
        <!-- SECTION 2 : SOLDES ET MEMBRES -->
        <div class="grid">
            <div class="card">
                <h2>💰 Soldes du groupe</h2>
                <ul style="list-style: none; padding: 0; margin-top: 1rem;">
                    {% for m in membres %}
                        <li style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                            <span><strong>{{ m.nom }}</strong></span>
                            {% set solde = soldes[m.id] %}
                            <span class="badge {% if solde > 0 %}badge-positive{% elif solde < 0 %}badge-negative{% else %}badge-zero{% endif %}">
                                {% if solde > 0 %}+{% endif %}{{ "%.2f"|format(solde) }} €
                            </span>
                        </li>
                    {% endfor %}
                </ul>
            </div>

            <div class="card">
                <h2>👤 Ajouter un membre</h2>
                <form method="post" action="/membres" style="margin-top: 1rem;">
                    <input type="hidden" name="groupe_id" value="{{ groupe.id }}">
                    <div class="form-group">
                        <input name="nom" placeholder="Prénom (ex: Alice)" required>
                    </div>
                    <button type="submit" style="width: 100%;">Ajouter au groupe</button>
                </form>
            </div>
        </div>

        <!-- SECTION 3 : NOUVELLE DÉPENSE -->
        <div class="card">
            <h2>💳 Ajouter une dépense</h2>
            <form method="post" action="/depenses" style="margin-top: 1rem;">
                <input type="hidden" name="groupe_id" value="{{ groupe.id }}">
                <div class="grid">
                    <div class="form-group">
                        <label>Libellé</label>
                        <input name="libelle" placeholder="ex: Restaurant, Courses..." required>
                    </div>
                    <div class="form-group">
                        <label>Montant (€)</label>
                        <input type="number" step="0.01" name="montant" placeholder="0.00" required>
                    </div>
                    <div class="form-group">
                        <label>Date</label>
                        <input type="date" name="date" value="{{ groupe.date_debut }}" required>
                    </div>
                    <div class="form-group">
                        <label>Payeur</label>
                        <select name="payeur_id" required>
                            {% for m in membres %}
                                <option value="{{ m.id }}">{{ m.nom }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>

                <div class="form-group">
                    <label>Participants</label>
                    <div class="checkbox-group">
                        {% for m in membres %}
                            <label class="checkbox-label">
                                <input type="checkbox" name="participants" value="{{ m.id }}" checked>
                                {{ m.nom }}
                            </label>
                        {% endfor %}
                    </div>
                </div>

                <button type="submit" style="margin-top: 0.5rem;">Enregistrer la dépense</button>
            </form>
        </div>

        <!-- SECTION 4 : HISTORIQUE DES DÉPENSES -->
        <div class="card">
            <h2>📜 Historique des dépenses</h2>
            {% if depenses_affichage %}
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Libellé</th>
                            <th>Montant</th>
                            <th>Payé par</th>
                            <th>Pour</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for d in depenses_affichage %}
                            <tr>
                                <td>{{ d.date }}</td>
                                <td><strong>{{ d.libelle }}</strong></td>
                                <td>{{ d.montant_euros }} €</td>
                                <td>{{ d.payeur_nom }}</td>
                                <td><small>{{ d.participants_noms }}</small></td>
                                <td>
                                    <form method="post" action="/depenses/{{ d.id }}/supprimer" style="margin:0;">
                                        <input type="hidden" name="groupe_id" value="{{ groupe.id }}">
                                        <button type="submit" class="btn-danger">Supprimer</button>
                                    </form>
                                </td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p style="color: var(--text-muted); margin-top: 1rem;">Aucune dépense enregistrée pour le moment.</p>
            {% endif %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""


# -----------------------------------------------------------------------------
# ROUTES FLASK
# -----------------------------------------------------------------------------

@app.get("/")
def accueil():
    groupe_id = request.args.get("groupe_id", type=int)

    with ouvrir_base() as conn:
        groupes = conn.execute("SELECT * FROM groupes").fetchall()

        # Si aucun groupe sélectionné, on prend le premier disponible par défaut
        if not groupe_id and groupes:
            groupe_id = groupes[0]["id"]

        groupe = None
        membres = []
        soldes = {}
        depenses_affichage = []

        if groupe_id:
            groupe = conn.execute("SELECT * FROM groupes WHERE id = ?", [groupe_id]).fetchone()
            membres = conn.execute("SELECT * FROM membres WHERE groupe_id = ?", [groupe_id]).fetchall()
            
            # Récupération des dépenses et construction des structures pour calculs.py
            depenses_raw = conn.execute(
                "SELECT d.*, m.nom as payeur_nom FROM depenses d JOIN membres m ON d.payeur_id = m.id WHERE d.groupe_id = ?",
                [groupe_id]
            ).fetchall()

            depenses_pour_calcul = []
            for d in depenses_raw:
                parts = conn.execute(
                    "SELECT m.id, m.nom FROM participants p JOIN membres m ON p.membre_id = m.id WHERE p.depense_id = ?",
                    [d["id"]]
                ).fetchall()

                p_ids = [p["id"] for p in parts]
                p_noms = [p["nom"] for p in parts]

                depenses_pour_calcul.append({
                    "payeur_id": d["payeur_id"],
                    "montant_centimes": d["montant_centimes"],
                    "participants_ids": p_ids
                })

                depenses_affichage.append({
                    "id": d["id"],
                    "libelle": d["libelle"],
                    "montant_euros": f"{d['montant_centimes'] / 100:.2f}",
                    "date": d["date"],
                    "payeur_nom": d["payeur_nom"],
                    "participants_noms": ", ".join(p_noms)
                })

            # Calcul des soldes via calculs.py
            membres_dict = [{"id": m["id"], "nom": m["nom"]} for m in membres]
            soldes = calculer_soldes(membres_dict, depenses_pour_calcul)

    return render_template_string(
        PAGE,
        groupes=groupes,
        groupe=groupe,
        membres=membres,
        soldes=soldes,
        depenses_affichage=depenses_affichage
    )


@app.post("/groupes")
def creer_groupe():
    nom = request.form.get("nom")
    date_debut = request.form.get("date_debut")
    date_fin = request.form.get("date_fin")

    if nom and date_debut and date_fin:
        with ouvrir_base() as conn:
            cursor = conn.execute(
                "INSERT INTO groupes (nom, date_debut, date_fin) VALUES (?, ?, ?)",
                [nom, date_debut, date_fin]
            )
            nouveau_id = cursor.lastrowid
        return redirect(url_for("accueil", groupe_id=nouveau_id))
    
    return redirect(url_for("accueil"))


@app.post("/membres")
def ajouter_membre():
    nom = request.form.get("nom")
    groupe_id = request.form.get("groupe_id", type=int)

    if nom and groupe_id:
        with ouvrir_base() as conn:
            conn.execute("INSERT INTO membres (groupe_id, nom) VALUES (?, ?)", [groupe_id, nom])

    return redirect(url_for("accueil", groupe_id=groupe_id))


@app.post("/depenses")
def ajouter_depense():
    groupe_id = request.form.get("groupe_id", type=int)
    libelle = request.form.get("libelle")
    montant_raw = request.form.get("montant", type=float, default=0.0)
    date_str = request.form.get("date")
    payeur_id = request.form.get("payeur_id", type=int)
    participants_ids = [int(p) for p in request.form.getlist("participants")]

    montant_centimes = int(round(montant_raw * 100))

    with ouvrir_base() as conn:
        groupe = conn.execute("SELECT * FROM groupes WHERE id = ?", [groupe_id]).fetchone()
        membres = conn.execute("SELECT id FROM membres WHERE groupe_id = ?", [groupe_id]).fetchall()
        membres_ids = [m["id"] for m in membres]

        try:
            # Validation via notre module calculs.py
            valider_depense(
                montant_centimes,
                date_str,
                groupe["date_debut"],
                groupe["date_fin"],
                payeur_id,
                participants_ids,
                membres_ids
            )

            # Insertion de la dépense
            cursor = conn.execute(
                "INSERT INTO depenses (groupe_id, libelle, montant_centimes, date, payeur_id) VALUES (?, ?, ?, ?, ?)",
                [groupe_id, libelle, montant_centimes, date_str, payeur_id]
            )
            depense_id = cursor.lastrowid

            # Insertion des participants (l'ordre d'ajout est conservé)
            for p_id in participants_ids:
                conn.execute(
                    "INSERT INTO participants (depense_id, membre_id) VALUES (?, ?)",
                    [depense_id, p_id]
                )

        except DepenseInvalideError as e:
            flash(str(e))

    return redirect(url_for("accueil", groupe_id=groupe_id))


@app.post("/depenses/<int:depense_id>/supprimer")
def supprimer_depense(depense_id):
    groupe_id = request.form.get("groupe_id", type=int)

    with ouvrir_base() as conn:
        conn.execute("DELETE FROM depenses WHERE id = ?", [depense_id])

    return redirect(url_for("accueil", groupe_id=groupe_id))


if __name__ == "__main__":
    app.run(debug=True)