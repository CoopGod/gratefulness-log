# imports ------ python -m flask run
from xxlimited import new
import flask
from datetime import date
from flask import Flask, render_template, Markup, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.utils import redirect

# flask and postgres setup
app = Flask(__name__)
app.secret_key = "oh_so_secret"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:coopgod@localhost:5432/logs'
#os.environ.get("DATABASE_URLL")
db = SQLAlchemy(app)


#class defining user writings/entries 
class writings(db.Model):
    ID = db.Column(db.Integer, primary_key=True, nullable=False)
    date = db.Column(db.Date)
    grateful1 = db.Column(db.String)
    grateful2 = db.Column(db.String)
    grateful3 = db.Column(db.String)
    passage = db.Column(db.String)
    tag = db.Column(db.String)
    user_ID = db.Column(db.Integer)

    def __init__(self, date, g1, g2, g3, passage, tag, userID):
        self.date = date
        self.grateful1 = g1
        self.grateful2 = g2
        self.grateful3 = g3
        self.passage = passage
        self.tag = tag
        self.user_ID = userID

# class defining the user for login purposes
class users(db.Model):
    ID = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String)
    password = db.Column(db.String)

    def __init__(self, username, password):
        self.username = username
        self.password = password

# class defining users favorite entries
class favorites(db.Model):
    ID = db.Column(db.Integer, primary_key=True, nullable=False)
    user_ID = db.Column(db.Integer)
    log_ID = db.Column(db.Integer)

    def __init__(self, userID, logID):
        self.user_ID = userID
        self.log_ID = logID
    

# Home Page
@app.route("/", methods=['GET','POST'])
def index():
    # Validate username and password, continue if successful
    if flask.request.method == "POST":
        if request.form['button'] == 'signup':
            return redirect('/signup')
        else:
            username = request.values.get('formUser')
            password = request.values.get('formPass')
            validity = loginValidate(username, password)
            print(validity)
            if validity == True:
                session['user'] = username
                return redirect("/catalog")
            else:
                message = "Incorrect Username or Password!"
                return render_template("index.html", message=message)
    else:
        message = ""
        session['user'] = 'none'
        return render_template("index.html", message=message)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    error = ""
    if flask.request.method == "POST":
        username = request.values.get('formUser')
        password = request.values.get("formPass")
        new_user = makeUser(username, password)
        if new_user != False:  
            session['user'] = username
            return redirect("/catalog")
        else:
            error = "Username Already Taken!"
            return render_template("signup.html", error=error)

    else:
        return render_template("signup.html", error=error)
        

# Catalog page. See all your entries.
@app.route("/catalog", methods=['GET','POST'])
def catalog():
    if flask.request.method == "POST":
        return redirect('/newEntry')
    else:
        # table markup function
        activeUser = session["user"]
        infotable = tableMarkup(activeUser)
        return render_template('catalog.html', infotable=infotable)

# page to add entries
@app.route("/newEntry", methods=["GET","POST"])
def newEntry():
    if flask.request.method == "POST":
        g1 = request.values.get('g1')
        g2 = request.values.get('g2')
        g3 = request.values.get('g3')
        passage = request.values.get('passage')
        tag = request.values.get('tags')
        logWriting(g1, g2, g3, passage, tag)
        return redirect('/catalog')
    else:
        return render_template('add.html')

# Helper functions --------------------------------------------------------------------------------------------------------------
# function to create table markup for catalog page
def tableMarkup(user):
    userWritings = writings.query.order_by(desc(writings.ID)).filter_by(user_ID = f"{user}")
    infotable = Markup("")
    for row in userWritings:
        infotable = infotable + Markup(f"<tr><td>{row.grateful1}</td><td>{row.grateful2}</td> \
            <td>{row.grateful3}</td><td>{row.passage}</td><td>{row.tag}</td><td>{row.date}</td></tr> \
                <td><button name={row.ID}>Fav</button></td>")
    return infotable

# function to check username and password combinations. returns true if user is valid
def loginValidate(usernameVal, passwordVal):
    allUsers = users.query.filter_by(username = usernameVal)
    for row in allUsers:
        if row.password == passwordVal:
            return True
    return False

# function to check if username is already taken and if not, add it
def makeUser(usernameVal, passwordVal):
    allUsers = users.query.filter_by(username = usernameVal)
    userCount = allUsers.count()
    if userCount > 0:
        return False
    else:
        new_user = users(usernameVal, passwordVal)
        db.session.add(new_user)
        db.session.commit()

#funciton to create and submit row for SQL
def logWriting(g1, g2, g3, passage, tag):
    todaysDate = date.today()
    new_writing = writings(todaysDate, g1, g2, g3, passage, tag, session['user'])
    db.session.add(new_writing)
    db.session.commit()

# function to add favourite to list
def addFavourite(logID, userID):
    new_favourite = favorites(userID, logID)
    db.session.add(new_favourite)
    db.session.commit()
    

# Run flask app --------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
