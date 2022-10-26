from tkinter.font import nametofont
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import pandas as pd
import re
import os
import sys
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)
app.secret_key = 'NateTheGreat'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'murosys'
app.config['MYSQL_DB'] = 'murosys_database'

UPLOAD_FOLDER = 'files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

@app.route('/', methods = ['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']

            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'

    return render_template('index.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exist!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    
    return render_template('register.html', msg=msg)

@app.route('/upload')
def indianajones():
    return render_template('indianajones.html', username=session['username'])


@app.route('/home')
def home():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM recommendations')
        reccs = cursor.fetchall()
        return render_template('home.html', reccs=reccs, username=session['username'])

    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)

    return redirect(url_for('login'))

@app.route("/upload", methods = ['POST'])
def uploadFiles():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
        parseCSV(file_path)
        recommendations(os.path.join(app.config['UPLOAD_FOLDER'], "tracks.csv"))

        

    return redirect(url_for('home'))

def parseCSV(filepath):
    data = pd.read_csv(filepath)
    columns = list(data.columns)

    for i,row in data.iterrows():
        insert = "INSERT INTO listening_history (endTime, artistName, trackName, msPlayed) VALUES (%s, %s, %s, %s)"
        values = (row[columns[0]], row[columns[1]], row[columns[2]], row[columns[3]])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(insert, values)
        mysql.connection.commit()

def recommendations(filepath):
    music = pd.read_csv(filepath)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from listening_history")
    data = cursor.fetchall()
    user = pd.DataFrame(data)

    # Data Cleaning Steps
    music = music.drop_duplicates(subset = ['name', 'artists'])
    user_grouped = user.groupby(by = 'trackName').max().reset_index()
    music['primary_artist'] = music['artists'].str.strip('[]').str.split(',').str[0].str.strip('\'\'')
    merged = pd.merge(user_grouped, music, left_on = ['trackName', 'artistName'], right_on = ['name', 'primary_artist'])
    merged.loc[merged['msPlayed'] <= 30000, 'Likes_Song'] = 0
    merged.loc[merged['msPlayed'] > 30000, 'Likes_Song'] = 1

    # Selecting subset of features
    filters = list(merged.columns[12:22])
    train = merged[filters + ["Likes_Song"]]
    name = music['name']
    artist = music['artists']
    test = music[filters]
    user_x = train[filters]
    user_y = train["Likes_Song"]

    model = RandomForestClassifier()
    model.fit(user_x, user_y)
    predictions = model.predict(test)
    test['recommendations'] = predictions
    test['name'] = name
    test['artist'] = artist

    recommendations = test[test['recommendations'] == 1].sample(50)[['name','artist']]

    for i,row in recommendations.iterrows():
        insert = "INSERT INTO recommendations (trackName, artistName) VALUES (%s, %s)"
        values = (row['name'], row['artist'])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(insert, values)
        mysql.connection.commit()










    