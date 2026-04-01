from flask import Flask, render_template, request, session, redirect, url_for, flash
import pymongo
import os
import bcrypt
from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import re
import json

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------------
# A mettre que un fichier .env mais pas envie
client = pymongo.MongoClient(
    "mongodb+srv://labananeheureusedu92_db_user:Dx1S7hfG6W6kxthL@cluster0.myh4cg9.mongodb.net"
    "/?retryWrites=true&w=majority&appName=Cluster0"
)
db = client["Experiences"]

app.secret_key = "Dx1S7hfG6W6kxthL"

users_collection = db["users"]
experiences_collection = db["experiences"]

# ---------------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------------

def _gen_mouse_trail(color, size, speed, gravity):
    """Retourne le code JS pour un dessin en traînée de souris."""
    return f'''function setup() {{
  let container = document.getElementById('p5-container');
  let cnv = createCanvas(container.offsetWidth, 400);
  cnv.parent('p5-container');
  background(220);
}}

function draw() {{
  if (mouseIsPressed) {{
    fill('{color}');
    noStroke();
    ellipse(mouseX, mouseY, {size}, {size});
  }}
}}

function windowResized() {{
  let container = document.getElementById('p5-container');
  resizeCanvas(container.offsetWidth, 400);
}}'''


def _gen_gravity(color, size, speed, gravity):
    """Génère du JS pour des balles soumises à la gravité et rebondissant."""
    return f'''let balls = [];

function setup() {{
  let container = document.getElementById('p5-container');
  let cnv = createCanvas(container.offsetWidth, 400);
  cnv.parent('p5-container');
}}

function draw() {{
  background(220);
  
  // Ajouter une nouvelle balle de temps en temps quand la souris est enfoncée
  if (mouseIsPressed && frameCount % 10 === 0) {{
    balls.push({{
      x: mouseX,
      y: mouseY,
      vx: random(-2, 2),
      vy: 0
    }});
  }}
  
  // Mettre à jour et afficher chaque balle
  for (let ball of balls) {{
    ball.vy += {gravity}; // gravité accélère vers le bas
    ball.x += ball.vx * {speed};
    ball.y += ball.vy * {speed};
    
    // Rebondir sur les bords horizontaux
    if (ball.x < {size/2} || ball.x > width - {size/2}) {{
      ball.vx *= -0.8;
      ball.x = constrain(ball.x, {size/2}, width - {size/2});
    }}
    if (ball.y > height - {size/2}) {{
      ball.vy *= -0.8;
      ball.y = height - {size/2};
    }}
    
    fill('{color}');
    ellipse(ball.x, ball.y, {size}, {size});
  }}
}}

function windowResized() {{
  let container = document.getElementById('p5-container');
  resizeCanvas(container.offsetWidth, 400);
}}'''


def _gen_particles(color, size, speed, gravity):
    """Génère un système de particules qui disparaissent progressivement."""
    return f'''let particles = [];

function setup() {{
  let container = document.getElementById('p5-container');
  let cnv = createCanvas(container.offsetWidth, 400);
  cnv.parent('p5-container');
}}

function draw() {{
  background(220, 10);
  
  // Ajouter des particules tant que la souris est enfoncée
  if (mouseIsPressed) {{
    for (let i = 0; i < 5; i++) {{
      particles.push({{
        x: mouseX + random(-10, 10),
        y: mouseY + random(-10, 10),
        vx: random(-{speed*2}, {speed*2}),
        vy: random(-{speed*2}, {speed*2}),
        life: 255
      }});
    }}
  }}
  
  // Mettre à jour et dessiner les particules, en retirant les mortes
  for (let i = particles.length - 1; i >= 0; i--) {{
    let p = particles[i];
    p.x += p.vx;
    p.y += p.vy;
    p.vy += {gravity} * 0.1;
    p.life -= 2;
    
    if (p.life <= 0) {{
      particles.splice(i, 1);
    }} else {{
      fill('{color}' + hex(floor(p.life), 2));
      noStroke();
      ellipse(p.x, p.y, {size} * (p.life / 255), {size} * (p.life / 255));
    }}
  }}
}}

function hex(value, digits) {{
  return ('0'.repeat(digits) + value.toString(16)).slice(-digits);
}}

function windowResized() {{
  let container = document.getElementById('p5-container');
  resizeCanvas(container.offsetWidth, 400);
}}'''


