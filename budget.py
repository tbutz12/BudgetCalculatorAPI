import json
from json import JSONEncoder
from flask import Flask, request, abort, url_for, redirect, session, render_template, flash, jsonify
from models import db, User, Categories, PurchaseList, AlchemyEncoder
from datetime import datetime
from sqlalchemy import exc
from flask_restful import reqparse, abort, Api, Resource
from pprint import pprint
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)

cID = 1

parser = reqparse.RequestParser()
parser.add_argument('category', type=str,help='category should be a string')
parser.add_argument('purchase', type=str,help='purchase name should be a string')

@app.cli.command('initdb')
def initdb_command():
    db.create_all()

db.init_app(app)

with app.app_context():
    db.create_all()

users = {}

@app.route("/", methods=['GET'])
def homepage():
    if "username" not in session:
        return redirect(url_for("login"))
    else:
        return render_template("homepage.html")

class Category(Resource):
    def get(self, cat_name):
        for instance in User.query:
            if instance.username == session["username"]:
                userID = instance.id
        userCat = Categories.query.filter_by(user_id=userID).all()
        catCheck = userCat.categoryName
        catName = Categories.query.filter_by(categoryName=catCheck).scalar()
        return json.dumps(catName, cls=AlchemyEncoder)
    def delete(self, cat_name):
        for x in PurchaseList.query:
            if x.categoryName == cat_name:
                x.categoryName = "uncategorized"
                db.session.commit()
        Categories.query.filter_by(categoryName=cat_name).delete()
        db.session.commit()
        return '', 204
    def post(self, cat_name):
        global cID
        parser.add_argument('CategoryName')
        parser.add_argument('budgetedAmount')
        args = parser.parse_args()
        categoryName = args['CategoryName']
        amount = args['budgetedAmount']
        for instance in User.query:
            if instance.username == session["username"]:
                userID = instance.id
        q = Categories(cID, categoryName, amount)
        db.session.add(q)
        db.session.commit()
        cID += 1
        for x in Categories.query:
            if x.categoryName == cat_name:
                x.user_id = userID
        db.session.commit()
        categories = Categories.query.filter_by(categoryName=cat_name).scalar()
        return json.dumps(categories, cls=AlchemyEncoder), 201

class CategoryList(Resource):
    def get(self):
        for instance in User.query:
            if instance.username == session["username"]:
                userID = instance.id
        userCat = Categories.query.filter_by(user_id=userID).all()
        return json.dumps(userCat, cls=AlchemyEncoder)
    def post(self):
        global cID
        parser.add_argument('CategoryName')
        parser.add_argument('budgetedAmount')
        args = parser.parse_args()
        categoryName = args['CategoryName']
        amount = args['budgetedAmount']
        for instance in User.query:
            if instance.username == session["username"]:
                userID = instance.id
        q = Categories(cID, categoryName, amount)
        db.session.add(q)
        db.session.commit()
        cID += 1
        for x in Categories.query:
            if x.categoryName == categoryName:
                x.user_id = userID
        db.session.commit()
        return json.dumps(q, cls=AlchemyEncoder), 201

class PurchasesList(Resource):
    def get(self):
        for instance in User.query:
            if instance.username == session["username"]:
                userID = instance.id
        userPurchases = PurchaseList.query.filter_by(user_id=userID).all()
        return json.dumps(userPurchases, cls=AlchemyEncoder)

    def post(self):
        for instance in User.query:
            if instance.username == session["username"]:
                userID = instance.id
        parser.add_argument('Name')
        parser.add_argument('CategoryName')
        parser.add_argument('Amount')
        parser.add_argument('Date', type=str, help='Should be a string in form MM/DD/YY')
        args = parser.parse_args()
        name = args["Name"]
        catName = args["CategoryName"]
        amount = args['Amount']
        date = args["Date"]
        newPurchase = None
        if(validate(date)):
            newPurchase = PurchaseList(name, catName, amount, date)
            db.session.add(newPurchase)
            db.session.commit()
        for c in Categories.query:
            if c.categoryName == catName:
                catID = c.id
        for x in PurchaseList.query:
            if x.categoryName == catName:
                x.user_id = userID
                x.category_id = catID
                db.session.commit()
        return json.dumps(newPurchase, cls=AlchemyEncoder), 201

@app.route("/login/", methods=["GET", "POST"])
def login():
    result = User.query.all()
    if "username" in session:
        return redirect(url_for("homepage", username=session["username"]))

    elif request.method == "POST":
        len = User.query.count()
        print(len)
        for r in result:
            print(r.username)
            print(request.form["user"])
            print(r.password)
            print(request.form["pass"])
            if r.username == request.form["user"] and r.password == request.form["pass"]:
                session["username"] = r.username
                userName = r.username
                if(userName not in users):
                    users[userName] = r.password
                return redirect(url_for("homepage", username=r.username)) 
            else:
                len -= 1
                if(len == 0):
                    return render_template("login.html", flag = True)
    return render_template("login.html")

def validate(date_text):
    try:
        if date_text != datetime.strptime(date_text, "%m/%d/%Y %H:%M").strftime('%m/%d/%Y %H:%M'):
            raise ValueError
        return True
    except ValueError:
        return False

@app.route("/registration/", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        userName = request.form["user"]
        qUser = User.query.all()
        for u in qUser:
            users[u.username] = u.password
        if(userName in users):
            return render_template("registration.html", flag1 = True)
        users[userName] = request.form["pass"]
        if(len(userName) == 0):
            return render_template("registration.html", flag2 = True)
        passW = request.form["pass"]
        if(len(passW) == 0):
            return render_template("registration.html", flag3 = True)
        q = User(userName, passW)
        db.session.add(q)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("registration.html")

@app.route("/logout/")
def logout():
    if "username" in session:
        session.clear()
        return render_template("logoutPage.html")
    else:
        return redirect(url_for("login"))

api.add_resource(CategoryList, '/cats')
api.add_resource(Category, '/cats/<cat_name>')
api.add_resource(PurchasesList, '/purchases')

app.secret_key = "asdf;lkj"
            
if __name__ == "__main__":
    app.run()

