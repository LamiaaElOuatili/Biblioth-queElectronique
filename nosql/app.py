from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from pymongo import MongoClient
from bson import ObjectId
import datetime
from flask_wtf.csrf import CSRFProtect
import datetime
from neo4j import GraphDatabase



app = Flask(__name__)
csrf = CSRFProtect(app)
app.secret_key = 'supersecretkey'  # Change this to a long random string for security
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
csrf.init_app(app)
app.config['WTF_CSRF_ENABLED'] = True
login_manager.login_view = 'login'

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["Data_Library"]
users_collection = db["users"]
collection = db['books']
from bson import ObjectId

# Neo4j connection details
neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "Movies2024"
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

class User(UserMixin):
    def __init__(self, user_data):
        if '_id' not in user_data:
            user_data['_id'] = ObjectId()
        elif isinstance(user_data['_id'], str):
            user_data['_id'] = ObjectId(user_data['_id'])
        
        self.user_data = user_data
        self.booked_books = user_data.get('booked', [])
        self.role = user_data.get('role', 'user')  # Default role is 'user'

    def get_id(self):
        return str(self.user_data['_id'])
    
    @staticmethod
    def find_by_id(user_id):
        user_data = users_collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def find_by_email(email):
        user_data = users_collection.find_one({"email": email})
        if user_data:
            return User(user_data)
        return None

    @staticmethod
    def validate_login(password_hash, password):
        return bcrypt.check_password_hash(password_hash, password)

    def save_to_db(self):
        users_collection.update_one({"_id": self.user_data['_id']}, {"$set": self.user_data}, upsert=True)

    def book_book(self, book_id):
        # Check if the user has already booked 3 books
        active_bookings = [book for book in self.booked_books if not book['returned']]
        if len(active_bookings) >= 3:
            return False, "You can't book more than 3 books"

        if not any(book['book_id'] == book_id and not book['returned'] for book in self.booked_books):
            self.booked_books.append({
                'book_id': book_id,
                'date_booked': datetime.datetime.now(),
                'returned': False
            })
            self.user_data['booked'] = self.booked_books
            self.save_to_db()
            return True, "Booked successfully"
        return False, "Book already booked"


@app.route('/book/<book_id>', methods=['POST'])
@login_required
def book_book(book_id):
    book = collection.find_one({"_id": ObjectId(book_id)})
    if not book:
        return jsonify({'message': 'Book not found'}), 404

    success, message = current_user.book_book(book_id)
    if success:
        if book.get('quantity', 0) > 0:
            collection.update_one({"_id": ObjectId(book_id)}, {"$inc": {"quantity": -1}})
            return jsonify({'message': message, 'alreadyBooked': False}), 200
        else:
            flash('No more copies available!', 'warning')
            return jsonify({'message': 'No more copies available', 'alreadyBooked': False}), 400
    else:
        flash(message, 'warning')
        return jsonify({'message': message, 'alreadyBooked': True}), 400
    
    
@app.route('/book/<book_id>')
@login_required
def book_details(book_id):
    book = collection.find_one({"_id": ObjectId(book_id)})
    if not book:
        flash('Book not found', 'danger')
        return redirect(url_for('index'))
    
    return render_template('book_details.html', book=book)




from functools import wraps
from flask import abort

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)  # HTTP status code for Forbidden
        return f(*args, **kwargs)
    return decorated_function




# Load user callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = users_collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data)
    except Exception as e:
        print(f"Error loading user: {e}")
    return None


from wtforms import RadioField

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    role = RadioField('Role', choices=[('user', 'User'), ('admin', 'Admin')], default='user')
    submit = SubmitField('Register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        role = form.role.data

        if User.find_by_email(email):
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User({
            "username": username,
            "email": email,
            "password": password_hash,
            "role": role
        })

        new_user.save_to_db()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)