def _gen_bouncing_ball(color, size, speed, gravity):
    """Boule rebondissante simple inversant sa vitesse aux bords."""
    return f'''let x = 300;
let y = 200;
let vx = {speed};
let vy = {speed};

function setup() {{
  let container = document.getElementById('p5-container');
  let cnv = createCanvas(container.offsetWidth, 400);
  cnv.parent('p5-container');
}}

function draw() {{
  background(220);
  
  // update position
  x += vx;
  y += vy;
  
  // rebondir sur les bords
  if (x < {size/2} || x > width - {size/2}) {{
    vx *= -1;
  }}
  if (y < {size/2} || y > height - {size/2}) {{
    vy *= -1;
  }}
  
  fill('{color}');
  ellipse(x, y, {size}, {size});
}}

function windowResized() {{
  let container = document.getElementById('p5-container');
  resizeCanvas(container.offsetWidth, 400);
}}'''


def _gen_rain(color, size, speed, gravity):
    """Génère des gouttes de pluie; réapparaissent en bas de l'écran."""
    return f'''let drops = [];

function setup() {{
  let container = document.getElementById('p5-container');
  let cnv = createCanvas(container.offsetWidth, 400);
  cnv.parent('p5-container');
  for (let i = 0; i < 100; i++) {{
    drops.push({{
      x: random(width),
      y: random(-500, 0),
      speed: random({speed*0.5}, {speed*2})
    }});
  }}
}}

function draw() {{
  background(220);
  
  for (let drop of drops) {{
    drop.y += drop.speed;
    if (drop.y > height) {{
      drop.y = random(-100, 0);
      drop.x = random(width);
    }}
    
    stroke('{color}');
    strokeWeight(2);
    line(drop.x, drop.y, drop.x, drop.y + {size});
  }}
}}

function windowResized() {{
  let container = document.getElementById('p5-container');
  resizeCanvas(container.offsetWidth, 400);
  // rebuild drops when the size changes
  drops = [];
  for (let i = 0; i < 100; i++) {{
    drops.push({{
      x: random(width),
      y: random(-500, 0),
      speed: random({speed*0.5}, {speed*2})
    }});
  }}
}}'''


def _gen_fireworks(color, size, speed, gravity):
    """Animation de feux d'artifice avec classes Firework et Particle."""
    return f'''let fireworks = [];

function setup() {{
  let container = document.getElementById('p5-container');
  let cnv = createCanvas(container.offsetWidth, 400);
  cnv.parent('p5-container');
}}

function draw() {{
  background(20, 20, 40);
  
  if (mouseIsPressed && random() < 0.1) {{
    fireworks.push(new Firework(mouseX, height));
  }}
  
  for (let i = fireworks.length - 1; i >= 0; i--) {{
    fireworks[i].update();
    fireworks[i].show();
    if (fireworks[i].done()) {{
      fireworks.splice(i, 1);
    }}
  }}
}}

class Firework {{
  constructor(x, y) {{
    this.x = x;
    this.y = y;
    this.particles = [];
    this.exploded = false;
    
    for (let i = 0; i < 30; i++) {{
      this.particles.push(new Particle(this.x, this.y));
    }}
  }}
  
  update() {{
    if (!this.exploded) {{
      this.y -= {speed*3};
      if (this.y < height * 0.3) {{
        this.exploded = true;
      }}
    }}
    
    for (let particle of this.particles) {{
      particle.update();
    }}
  }}
  
  show() {{
    if (!this.exploded) {{
      fill('{color}');
      ellipse(this.x, this.y, {size/2}, {size/2});
    }}
    
    for (let particle of this.particles) {{
      particle.show();
    }}
  }}
  
  done() {{
    return this.exploded && this.particles.every(p => p.done());
  }}
}}

class Particle {{
  constructor(x, y) {{
    this.x = x;
    this.y = y;
    this.vx = random(-{speed*2}, {speed*2});
    this.vy = random(-{speed*2}, {speed*2});
    this.alpha = 255;
  }}
  
  update() {{
    this.x += this.vx;
    this.y += this.vy;
    this.vy += {gravity} * 0.1;
    this.alpha -= 2;
  }}
  
  show() {{
    noStroke();
    fill('{color}' + hex(floor(this.alpha), 2));
    ellipse(this.x, this.y, {size/3}, {size/3});
  }}
  
  done() {{
    return this.alpha <= 0;
  }}
}}

function hex(value, digits) {{
  return ('0'.repeat(digits) + value.toString(16)).slice(-digits);
}}

function windowResized() {{
  let container = document.getElementById('p5-container');
  resizeCanvas(container.offsetWidth, 400);
}}'''


