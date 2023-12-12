from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson import ObjectId
import datetime

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/productDb"
mongo = PyMongo(app)


@app.route('/products', methods=['GET'])
def get_products():
    products = mongo.db.products.find()
    return jsonify([
        {
            'id': str(product['_id']),
            'name': product['name'],
            'price': product['price'],
            'description': product['description'],
            'stock': product['stock'],
            'status': product.get('status', 'Available')
        }
        for product in products
    ])


@app.route('/product/<product_id>', methods=['GET'])
def get_product(product_id):
    product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
    if product:
        product.setdefault('status', 'Available')
        return jsonify({'id': str(product['_id']), 'name': product['name'], 'price': product['price'], 'description': product['description'], 'stock': product['stock'], 'status': product['status']})
    else:
        return jsonify({"message": "Product not found"}), 404
    
    
@app.route('/product/<product_id>/history', methods=['GET'])
def get_product_history(product_id):
    history = mongo.db.product_history.find({'product_id': ObjectId(product_id)})
    return jsonify([{
        'timestamp': record['timestamp'],
        'changes': { 
            key: {'old': str(change['old']), 'new': str(change['new'])} for key, change in record['changes'].items()
        } if record.get('changes') else record.get('changes')
    } for record in history])



@app.route('/product', methods=['POST'])
def add_product():
    data = request.json
    if 'price' in data and data['price'] < 0:
        return jsonify({"message": "Negative price is not allowed"}), 400

    data['status'] = 'Available'
    result = mongo.db.products.insert_one(data)
    new_product_id = result.inserted_id

    # Log product creation
    log_product_change(new_product_id, {}, data)

    new_product = mongo.db.products.find_one({'_id': new_product_id})
    return jsonify({
        'id': str(new_product['_id']),
        'name': new_product['name'],
        'price': new_product['price'],
        'description': new_product['description'],
        'stock': new_product['stock'],
        'status': new_product['status']
    }), 201


@app.route('/product/<product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    original_product = mongo.db.products.find_one({'_id': ObjectId(product_id)})

    if original_product:
        mongo.db.products.update_one({'_id': ObjectId(product_id)}, {'$set': data})
        updated_product = mongo.db.products.find_one({'_id': ObjectId(product_id)})

        if updated_product.get('stock', 1) <= 0:
            updated_product['status'] = 'Unavailable'
            mongo.db.products.update_one({'_id': ObjectId(product_id)}, {'$set': {'status': 'Unavailable'}})
        else:
            updated_product.setdefault('status', 'Available')

        log_product_change(product_id, original_product, data)

        return jsonify({'id': str(updated_product['_id']), 'name': updated_product['name'], 'price': updated_product['price'], 'description': updated_product['description'], 'stock': updated_product['stock'], 'status': updated_product['status']})
    else:
        return jsonify({"message": "Product not found"}), 404


@app.route('/product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
    if product:
        result = mongo.db.products.delete_one({'_id': ObjectId(product_id)})
        if result.deleted_count > 0:
            # Log product deletion
            log_product_change(product_id, product, None)
            return jsonify({"message": "Product deleted"})
        else:
            return jsonify({"message": "Product not found"}), 404
    else:
        return jsonify({"message": "Product not found"}), 404


def log_product_change(product_id, original_data, new_data):
    change_record = {
        'product_id': ObjectId(product_id),
        'timestamp': datetime.datetime.now(),
        'changes': {key: {'old': original_data.get(key), 'new': new_data.get(key)} for key in new_data} if new_data else 'Deleted'
    }
    mongo.db.product_history.insert_one(change_record)


if __name__ == '__main__':
    app.debug = True
    app.run()