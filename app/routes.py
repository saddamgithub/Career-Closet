
from flask import Flask, render_template, flash, request, session, url_for, redirect, jsonify
from forms import ContactForm, SignupForm, SigninForm, AvailabilityForm, CheckoutForm
from flask_mail import Message, Mail
from models import db, User, Suits, Schedule
from sqlalchemy import or_, and_
import datetime

mail = Mail()

app = Flask(__name__)

@app.route("/")
def home():
    if "email" in session:        
        user = User.query.filter_by(email = session["email"]).first()
        if user is None:
            return redirect(url_for("signin"))        
    return render_template("home.html")

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "email" not in session:
        return redirect(url_for("signin"))
    user = User.query.filter_by(email = session["email"]).first()
    #print(user)
    if user is None:
        return redirect(url_for("signin"))
    elif user.email =="careerclosetatm@gmail.com":
        form = CheckoutForm()
        if request.method == "POST":
            if form.validate() == False:
                flash("All fields are required")
                return render_template("checkout.html", form=form)
            else:
                suits = Suits.query.filter(Suits.suit_id == form.suiteId.data).first()
                suits.available = False
                db.session.commit()   
                return render_template("checkout.html", success = True)
        elif request.method == "GET":
            return render_template("checkout.html", form=form)  
    else:
        return render_template("home.html")
    

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()   
    if request.method == 'POST':
        if form.validate() == False:            
            return render_template('signup.html', form=form)
        else:
            print("Creating user")   
            newuser = User(form.username.data, form.firstname.data, form.lastname.data, form.email.data, form.uin.data, form.password.data)
            db.session.add(newuser)
            db.session.commit()   
            session["email"] = newuser.email;
            return redirect(url_for("home"))
   
    elif request.method == 'GET':
        return render_template('signup.html', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
   
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signin.html', form=form)
        else:
            session['email'] = form.email.data
            return redirect(url_for('home'))
                 
    elif request.method == 'GET':
        return render_template('signin.html', form=form)

@app.route('/signout')
def signout():
 
    if 'email' not in session:
        return redirect(url_for('signin'))
     
    session.pop('email', None)
    return redirect(url_for('home'))

@app.route("/availability", methods=["GET", "POST"])
def availability():
    if "email" not in session:
        return redirect(url_for("signin"))
    user = User.query.filter_by(email = session["email"]).first()
    if user is None:
        return redirect(url_for("signin"))
    else:
        form = AvailabilityForm()
        if request.method == "POST":
            if form.validate() == False:
                flash("All fields are required")
                return render_template("availability.html", form=form)
            else:
                suits = Suits.query.filter(and_(Suits.gender == form.gender.data, Suits.type == form.type.data, Suits.available == True)).all()
                scount = 0
                mcount = 0
                lcount = 0
                for suit in suits:
                    if suit.size == "s": scount = scount+1
                    if suit.size == "m": mcount = mcount+1
                    if suit.size == "l": lcount =lcount+1
                #suits = Suits.query.filter(Suits.type == form.type.data).all()
                return render_template("availability.html", success = True, suits = suits, scount = scount, lcount = lcount, mcount = mcount)
        elif request.method == "GET":
            return render_template("availability.html", form=form)  

@app.route('/echo/', methods=['GET'])
def echo():
    print("Entered echo")
    #form = ScheduleForm()
    date = request.args.get('date')
    print("Querying")
    #slots = Schedule.query.filter(Schedule.date == date).first()
    slots = Schedule.query.filter(Schedule.date == date).first()
    print("Finished Querying")
    return jsonify(slots = {"date":slots.date, "time9_00":slots.time9_00})    

    
@app.route("/learn")
def learn():
    return render_template("learn.html")

@app.route("/appointment")
def appointment():
    if "email" not in session:
        return redirect(url_for("signin"))
    user = User.query.filter_by(email = session["email"]).first()
    if user is None:
        return redirect(url_for("signin"))
    else:          
        return render_template("appointment.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    
    if request.method == "POST":
        print("contact post")
        if form.validate() == False:
            flash("All fields are required")
            print("validate false")
            return render_template("contact.html", form=form)
        else:
            print("Going to send message")
            msg = Message(form.subject.data, sender="hussain.m@tamu.edu", recipients = ["saddamhussain4321@gmail.com"])
            msg.body = """
            From: %s <%s>
            %s
            """%(form.name.data, form.email.data, form.message.data)
            mail.send(msg)
            print("message sent")
            return render_template("contact.html", success = True)
    elif request.method == "GET":
        print("contact get")
        return render_template("contact.html", form=form)

if __name__=="__main__":
    app.secret_key = "12345667"
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 465
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = 'careerclosetatm@gmail.com'
    app.config["MAIL_PASSWORD"] = 'Group5Password'
    mail.init_app(app)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///development'
    from models import db
    db.init_app(app)    
    with app.test_request_context():
        #db.drop_all()
        db.create_all()
#         schedule1 = Schedule(datetime.datetime.strptime('19-03-17', '%d-%m-%y').date(),'1','1','1','1','1','1''1','1','1','1')
#         schedule2 = Schedule(datetime.datetime.strptime('20-03-17', '%d-%m-%y').date(),'0','1','0','1','0','1''0','1','0','1')
#         schedule3 = Schedule(datetime.datetime.strptime('21-03-17', '%d-%m-%y').date(),'1','1','0','1','1','0''1','1','0','1')
#         db.session.add(schedule1)
#         db.session.add(schedule2)
#         db.session.add(schedule3)
#         db.session.commit()
#          
#         suit1 = Suits('1','m','s','jacket')
#         suit2 = Suits('2','m','s','jacket')
#         suit3 = Suits('3','m','s','jacket')
#         suit4 = Suits('4','m','m','jacket')
#         suit5 = Suits('5','m','m','jacket')
#         suit6 = Suits('6','m','l','jacket')
#         suit7 = Suits('7','m','s','pant')
#         suit8 = Suits('8','m','m','pant')
#         suit9 = Suits('9','m','l','pant')
#                    
#         suit10 = Suits('10','f','s','jacket')
#         suit11 = Suits('11','f','m','jacket')
#         suit12 = Suits('12','f','m','jacket')
#         suit13 = Suits('13','f','m','jacket')
#         suit14 = Suits('14','f','l','jacket')
#         suit15 = Suits('15','f','l','jacket')
#         suit16 = Suits('16','f','l','jacket')
#         suit17 = Suits('17','f','s','pant')
#         suit18 = Suits('18','f','m','pant')
#         suit19 = Suits('19','f','l','pant')
#         #db.session.add(suit1)
#         db.session.commit() 
#         db.session.add(suit2)
#         db.session.commit() 
#         db.session.add(suit3)
#         db.session.commit() 
#         db.session.add(suit4)
#         db.session.commit() 
#         db.session.add(suit5)
#         db.session.commit() 
#         db.session.add(suit6)
#         db.session.commit() 
#         db.session.add(suit7)
#         db.session.commit() 
#         db.session.add(suit8)
#         db.session.commit() 
#         db.session.add(suit9)
#         db.session.commit() 
#         db.session.add(suit10)
#         db.session.commit() 
#         db.session.add(suit11)
#         db.session.commit() 
#         db.session.add(suit12)
#         db.session.commit() 
#         db.session.add(suit13)
#         db.session.commit() 
#         db.session.add(suit14)
#         db.session.commit() 
#         db.session.add(suit15)
#         db.session.commit() 
#         db.session.add(suit16)
#         db.session.commit() 
#         db.session.add(suit17)
#         db.session.commit() 
#         db.session.add(suit18)
#         db.session.commit() 
#         db.session.add(suit19)
#         db.session.commit()
          
        
        
    app.run(debug=True)
    

