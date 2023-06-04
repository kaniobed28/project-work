from flask import Flask, render_template, request,redirect,url_for,session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' 
db = SQLAlchemy(app)

app.secret_key = 'your_secret_key'  # Set a secret key for session encryption


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)


with app.app_context():
    # Create the table
    db.create_all()

@app.route('/')
def index():
    if not session.get('username'):
        return redirect(url_for("login"))
    return render_template('index.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        
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
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return 'Password and Confirm Password do not match'
        
        user = User.query.filter_by(username=username).first()
        if user:
            return 'Username already exists'
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        return render_template('index.html')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    # Clear session data
    session.clear()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 