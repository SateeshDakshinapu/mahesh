from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import base64
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient("mongodb+srv://tiger:tigersateesh@cluster0.0ggj59e.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['competition_db']
photos_collection = db['photos']
votes_collection = db['votes']
emails_collection = db['emails']

# Email setup
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify_email', methods=['POST'])
def verify_email():
    email = request.form['email']
    user = emails_collection.find_one({"email": email})
    
    if not user:
        flash("Email not registered.", "error")
        return redirect(url_for('index'))
    elif user.get("voted", False):
        flash("Already voted.", "warning")
        return redirect(url_for('index'))
    else:
        return redirect(url_for('gallery', user_name=user.get("name", "User"), email=email))

@app.route('/gallery')
def gallery():
    user_name = request.args.get('user_name')
    email = request.args.get('email')
    photos = list(photos_collection.find())
    for photo in photos:
        photo['image'] = base64.b64encode(photo['image']).decode('utf-8')
    return render_template('gallery.html', user_name=user_name, email=email, photos=photos)

@app.route('/vote', methods=['POST'])
def vote():
    photo_id = request.form['image_id']
    email = request.form['email']
    
    # Update vote in votes collection
    votes_collection.insert_one({"photo_id": photo_id, "email": email})
    emails_collection.update_one({"email": email}, {"$set": {"voted": True}})
    
    send_confirmation_email(email)  # Send confirmation email after voting
    
    flash("Thank you for voting!", "success")
    return redirect(url_for('index'))

def send_confirmation_email(email):
    msg = Message('Vote Confirmation', recipients=[email])
    msg.body = 'Thank you for voting in the competition!'
    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True)
