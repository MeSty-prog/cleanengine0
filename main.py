from flask import Flask, request, redirect, session
import json
import os
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.permanent_session_lifetime = timedelta(days=30)

DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"users": {}}, f)


def load_data():
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    if "users" not in data:
        data["users"] = {}
    return data


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


# ========================
# GLOBAL STYLE
# ========================

STYLE = """
<style>
body{
    margin:0;
    font-family:Arial, sans-serif;
    background:linear-gradient(135deg,#1e3c72,#2a5298);
    color:white;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
}
.card{
    background:white;
    color:black;
    padding:30px;
    border-radius:15px;
    width:400px;
    box-shadow:0 10px 30px rgba(0,0,0,0.3);
}
input{
    width:100%;
    padding:10px;
    margin:8px 0;
    border-radius:8px;
    border:1px solid #ccc;
}
button{
    width:100%;
    padding:10px;
    border:none;
    border-radius:8px;
    background:#2a5298;
    color:white;
    font-weight:bold;
    cursor:pointer;
}
button:hover{
    background:#1e3c72;
}
a{
    text-decoration:none;
    color:#2a5298;
    font-weight:bold;
}
.stats{
    background:#f4f4f4;
    padding:15px;
    border-radius:10px;
    margin-top:15px;
}
.history{
    max-height:120px;
    overflow:auto;
    font-size:14px;
}
.logout{
    text-align:right;
    font-size:14px;
}
</style>
"""

# ========================
# REGISTER
# ========================
@app.route("/register", methods=["GET", "POST"])
def register():
    data = load_data()
    message = ""

    if request.method == "POST":
        name = request.form["name"]
        age = int(request.form["age"])
        password = request.form["password"]

        if name in data["users"]:
            message = "Bu kullanıcı zaten var!"
        else:
            data["users"][name] = {
                "age": age,
                "password": password,
                "total": 0,
                "pack_price": 60,
                "history": []
            }
            save_data(data)
            return redirect("/login")

    return f"""
    {STYLE}
    <div class="card">
        <h2>Kayıt Ol</h2>
        <form method="POST">
            <input name="name" placeholder="İsim" required>
            <input type="number" name="age" placeholder="Yaş" required>
            <input type="password" name="password" placeholder="Şifre" required>
            <button type="submit">Kayıt Ol</button>
        </form>
        <p>{message}</p>
        <p><a href="/login">Giriş Yap</a></p>
    </div>
    """


# ========================
# LOGIN
# ========================
@app.route("/login", methods=["GET", "POST"])
def login():
    data = load_data()
    message = ""

    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        if name in data["users"] and data["users"][name]["password"] == password:
            session.permanent = True
            session["user"] = name
            return redirect("/")
        else:
            message = "Hatalı giriş!"

    return f"""
    {STYLE}
    <div class="card">
        <h2>Giriş Yap</h2>
        <form method="POST">
            <input name="name" placeholder="İsim" required>
            <input type="password" name="password" placeholder="Şifre" required>
            <button type="submit">Giriş</button>
        </form>
        <p>{message}</p>
        <p><a href="/register">Kayıt Ol</a></p>
    </div>
    """


# ========================
# HOME
# ========================
@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect("/login")

    data = load_data()
    if session["user"] not in data["users"]:
        session.pop("user", None)
        return redirect("/login")

    user = data["users"][session["user"]]
    money = int((user["total"] / 20) * user["pack_price"])
    message = ""

    if request.method == "POST":
        today = int(request.form["smokes"])
        pack_price = float(request.form["price"])

        user["total"] += today
        user["pack_price"] = pack_price
        user["history"].append({
            "date": datetime.now().strftime("%d-%m-%Y %H:%M"),
            "smokes": today
        })

        save_data(data)

        messages = [
            "Kontrol sende.",
            "Azaltmaya devam!",
            "Ciğerlerin teşekkür ediyor.",
            "Her gün bir adım."
        ]
        message = random.choice(messages)
        money = int((user["total"] / 20) * user["pack_price"])

    history_html = ""
    for entry in reversed(user["history"]):
        history_html += f"<p>{entry['date']} → {entry['smokes']} sigara</p>"

    return f"""
    {STYLE}
    <div class="card">
        <div class="logout">
            <a href="/logout">Çıkış Yap</a>
        </div>
        <h2>CleanEngine 🚭</h2>
        <p>Hoşgeldin <b>{session['user']}</b></p>

        <form method="POST">
            <input type="number" name="smokes" placeholder="Bugün kaç sigara?" required>
            <input type="number" step="0.01" name="price" placeholder="Paket fiyatı (TL)" required>
            <button type="submit">Kaydet</button>
        </form>

        <div class="stats">
            <p><b>Toplam:</b> {user['total']} sigara</p>
            <p><b>Harcanan:</b> {money} TL</p>
            <p>{message}</p>
        </div>

        <div class="history">
            <h4>Geçmiş</h4>
            {history_html}
        </div>
    </div>
    """


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)