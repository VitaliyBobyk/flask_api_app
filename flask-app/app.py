import json
import requests
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify
import os
from flask_marshmallow import Marshmallow

# init App
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
ma = Marshmallow(app)

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init DB
db = SQLAlchemy(app)


# Configure Users
class RandomUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    login = db.Column(db.String(150))
    password = db.Column(db.String(150))
    email = db.Column(db.String(150))
    phone = db.Column(db.String)

    def __init__(self, first_name, last_name, login, password, email, phone):
        self.first_name = first_name
        self.last_name = last_name
        self.login = login
        self.password = password
        self.email = email
        self.phone = phone


# Create DB
db.create_all()


# Configure MA
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'login', 'password', 'email', 'phone')


# Init UserSchema
many_user_schema = UserSchema(many=True)
one_user_schema = UserSchema(many=False)

# Get random users
response = requests.get("https://randomuser.me/api/?results=50&gender=male&inc=gender,name,email,phone,login&nat=gb")

todos = json.loads(response.text)


for i in todos['results']:
    first_name = i['name']['first']
    last_name = i['name']['last']
    login = i['login']['username']
    password = i['login']['password']
    email = i['email']
    phone = i['phone']

    add_user = RandomUser(first_name, last_name, login, password, email, phone)
    db.session.add(add_user)
    db.session.commit()


# List all data from a collection
@app.route('/all_users', methods=['GET'])
def get_users():
    all_users = RandomUser.query.all()
    result = many_user_schema.dump(all_users)
    return jsonify(result)


# Get one specified entity
@app.route('/user/<id>', methods=['GET'])
def one_user(id):
    user = RandomUser.query.get(id)
    if user is None:
        return jsonify({'User does\'nt exist!': ''})
    return one_user_schema.jsonify(user)


# Delete one specified entity
@app.route('/delete/user/<id>', methods=['GET', 'DELETE'])
def delete_user(id):
    try:
        user = RandomUser.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'You successfully deleted user:': user.first_name})
    except:
        return jsonify({'User does\'nt exist!': ''})


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=int(os.environ.get("PORT", 5000)))
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
