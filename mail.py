from flask_mail import *
from random import *
from flask import *
app = Flask(__name__)

with open('config.json','f') as f:
    params = json.load(f)['paras']

app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = params['gmail-user']
app.config['MAIL_PASSWORD'] = params['gmail-password']  
#users={{'name':'harsh', 'email':'hashclg@gmail.com'}}
mail = Mail(app)
otp=randint(0000,9999)

@app.route('/')
def index():
    return render_template("email.html",msg="")

@app.route('/verify',methods=["POST"])
def verify():
    gmail = request.form['email']
    msg = Message('OTP', sender='hashclg@gmail.com', recipients=[gmail])
    msg.body=str(otp)
    mail.send(msg)
    return render_template("verify.html")

@app.route('/validate',methods=["POST"])
def validate():
    userotp=request.form['otp']
    if otp==int(userotp):
        return "Email Verified Successfully !"
    return render_template('email.html', msg="Not Verified!! Try again")

if __name__=='__main__':
    app.run(debug=True)