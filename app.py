from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
mongo = PyMongo(app)

plants_collection = mongo.db.plants
harvests_collection = mongo.db.harvests


############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""
    plants_data = plants_collection.find()

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        name = request.form.get('plant_name')
        variety = request.form.get('variety')
        photo_url = request.form.get('photo')
        date_planted = request.form.get('date_planted')
        new_plant = {
            'name': name,
            'variety': variety,
            'photo_url': photo_url,
            'date_planted': date_planted
        }
        returned_value = plants_collection.insert_one(new_plant)
        return redirect(url_for('detail', plant_id=returned_value.inserted_id))

    else:
        return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""

    plant_to_show = plants_collection.find_one({'_id': ObjectId(plant_id)})

    harvests = harvests_collection.find({'_id': ObjectId(plant_id)})

    context = {
        'plant' : plant_to_show,
        'harvests': harvests
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """

    quantity = request.form.get('harvested_amount')
    date = request.form.get('date_planted')

    new_harvest = {
        'quantity': quantity, 
        'date': date,
        'plant_id': plant_id
    }

    harvests_collection.insert_one(new_harvest)

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""
    if request.method == 'POST':
        query = {'_id': ObjectId(plant_id)}
        new_values = { "$set": {
            'name': request.form.get('plant_name'),
            'variety': request.form.get('variety'),
            'photo_url': request.form.get('photo'),
            'date_planted': request.form.get('date_planted'),
        } } 
        plants_collection.update_one(query, new_values)
        
        return redirect(url_for('detail', plant_id=plant_id))
    else:
        plant_to_show = plants_collection.find_one({'_id': ObjectId(plant_id)})

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    query = {'_id': ObjectId(plant_id)}

    plants_collection.delete_one(query)

    harvests_collection.delete_many(query)

    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)

