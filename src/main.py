"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Post #importo los tablas del la bd de models
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/post/<int:id>', methods=['DELETE'])
def delete_post(id):
    post_delete = Post.query.filter_by(id=id).delete()
    db.session.commit()
    return "todo ok",200

@app.route('/post', methods=['POST','GET'])
def new_post():
    if (request.method == 'POST'):
        body = request.get_json() #lo que viene de frontend lo paso a formato json
        create_post = Post(body['text']) #para crear el nuevo post instancio la clase Post y le paso text la variable que viene de frontend
        db.session.add(create_post) #añadiendo el nuevo post a la db
        db.session.commit() #guardando el cambio en la db
        print (create_post.serialize())
        return jsonify(create_post.serialize()), 201 #puedo enviar esta respuesta al cliente conviiendo la respuesta en json
    else:
        post_list = Post.query.all() #post_lis contiene todo lo post
        #convertir a diccionario el contenido de post_list creo una nueva lista y la lleno para mostrarla como diccionario
        new_list=[]
        for post in post_list:
            new_list.append(post.serialize())
        print(new_list)
        return jsonify(new_list), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
