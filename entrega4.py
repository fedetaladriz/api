from flask import Flask, jsonify, abort, request, render_template
from pymongo import MongoClient, TEXT
import sys
import json

# Se recomienda descargar el json de requests para postman,
# e importarlo en postman para probar las funciones.

#
# <?php
#     $data =  json_decode(json);
#
#     if (count($data->stand)) {
#         // Open the table
#         echo "<table>";
#
#         // Cycle through the array
#         foreach ($data->stand as $idx => $stand) {
#
#             // Output a row
#             echo "<tr>";
#             echo "<td>$stand->afko</td>";
#             echo "<td>$stand->positie</td>";
#             echo "</tr>";
#         }
#
#         // Close the table
#         echo "</table>";
#     }
# ?>



app = Flask(__name__)
# MONGODATABASE corresponde al nombre de su base de datos
MONGODATABASE = "entrega4"
MONGOSERVER = "localhost"
MONGOPORT = 27017
# instanciar el cliente de pymongo para realizar consultas a la base de datos
client = MongoClient(MONGOSERVER, MONGOPORT)



# Decorador defiene la ruta.
@app.route('/')
def hello_world():
    print("Hello World")
    return render_template("index.php")


@app.route('/sender/<int:user>', methods=['GET'])
def sender(user):
    mongodb = client[MONGODATABASE]
    collection = mongodb.messages
    output = []
    for s in collection.find({"sender": user}, {"_id": 0}):
        output.append(s)
    if len(output) == 0:
        return jsonify(), 404
    else:
        return jsonify(output), 200


@app.route('/user/<int:_id>', methods=['GET'])
def message(_id):
    mongodb = client[MONGODATABASE]
    mensajes = mongodb.messages
    usuarios = mongodb.usuarios
    output = []

    usuario = usuarios.find({"uid": _id}, {"_id": 0})
    for a in usuario:
        print(a)
        output.append(a)

    for s in mensajes.find({"sender": _id}, {"_id": 0}):
        output.append(s)

    if len(output) == 0:
        return jsonify(), 404
    else:
        return jsonify(output), 200


@app.route('/intercambiados/<int:_id1>/<int:_id2>', methods=['GET'])
def intercambiados(_id1, _id2):
    mongodb = client[MONGODATABASE]
    collection = mongodb.messages
    output = []
    resultado = []
    output1= []

    for t in collection.find({"sender": _id1}, {"_id": 0}):
        output.append(t)

    for t in collection.find({"sender": _id2}, {"_id": 0}):
        output1.append(t)

    for dic1 in output1:
        if dic1["receptant"]==_id1:
            resultado.append(dic1)

    for dic in output:
        if dic["receptant"]==_id2:
            resultado.append(dic)

    if len(resultado) == 0:
        return jsonify(), 404
    else:
        return jsonify(resultado), 200


@app.route('/add_message/', methods=['POST'])
def add_message():
    mongodb = client[MONGODATABASE]
    collection = mongodb.menssages

    data = request.get_json()

    inserted_message = collection.insert_one({
        'message': data["message"],
        'sender': data["sender"],
        'receptant': data["receptant"],
        'lat': data['lat'],
        'long': data["long"],
        'date':data["date"],
    })

    # insert_one retorna None si no pudo insertar
    if inserted_message is None:
        return jsonify(), 404
    # Retorna el id del elemento insertado
    else:
        return jsonify({"id": str(inserted_message.inserted_id)}), 200


@app.route('/remove_message/<int:msg_id>', methods=['DELETE'])
def remove_message(msg_id):
    mongodb = client[MONGODATABASE]
    messages = mongodb.messages

    result = messages.find()
    rm_id = result[msg_id]

    # messages.delete_one({'date': date})

    if result.deleted_count == 0:
        return jsonify(), 404
    else:
        return jsonify("Eliminado"), 200

@app.route('/busqueda/<string:txt>', methods=['GET'])
def busqueda(txt):
    mongodb = client[MONGODATABASE]
    mensajes = mongodb.messages
    mensajes.create_index([('message', TEXT)], name='search_index', default_language="english")
    output = []
    final = ""
    for word in txt.split("_"):
        tipo = word[0]
        word = word[1:]
        if tipo == "0":#0 --> obligatoria
            final += "\"{}\" ".format(word)
        elif tipo == "1":# 1--> opcional
            final += " {} ".format(word)
        elif tipo == "2": #2--> obligatoria:
            final += " -{} ".format(word)
    for s in mensajes.find({"$text": {"$search": final}}, {"_id": 0}):
        print(s)

        output.append(s)

    if len(output) == 0:
        return jsonify(), 404
    else:
        return jsonify(output), 200

if __name__ == '__main__':
    # Pueden definir su puerto para correr la aplicación
    app.run(port=5000)
