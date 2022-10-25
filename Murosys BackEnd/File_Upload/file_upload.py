from flask import Flask, render_template, request, redirect, url_for
import os
from os.path import join, dirname, realpath
import pandas as pd
from flask_mysqldb import MySQL
import MySQLdb.cursors


app = Flask(__name__)

app.config["DEBUG"] = True

UPLOAD_FOLDER = 'files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'murosys'
app.config['MYSQL_DB'] = 'murosys_database'

mysql = MySQL(app)


@app.route("/")
def index():
    return render_template('indianajones.html')

@app.route("/", methods = ['POST'])
def uploadFiles():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
        parseCSV(file_path)

    return redirect(url_for('index'))

def parseCSV(filepath):
    data = pd.read_csv(filepath)
    columns = list(data.columns)

    for i,row in data.iterrows():
        insert = "INSERT INTO listening_history (endTime, artistName, trackName, msPlayed) VALUES (%s, %s, %s, %s)"
        values = (row[columns[0]], row[columns[1]], row[columns[2]], row[columns[3]])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(insert, values)
        mysql.connection.commit()