# Login route
# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.find_by_email(email)
        if user and User.validate_login(user.user_data['password'], password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('login.html')



# Logout route
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return render_template('login.html')

@app.route('/update-quantity/<id>', methods=['PUT'])
def update_quantity(id):
    try:
        # Check the current quantity of the book
        book = collection.find_one({"_id": ObjectId(id)})
        if not book:
            return jsonify({'message': 'Book not found'}), 404
        
        current_quantity = book.get('quantity', 0)
        if current_quantity <= 0:
            return jsonify({'message': 'Quantity cannot be decremented below 0'}), 400

        # Decrement the quantity field by 1
        result = collection.update_one({"_id": ObjectId(id)}, {"$inc": {"quantity": -1}})
        
        # Check if the update was successful
        if result.modified_count == 1:
            return jsonify({'message': 'Quantity updated successfully'}), 200
        else:
            return jsonify({'message': 'Failed to update quantity'}), 500
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/')
@login_required
def index():
    if current_user.role == 'admin':
        return redirect(url_for('admin'))
    else:
        books = list(collection.find())
        
        # Get the current user's booked books IDs
        booked_books_ids = [str(book['book_id']) for book in current_user.user_data.get('booked', [])]
        
        for book in books:
            book['is_booked'] = str(book['_id']) in booked_books_ids
        
        return render_template('index.html', books=books, current_user=current_user)






def get_book_details(book_id):
    # Fetch book details from the database based on the provided book ID
    book_details = collection.find_one({"_id": ObjectId(book_id)})
    return book_details

def is_overdue(booked_book):
    one_week_ago = dt.datetime.now() - dt.timedelta(weeks=1)
    return not booked_book.get('returned', False) and booked_book['date_booked'] < one_week_ago



@app.route('/booked')
@login_required
def booked():
    # Get the current user's booked books
    user_booked_books = current_user.user_data.get('booked', [])
    
    # Create a list to store book details
    booked_books_info = []
    
    # Fetch book details from the database based on booked book IDs
    for booked_book in user_booked_books:
        # Ensure that booked_book is parsed as a dictionary
        if isinstance(booked_book, dict) and not booked_book.get('returned', False):
            book_id = booked_book['book_id']
            book_details = get_book_details(book_id)
            if book_details:
                # Include all attributes of the booked book
                booked_books_info.append({
                    'title': book_details.get('title'),
                    'author': book_details.get('author'),
                    'category': book_details.get('category'),
                    'cover': book_details.get('cover'),
                    'date_booked': booked_book['date_booked'].strftime('%d/%m/%Y')
                })
    
    return render_template('booked.html', booked_books_info=booked_books_info)


@app.route('/history')
@login_required
def history():
    all_users = users_collection.find()  # Retrieve all users
    return render_template('history.html', all_users=all_users, get_book_details=get_book_details)

import datetime as dt  # Rename the standard datetime module import

# Now you can use dt.datetime.now()
@app.route('/admin')
@login_required
@admin_required
def admin():
    all_users = users_collection.find()
    all_users_info = []

    for user in all_users:
        user_info = {
            'username': user.get('username'),
            'email': user.get('email'),
            'booked_books': []
        }

        for booked_book in user.get('booked', []):
            if not booked_book.get('returned', False):
                book = get_book_details(booked_book['book_id'])
                if book:
                    book_info = {
                        'book_id': booked_book['book_id'],
                        'title': book.get('title'),
                        'date_booked': booked_book['date_booked'].strftime('%d/%m/%Y'),
                        'is_overdue': is_overdue(booked_book)
                    }
                    user_info['booked_books'].append(book_info)

        all_users_info.append(user_info)

    return render_template('admin.html', all_users=all_users_info)

class AddBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    cover = StringField('Cover URL', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    about = StringField('About', validators=[DataRequired()])
    submit = SubmitField('Add Book')


@app.route('/admin/add_book', methods=['GET', 'POST'])
@login_required
@admin_required
def add_book():
    form = AddBookForm()
    if form.validate_on_submit():
        title = form.title.data
        author = form.author.data
        category = form.category.data
        cover = form.cover.data
        quantity = form.quantity.data
        about = form.about.data

        new_book = {
            "title": title,
            "author": author,
            "category": category,
            "cover": cover,
            "quantity": int(quantity),
            "about" : about
        }

        with driver.session() as session:
            session.run(
                """
                MERGE (b:Book {title: $title, category: $category, cover: $cover, quantity: $quantity, about: $about})
                """,
                title=new_book['title'],
                category=new_book['category'],
                cover=new_book['cover'],
                quantity=new_book['quantity'],
                about=new_book['about']
            )

            # Create or match the author node
            session.run(
                """
                MERGE (a:Author {name: $author})
                """,
                author=new_book['author']
            )

            # Create the "WROTE" relationship between the author and the book
            session.run(
                """
                MATCH (b:Book {title: $title})
                MATCH (a:Author {name: $author})
                MERGE (a)-[:WROTE]->(b)
                """,
                title=new_book['title'],
                author=new_book['author']
            )
        collection.insert_one(new_book)
        flash('Book added successfully!', 'success')
        return redirect(url_for('admin'))
    return render_template('addbook.html', form=form)

@app.route('/api/book/<title>', methods=['GET'])
@login_required
def get_book_by_title(title):
    book = collection.find_one({"title": title})
    if not book:
        return jsonify({'message': 'Book not found'}), 404

    book['_id'] = str(book['_id'])  # Convert ObjectId to string for JSON serialization
    return jsonify(book), 200


class UpdateBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    cover = StringField('Cover', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    about = StringField('About', validators=[DataRequired()])
    submit = SubmitField('Update Book')


@app.route('/admin/update_book', methods=['GET', 'POST'])
@login_required
@admin_required
def update_book():
    form = UpdateBookForm()
    books = list(collection.find())  # Get all books from the database
    book_titles = [book['title'] for book in books]

    if form.validate_on_submit():
        title = form.title.data
        author = form.author.data
        category = form.category.data
        cover = form.cover.data
        quantity = form.quantity.data
        about = form.about.data

        book = collection.find_one({"title": title})
        if book:
            collection.update_one(
                {"_id": book['_id']},
                {"$set": {
                    "title": title,
                    "author": author,
                    "category": category,
                    "cover": cover,
                    "quantity": quantity,
                    "about" : about
                }}
            )
            with driver.session() as session:
                session.run(
                    """
                    MATCH (b:Book {title: $title})
                    SET b.author = $author,
                        b.category = $category,
                        b.cover = $cover,
                        b.quantity = $quantity,
                        b.about = $about
                    """,
                    title=title, author=author, category=category, cover=cover, quantity=quantity, about=about
                )
            flash('Book updated successfully!', 'success')
        else:
            flash('Book not found!', 'danger')

        return redirect(url_for('admin'))

    return render_template('updatebook.html', form=form, book_titles=book_titles)


class DeleteBookForm(FlaskForm):
    book_name = StringField('Book Name', validators=[DataRequired()])
    submit = SubmitField('Delete')

@app.route('/admin/delete_book', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_book():
    form = DeleteBookForm()
    books = collection.find()  # Retrieve all books

    if request.method == 'POST':
        book_name = request.form['book_name']

        # Find the book by title
        book = collection.find_one({"title": book_name})
        if not book:
            flash('Book not found!', 'danger')
            delete_success = False
        else:
            # Delete the book
            collection.delete_one({"_id": book['_id']})
            with driver.session() as session:
                session.run("MATCH (b:Book {title: $title}) DETACH DELETE b", title=book_name)
            
            flash('Book deleted successfully!', 'success')
            delete_success = True

        return render_template("deletebook.html", form=form, books=books, delete_success=delete_success)

    return render_template("deletebook.html", form=form, books=books)

@app.route('/admin/all_books')
@login_required
@admin_required
def all_books():
    books = list(collection.find())
    all_users = list(users_collection.find())
    
    book_user_info = []
    
    for book in books:
        book_info = {
            "title": book.get("title"),
            "quantity": book.get("quantity", 0),
            "users": []
        }
        
        for user in all_users:
            booked_books = user.get("booked", [])
            for booked_book in booked_books:
                if booked_book['book_id'] == str(book['_id']) and not booked_book.get('returned', False):
                    book_info["users"].append(user["email"])
        
        book_user_info.append(book_info)
    
    return render_template('allbooks.html', books=book_user_info)

@app.route('/admin/all_users')
@login_required
@admin_required
def all_users():
    all_users_cursor = users_collection.find()
    all_users = []
    
    for user_data in all_users_cursor:
        user = User(user_data)
        all_users.append({
            '_id': str(user.user_data['_id']),
            'username': user.user_data.get('username'),
            'email': user.user_data.get('email'),
            'booked_books': user.booked_books,
            'role': user.user_data.get('role', 'user')
        })
    
    return render_template("allusers.html", all_users=all_users, get_book_details=get_book_details)


@app.route('/admin/make_admin/<user_id>', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    # Find the user by their ID
    user = User.find_by_id(user_id)
    if user:
        # Update the user's role to admin
        user.user_data['role'] = 'admin'
        user.save_to_db()
        print(f"Making user {user_id} an admin")
        flash('User role updated to admin successfully!', 'success')
    else:
        flash('User not found!', 'danger')
    
    # Redirect back to the all_users page
    return redirect(url_for('all_users'))



@app.route('/admin/all_admins')
@login_required
@admin_required
def all_admins():
    all_admins_cursor = users_collection.find({'role': 'admin'})
    all_admins = []

    # Iterate over the cursor and populate the list of admin users
    for admin_data in all_admins_cursor:
        all_admins.append({
            '_id': str(admin_data['_id']),
            'username': admin_data.get('username'),
            'email': admin_data.get('email'),
            'role': admin_data.get('role', 'user')
        })

    print("All Admins:", all_admins)  # Debug print to check admin data

    # Render the template with the list of admin users
    return render_template("alladmins.html", all_users=all_admins)



@app.route('/admin/revoke_admin/<user_id>', methods=['POST'])
@login_required
@admin_required
def revoke_admin(user_id):
    # Find the user by their ID
    user = User.find_by_id(user_id)
    if user:
        # Update the user's role to admin
        user.user_data['role'] = 'user'
        user.save_to_db()
        print(f"Making admin {user_id} a user")
        flash('Admin role updated to user successfully!', 'success')
    else:
        flash('Admin not found!', 'danger')
    
    # Redirect back to the all_users page
    return redirect(url_for('all_admins'))
@app.route('/return_book/<book_id>', methods=['POST'])
@login_required
@admin_required
def return_book(book_id):
    try:
        if not request.json or 'user_email' not in request.json:
            return jsonify({'message': 'User email is required'}), 400

        user_email = request.json.get('user_email')

        user = User.find_by_email(user_email)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        book = collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            return jsonify({'message': 'Book not found'}), 404

        # Update the book quantity
        collection.update_one({"_id": ObjectId(book_id)}, {"$inc": {"quantity": 1}})

        # Update the user's booked list
        book_returned = False
        for booked_book in user.booked_books:
            if booked_book['book_id'] == book_id and not booked_book['returned']:
                booked_book['returned'] = True
                booked_book['date_returned'] = dt.datetime.now()  # Use dt.datetime.now()
                book_returned = True
                break

        if not book_returned:
            return jsonify({'message': 'Book not found in user\'s booked list or already returned'}), 400

        user.save_to_db()
        return jsonify({'message': 'Book returned successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


def search_neo4j(query):
    results = {"books": [], "authors": []}
    with driver.session() as session:
        # Search for books
        book_results = session.run(
            """
            MATCH (b:Book)
            WHERE toLower(b.title) CONTAINS toLower($query)
            RETURN b.title AS title, b.cover AS cover, b.category AS category,
            [(a:Author)-[:WROTE]->(b) | a.name] AS authors
            """, {"query": query})
        
        for record in book_results:
            results["books"].append({
                "title": record["title"],
                "authors": record["authors"],
                "category": record["category"],
                "cover": record["cover"]
            })

        if not results["books"]:
            # Search for authors if no books found
            author_results = session.run(
                """
                MATCH (a:Author)-[:WROTE]->(b:Book)
                WHERE toLower(a.name) CONTAINS toLower($query)
                RETURN a.name AS name, collect(b.title) AS books, collect(b.cover) AS covers, collect(b.category) AS categories
                """, {"query": query})
            
            for record in author_results:
                results["authors"].append({
                    "name": record["name"],
                    "books": record["books"],
                    "covers": record["covers"],
                    "categories": record["categories"]
                })
    
    return results



@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if query:
        results = search_neo4j(query)
        return jsonify(results)
    return jsonify({"books": [], "authors": []})






if __name__ == '__main__':
    app.run(debug=True, port=5001)