def generate_visual_code(config):
    """Génère du code JavaScript à partir d'une configuration visuelle.

    clés de config :
      * type : l'une de 'mouse-trail', 'gravity', 'particles', 'bouncing-ball',
        'rain', 'fireworks'
      * color, size, speed, gravity sont des valeurs numériques/chaînes
        utilisées par chaque générateur.
    """
    exp_type = config.get('type', 'mouse-trail')
    color = config.get('color', '#ff0000')
    size = config.get('size', 20)
    speed = config.get('speed', 1.0)
    gravity = config.get('gravity', 0.5)

    generators = {
        'mouse-trail': _gen_mouse_trail,
        'gravity': _gen_gravity,
        'particles': _gen_particles,
        'bouncing-ball': _gen_bouncing_ball,
        'rain': _gen_rain,
        'fireworks': _gen_fireworks,
    }

    gen = generators.get(exp_type, _gen_mouse_trail)
    return gen(color, size, speed, gravity)

# ---------------------------------------------------------------------------
# Routes Flask
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    """Page d'accueil : affiche toutes les expériences, les plus récentes en premier."""

    experiences = list(experiences_collection.find().sort("date", -1))

    for exp in experiences:
        # backfill missing fields for old documents
        if 'type' not in exp:
            if 'steps' not in exp:
                exp['steps'] = [
                    {'type': 'text', 'content': exp.get('description', '')}
                ]
            exp['type'] = 'narrative'
        if 'plays' not in exp:
            exp['plays'] = 0

    return render_template('index.html', experiences=experiences)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Gère la connexion utilisateur ; enregistre la session en cas de succès."""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({"username": username})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            if user.get('banned', False):
                flash('Votre compte est banni.')
                return redirect(url_for('login'))
            session['username'] = username
            flash('Connexion réussie !')
            return redirect(url_for('index'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Point d'accès pour l'inscription d'un utilisateur."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users_collection.find_one({"username": username}):
            flash('Nom d\'utilisateur déjà pris.')
        else:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            users_collection.insert_one({"username": username, "password": hashed})
            flash('Inscription réussie ! Vous pouvez maintenant vous connecter.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Créer une nouvelle expérience (code ou visuelle)."""
    if 'username' not in session:
        flash('Vous devez être connecté pour créer une expérience.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        experience_type = request.form.get('experience_type', 'code')
        author = session['username']
        date = datetime.now()

        if experience_type == 'visual':
            visual_config = request.form.get('visual_config', '{}')
            try:
                config = json.loads(visual_config)
                code = generate_visual_code(config)
            except json.JSONDecodeError:
                flash('Configuration invalide.')
                return redirect(url_for('create'))
        else:
            code = request.form['code']

        experience = {
            "title": title,
            "description": description,
            "code": code,
            "author": author,
            "date": date,
            "plays": 0,
            "type": "interactive",
            "creation_mode": experience_type,
        }

        experiences_collection.insert_one(experience)
        flash('Expérience créée avec succès !')
        return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/play/<experience_id>')
def play(experience_id):
    """Jouer une expérience identifiée par son ObjectId."""
    try:
        experience = experiences_collection.find_one({"_id": ObjectId(experience_id)})
        if not experience:
            flash('Expérience non trouvée.')
            return redirect(url_for('index'))

        experiences_collection.update_one(
            {"_id": ObjectId(experience_id)},
            {"$inc": {"plays": 1}}
        )
        return render_template('play.html', experience=experience)
    except Exception:
        flash('ID d\'expérience invalide.')
        return redirect(url_for('index'))

@app.route('/admin')
def admin():
    """Tableau de bord admin avec listes des utilisateurs et expériences."""
    if 'username' not in session or session['username'] != 'Admin':
        return redirect(url_for('login'))
    users = list(users_collection.find())
    experiences = list(experiences_collection.find())
    total_plays = sum(exp.get('plays', 0) for exp in experiences)
    
    # Statistiques supplémentaires
    banned_users = [u for u in users if u.get('banned', False)]
    active_users = [u for u in users if not u.get('banned', False)]
    
    # Top expériences par plays
    top_experiences = sorted(experiences, key=lambda x: x.get('plays', 0), reverse=True)[:5]
    
    # Utilisateurs avec le plus d'expériences
    user_exp_counts = {}
    for exp in experiences:
        creator = exp.get('creator')
        if creator:
            user_exp_counts[creator] = user_exp_counts.get(creator, 0) + 1
    top_creators = sorted(user_exp_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return render_template('admin/admin.html', users=users, experiences=experiences, total_plays=total_plays,
                           banned_users=banned_users, active_users=active_users, top_experiences=top_experiences,
                           top_creators=top_creators)

@app.route('/delete_experience/<experience_id>', methods=['POST'])
def delete_experience(experience_id):
    """Supprimer une expérience ; réservé à l'admin."""
    if 'username' not in session or session['username'] != 'Admin':
        return redirect(url_for('login'))
    try:
        experiences_collection.delete_one({'_id': ObjectId(experience_id)})
        flash('Expérience supprimée avec succès.')
    except Exception:
        flash('Erreur lors de la suppression.')
    return redirect(url_for('admin'))

@app.route('/ban_user/<username>', methods=['POST'])
def ban_user(username):
    """Marquer un utilisateur comme banni ; admin uniquement."""
    if 'username' not in session or session['username'] != 'Admin':
        return redirect(url_for('login'))
    users_collection.update_one({'username': username}, {'$set': {'banned': True}})
    flash(f'Utilisateur {username} banni.')
    return redirect(url_for('admin'))

@app.route('/unban_user/<username>', methods=['POST'])
def unban_user(username):
    """Retirer le bannissement d'un utilisateur ; admin uniquement."""
    if 'username' not in session or session['username'] != 'Admin':
        return redirect(url_for('login'))
    users_collection.update_one({'username': username}, {'$set': {'banned': False}})
    flash(f'Utilisateur {username} autorisé.')
    return redirect(url_for('admin'))

@app.route('/admin/user/<username>')
def admin_user_detail(username):
    """Détails d'un utilisateur pour l'admin."""
    if 'username' not in session or session['username'] != 'Admin':
        return redirect(url_for('login'))
    user = users_collection.find_one({'username': username})
    if not user:
        flash('Utilisateur non trouvé.')
        return redirect(url_for('admin'))
    user_experiences = list(experiences_collection.find({'creator': username}))
    total_plays = sum(exp.get('plays', 0) for exp in user_experiences)
    return render_template('admin/user_detail.html', user=user, experiences=user_experiences, total_plays=total_plays)

@app.route('/admin/experience/<experience_id>')
def admin_experience_detail(experience_id):
    """Détails d'une expérience pour l'admin."""
    if 'username' not in session or session['username'] != 'Admin':
        return redirect(url_for('login'))
    try:
        experience = experiences_collection.find_one({'_id': ObjectId(experience_id)})
        if not experience:
            flash('Expérience non trouvée.')
            return redirect(url_for('admin'))
        return render_template('admin/experience_detail.html', experience=experience)
    except Exception:
        flash('Erreur lors de la récupération.')
        return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
