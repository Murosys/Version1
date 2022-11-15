from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import re
import os
from sklearn.ensemble import RandomForestClassifier
import mysql.connector

app = Flask(__name__)
app.secret_key = 'NateTheGreat'

#connection = mysql.connector.connect(user="root", password="PQ9S4HLj4N\"zE}?J", host="10.17.48.4", database="MurosysDB")
connection = mysql.connector.connect(user="root", password="PQ9S4HLj4N\"zE}?J", host="34.67.157.2", database="MurosysDB")


UPLOAD_FOLDER = 'files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods = ['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        columns = cursor.description 
        account = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()][0]

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
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exist!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'^[A-Za-z0-9]*$', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s)', (username, password, email,))
            connection.commit()
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
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM recommendations where user_id = %s', (session['id'],))
        columns = cursor.description 
        reccs = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
        return render_template('home.html', reccs=reccs, username=session['username'])

    return redirect(url_for('login'))


@app.route('/profile', methods = ['GET', 'POST'])
def profile():
    if 'loggedin' in session:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['id'],))
        columns = cursor.description 
        account = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()][0]
        return render_template('profile.html', account=account)
    if request.method == 'POST':
        return redirect(url_for('home'))

    return redirect(url_for('login'))   

@app.route("/upload", methods = ['POST'])
def uploadFiles():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        #parseCSV(uploaded_file)
        recommendations(request.form.getlist('features'))
    return redirect(url_for('home'))

def parseCSV(file):
    data = pd.read_csv(file)
    columns = list(data.columns)

    for i,row in data.iterrows():
        cursor = connection.cursor()
        values = (row[columns[0]], row[columns[1]], row[columns[2]], row[columns[3]], session['id'])
        cursor.execute("INSERT INTO listening_history (endTime, artistName, trackName, msPlayed, user_id) VALUES (%s, %s, %s, %s, %s)", values)
        connection.commit()

def recommendations(features):
    cursor = connection.cursor()
    cursor.execute("select * from songs")
    music = pd.DataFrame(cursor.fetchall())
    music.columns = [i[0] for i in cursor.description]


    cursor = connection.cursor()
    cursor.execute("select endTime, artistName, trackName, msPlayed from listening_history where user_id = %s", (session['id'],))
    user = pd.DataFrame(cursor.fetchall())
    user.columns = [i[0] for i in cursor.description]

    # Data Cleaning Steps
    music = music.drop_duplicates(subset = ['name', 'artists'])
    user_grouped = user.groupby(by = 'trackName').max().reset_index()
    music['primary_artist'] = music['artists'].str.strip('[]').str.split(',').str[0].str.strip('\'\'')
    merged = pd.merge(user_grouped, music, left_on = ['trackName', 'artistName'], right_on = ['name', 'primary_artist'])
    merged.loc[merged['msPlayed'] <= 30000, 'Likes_Song'] = 0
    merged.loc[merged['msPlayed'] > 30000, 'Likes_Song'] = 1

    # Selecting subset of features
    #filters = list(merged.columns[12:22])
    filters = features
    train = merged[filters + ["Likes_Song"]]
    name = music['name']
    artist = music['artists'].str.strip('[]').str.split(',').str[0].str.strip('\'\'')
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
        insert = "INSERT INTO recommendations (trackName, artistName, user_id) VALUES (%s, %s, %s)"
        values = (row['name'], row['artist'], session['id'])
        cursor = connection.cursor()
        cursor.execute(insert, values)
        connection.commit()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT',8080))







    