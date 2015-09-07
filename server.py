from flask import Flask, render_template, request, redirect,session, jsonify, abort
from bankid.client import BankIDClient
from storage import MemoryStorage

client = BankIDClient(certificates=('certs/cert.pem',
                                    'certs/key.pem'), test_server=True)



app = Flask(__name__)
app.secret_key = "derpderp"

def make_unicode(input):
    if type(input) != unicode:
        input =  input.decode('utf-8')
        return input
    else:
        return input

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/sign")
def sign():
    t = client.sign(user_visible_data="Testing a python lib",
                personal_number="199110013290")
    return render_template("sign.html", t=t)

@app.route("/api/auth/<personid>")
def api_auth(personid):
    t = client.authenticate(user_visible_data="Testing a python lib",
                personal_number=personid)
    return jsonify(t)

@app.route("/api/status/<token>")
def api_status(token):
    token = make_unicode(token)
    sto = MemoryStorage()
    try:
        t = client.collect(token)
        print(t)
        sto.put(token, t["progressStatus"])
        return jsonify(t["progressStatus"])
    except:
        print("Exception occured, attempting to use cached value...")

    r = sto.get(token)
    t = { 'progressStatus': r[0]}
    return jsonify(t)


@app.route("/auth")
def auth():
    t = client.authenticate(user_visible_data="Testing a python lib",
                personal_number="199110013290")
    return render_template("auth.html", t=t)

@app.route("/token/<token>")
def do_token(token):
    t = client.authenticate(user_visible_data="Testing a python lib",
                personal_number="199110013290")
    print(type(t['orderRef']))
    t2 = client.collect(t['orderRef'])
    return render_template("collect.html", t=t, t2=t2)

@app.route("/collect/<token>")
def collect(token):
    token = make_unicode(token)
    print(type(token))
    t2 = token
    t2 = client.collect(token)
    return render_template("collect.html", t2=t2)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method != "POST":
        return render_template("login.html")

    id = request.form["personal_number"]
    t = client.authenticate(user_visible_data="Testing a python lib",
                personal_number=id)
    return redirect("/waiting/{}".format(t["orderRef"]))


@app.route("/waiting/<token>")
def waiting(token):
    t2 = client.collect(token)

    print(t2)
    if t2["progressStatus"] == u'COMPLETE':
        session["username"] = t2["userInfo"]["name"]
        return redirect("/done")

    return render_template("waiting.html", t2=t2)

@app.route("/done")
def done():
    return render_template("authed.html", name=session["username"])


if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0")
