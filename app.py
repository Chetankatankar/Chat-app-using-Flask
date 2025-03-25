from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from datetime import datetime

# Connect to MySQL server
cnx = mysql.connector.connect(
    host="127.0.0.1",
    port="3306",
    user="root",
    password="chetan",
    database="python" )

#cursor object
cur = cnx.cursor()

#object of flask class
app = Flask(__name__)
app.secret_key = "chetan"
#route for register page
@app.route('/')
def home():
    return render_template('register.html')

@app.route('/getdata', methods=['post'])
def getdata():
    # id = request.form['id']
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    city = request.form['city']
    q = "INSERT INTO users (username, email, password, city) VALUES (%s, %s, %s, %s)"
    cur.execute(q, (username, email, password, city))
    cnx.commit()
    return redirect(url_for("login"))

    
#route for login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if "email" in request.form and "password" in request.form:  
            email = request.form["email"]
            password = request.form["password"]

            cur.execute("SELECT id, username FROM users WHERE email = %s AND password = %s", (email, password))
            user = cur.fetchone()

            if user:
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect("/showusers")
            else:
                return "Invalid credentials!"

    return render_template("login.html")


#route for user list
@app.route("/showusers")
def showusers():
    cur.execute("SELECT id, username FROM users WHERE id != %s", (session['user_id'],))
    users = cur.fetchall()
    return render_template("showusers.html", users=users)


@app.route("/chat",methods=["GET", "POST"])
def chat():
    receiver_id = request.args['receiver_id']
    
    q = "SELECT users.username, chatbox.message, chatbox.timestamp FROM chatbox INNER JOIN users ON chatbox.sender_id = users.id WHERE receiver_id=%s AND sender_id=%s"
    cur.execute(q, (session['user_id'] , receiver_id))
    res = cur.fetchall()
    q = "SELECT  users.username, chatbox.message, chatbox.timestamp FROM chatbox INNER JOIN users ON chatbox.sender_id = users.id WHERE receiver_id=%s AND sender_id=%s" 
    cur.execute(q, (receiver_id, session['user_id']))
    res2 = cur.fetchall()
    return render_template('chat.html', receiver_id=receiver_id, res=res, res2=res2)


@app.route("/sendmsg", methods=['POST'])
def sendmsg():
    receiver_id = request.form['receiver_id'];
    msg = request.form['msg']
    sender_id = session['user_id']
    # timestamp = datetime.now()

    q = "INSERT INTO chatbox (sender_id, receiver_id, message, timestamp) VALUES (%s, %s, %s, %s)"
    cur.execute(q, (sender_id, receiver_id, msg, datetime.now()))
    cnx.commit()
    return redirect(url_for('chat', receiver_id=receiver_id))


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
