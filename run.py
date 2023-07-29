from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'uploads'  # Specify the folder to save uploaded pictures
app.config['STATIC_FOLDER'] = 'static'  # Specify the folder for static files
db = SQLAlchemy(app)

# Create the uploads and static directories if they don't exist
uploads_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

static_dir = os.path.join(app.root_path, app.config['STATIC_FOLDER'])
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Rest of the code remains the same

app.secret_key = 'your_secret_key'  # Set a secret key for session encryption


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    phone =  db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    items = db.relationship('Item', backref='user', lazy=True)



# Item model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    hostel = db.Column(db.String(50), nullable=False)
    picture = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref='items_owned')  # Change 'items' to 'items_owned'



with app.app_context():
    # Create the table
    db.create_all()


@app.route('/')
def index():
    if not session.get('username'):
        return redirect(url_for("login"))
    return render_template('index.html')


@app.route('/shop', methods=['GET', 'POST'])
def shop():
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        item_hostel = request.form.get('hostel')

        items_query = Item.query

        if item_name:
            items_query = items_query.filter(Item.name.ilike(f'%{item_name}%'))

        if item_hostel:
            items_query = items_query.filter(Item.hostel == item_hostel)

        items = items_query.all()
    else:
        items = Item.query.all()

    # Shuffle the items randomly
    random.shuffle(items)

    # Take the first 20 items or less if there are fewer items in the database
    random_items = items[:20]

    return render_template('shop.html', items=random_items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        phone = request.form['phone']
        password = request.form['password']
        session['username'] = username
        session['phone'] = phone

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            # If the login is successful, redirect to a success page
            return redirect(url_for('index'))
        else:
            # If the login is unsuccessful, render the login page with an error message
            return render_template('login.html', error='Invalid username or password')

    # Render the login page
    return render_template('login.html')


@app.route('/success')
def success():
    return "Login successful!"


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return 'Password and Confirm Password do not match'

        user = User.query.filter_by(username=username).first()
        if user:
            return 'Username already exists'

        new_user = User(username=username, password=password,email=email,phone=phone)
        db.session.add(new_user)
        db.session.commit()

        return render_template('index.html')

    return render_template('signup.html')


@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'POST':
        # Get the form data
        item_name = request.form['item_name']
        item_description = request.form['item_description']
        item_price = float(request.form['item_price'])
        item_hostel = request.form['hostel']
        item_picture = request.files['item_picture'] if 'item_picture' in request.files else None

        # Get the currently logged in user (you need to implement user authentication)
        user = User.query.get(1)  # Replace with the actual user ID

        # Create a new item and associate it with the user
        item = Item(
            name=item_name,
            description=item_description,
            price=item_price,
            hostel=item_hostel,
            user=user
        )

        # Handle the uploaded picture file
        if item_picture:
            # Save the picture file to the uploads folder
            picture_filename = secure_filename(item_picture.filename)
            item_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], picture_filename))
            item.picture = picture_filename

        # Add the item to the database
        db.session.add(item)
        db.session.commit()

        return render_template('index.html')

    return render_template('sell.html')


@app.route('/logout')
def logout():
    # Clear session data
    session.clear()

    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Serve uploaded files from the uploads folder
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if not session.get('username'):
        return redirect(url_for("login"))
        
    # Fetch reserved items for the currently logged in user (you need to implement user authentication)
    user = User.query.filter_by(username=session['username']).first()
    reserved_items = Item.query.filter_by(user_id=user.id).all()
    
    return render_template('reserve.html', reserved_items=reserved_items)

@app.route('/contact_owner', methods=['POST'])
def contact_owner():
    if not session.get('username'):
        return redirect(url_for("login"))

    if request.method == 'POST':
        item_id = request.form.get('item_id')

        # Fetch the item from the database based on the item_id
        item = Item.query.filter_by(id=item_id).first()

        if not item:
            return 'Item not found.'

        # Get the owner of the item
        owner = item.owner

        # Render the owner_details template and pass the owner object to it
        return render_template('owner_details.html', owner=owner)

    return 'Invalid request.'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
