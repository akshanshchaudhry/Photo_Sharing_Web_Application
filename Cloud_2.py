#Akshansh Chaudhry

from flask import Flask , render_template, request, session
import os


import boto3
from botocore.client import Config


import pymysql

# put in your AWS details below

host="your aws host name"
port="your aws port number"
dbname="your database name"
user="your user name"
password="your password"

conn = pymysql.connect(host, user=user, port=port, passwd=password, db=dbname)

cur = conn.cursor()



app = Flask(__name__)

# Put in the keys of your AWS connection

app.secret_key = os.urandom(24)

ACCESS_KEY_ID = 'your AWS access key'
ACCESS_SECRET_KEY = 'Your AWS secret key'
BUCKET_NAME = 'your bucket name'

##########################

s3Client = boto3.client('s3',aws_access_key_id=ACCESS_KEY_ID,
  aws_secret_access_key=ACCESS_SECRET_KEY,
  config=Config(signature_version='s3v4'))
#########################

s3 = boto3.resource(
    's3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=ACCESS_SECRET_KEY,
    config=Config(signature_version='s3v4')
)

#put in the directory from where you want to upload the images
directory = "directory from where you upload the images"

url = "bucket url"



@app.route('/')
def hello_world():
    return render_template("login.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        # print(session.values())
        uname = session['username']





    return render_template("index.html")





@app.route('/post', methods=['POST'])
def post():

    if request.method == 'POST':


        f = request.files['file']
        title = request.form['title']
        ratings = request.form['ratings']
        comments = request.form['comments']
        print(f)

        filename = f.filename
        data = directory + filename

        # keys = []
        # resp = s3Client.list_objects_v2(Bucket=BUCKET_NAME)
        # for obj in resp['Contents']:
        #     keys.append(obj['Key'])
        #
        # image_links = []
        # z = len(keys)
        # print(z)
        # for i in range(z):
        #     image_links.append(url+keys[i])
        #
        # print(image_links)


        if request.form['click'] == 'Upload Image':
            s3.Bucket(BUCKET_NAME).put_object(Key=filename, Body=open(data, 'rb'), ACL='public-read')
            keys = []
            resp = s3Client.list_objects_v2(Bucket=BUCKET_NAME)
            for obj in resp['Contents']:
                keys.append(obj['Key'])

            image_links = []
            z = len(keys)
            print(z)
            for i in range(z):
                image_links.append(url + keys[i])
            #
            cur.execute("SELECT CONVERT_TZ(NOW(),'-06:00','+00:00')")
            date_time = cur.fetchone()

            print("zero index")
            print(image_links[0])
            print("last index")
            print(image_links[-1])

            print(session['username'])
            cur.execute("""INSERT INTO picture VALUES (%s,%s,%s,%s,%s,%s);""", (image_links[-1], title, ratings, comments, date_time,session['username']))
            conn.commit()


            return "upload successful"

@app.route('/upload', methods=['GET','POST'])
def upload():

    if request.method == 'POST':

        if request.form['click'] == 'View Image':

            cur.execute("""SELECT * FROM picture""")
            data = (cur.fetchall())
            print(data[0])
            instagram = [dict(image_url=row[0],
                              title=row[1],
                              ratings=row[2],
                              comments=row[3],
                              date=row[4]) for row in data]

            print(instagram)

            # return '<img src="' + image_links[0]+ '"/>'
            return render_template("gallary.html", instagram=instagram)

# put below the directory where you want to download the images to
@app.route('/download', methods=['POST'])
def download():
    if request.method == 'POST':
        img_name = request.form['files']

        if request.form['download'] == 'Download Image':
            cur.execute("""SELECT image_url FROM picture WHERE title = (%s)""",(img_name))
            img_key = (cur.fetchall())
            str = ''.join(img_key[0])
            str_key= str[43:]
            print(str_key)
            down_path= "directory where the download images will be stored"+str_key
            s3Client.download_file(BUCKET_NAME,str_key,down_path)


            return "file downloaded"

        elif request.form['download'] == 'Edit Image':
            cur.execute("""SELECT image_url,title FROM picture WHERE title = (%s)""",(img_name))
            img_edit = (cur.fetchall())
            instagram_edit = [dict(image_url=row[0],
                              title=row[1])
                               for row in img_edit]



            # return '<img src="' + image_links[0]+ '"/>'
            return render_template("edit.html", instagram=instagram_edit)


            return "file edited"


        elif request.form['download'] == 'Delete Image':

            key = request.form['files']
            cur.execute("""SELECT image_url FROM picture WHERE title = (%s)""", (img_name))
            img_key = (cur.fetchall())
            str = ''.join(img_key[0])
            str_key = str[43:]

            s3Client.delete_object(Bucket = BUCKET_NAME, Key= str_key)
            cur.execute("""Delete FROM picture WHERE title = (%s)""",(key))
            conn.commit()

            return "deleted"





@app.route('/save', methods=['POST'])
def save():
    if request.method == 'POST':
        edit_name= request.form['edit_name']
        ratings_edit = request.form['ratings']
        comments_edit = request.form['comments']
        print(comments_edit, ratings_edit,edit_name)

        if request.form['save'] == 'Save Changes':

            cur.execute("""UPDATE picture SET ratings = (%s), comments = (%s), user_name = (%s) WHERE title = (%s);""", (ratings_edit,comments_edit,session['username'],edit_name))
            conn.commit()

            return "saved"









if __name__== '__main__':
    app.run()


# port = os.getenv('0.0.0.0','8080')
#
# if __name__== '__main__':
#     app.run(host = '0.0.0.0',port = int(port), debug = True)
