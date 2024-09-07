from flask import Flask,render_template,request,render_template_string,jsonify,redirect,url_for,make_response
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bson import json_util, ObjectId
from passlib.hash import pbkdf2_sha256
from users.models import User
from flask_cors import CORS
from functools import wraps 
from flask_jwt_extended import JWTManager,jwt_required,create_access_token,get_jwt_identity,set_access_cookies,get_jwt,unset_jwt_cookies
import json
import datetime
import os


def role_required(allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user = get_jwt()
            print(current_user)
            if current_user.get('role') in allowed_roles:
                return fn(*args, **kwargs)
            else:
                return jsonify(message="Access forbidden. Insufficient role."), 403
        return wrapper
    return decorator

app= Flask(__name__)

CORS(app)
app.config["JWT_TOKEN_LOCATION"] = ["cookies","headers"]
app.config['JWT_SECRET_KEY']= os.urandom(24)
app.config['JWT_COOKIE_CSRF_PROTECT']= False
#app.config['JWT_CSRF_CHECK_FORM']=True
app.config['JWT_COOKIE_SECURE']=True
jwt= JWTManager(app)

#app.config['MONGO_URI']='mongodb://localhost:27017/Hostel_leave'
##client=MongoClient('mongodb://localhost:27017/')
#mongo= PyMongo(app)

client=MongoClient(host='hostel_leave',port=27017,username='root',password='pass')
db=client['Hostel']
collection=db['Leave_apply']
loginDB=client['user_login']
loginCollection=loginDB['users']

@app.route('/',methods=['GET','POST'])
def Login():
        if request.method =='GET':
            print("from get:",request.headers)
            #print("Cookie:", request.cookies.get('token'))
            return render_template('Login.html')
        else:
            email=request.form.get('email')
            password=request.form.get('password')
            user=loginCollection.find_one({'Email':email})
            print(user)
                

            if user and  pbkdf2_sha256.verify(password,user['password']):
                if email !='admin@gmail.com':
                    status={"role":"student"}
                    access_token=create_access_token(email,additional_claims=status)
                    response = make_response(redirect(url_for('Dashboard'))) # this the change done , to save that cookie and also return the response only.
                    #response = jsonify({"msg": "login successful"})
                    set_access_cookies(response, access_token)
                    return response
                else:
                    status={"role":"Admin"}
                    access_token=create_access_token(email,additional_claims=status)
                    response = make_response(redirect(url_for('adminview'))) # this the change done , to save that cookie and also return the response only.
                    #response = jsonify({"msg": "login successful"})
                    set_access_cookies(response, access_token)
                    return response
                    

                #return redirect('/protected')
                #return render_template_string('login success')
                #response.headers['Authorization'] = f'Bearer {access_token}'   
            return render_template('Login.html',data=True)

@app.route('/logout',methods=['POST','GET'])
@jwt_required()
def logout():
    response=make_response(redirect(url_for('Login')))
    unset_jwt_cookies(response)
    return response

@app.route('/signup')
def signup():
   return render_template('Signup.html',data=False)

@app.route('/users/signup',methods=['POST'])
def APISignup():
    name=request.form.get('name')
    email=request.form.get('email')
    password=request.form.get('password')

    user= User()
    result=user.signup(name,email,password)
    
    if loginCollection.find_one({"Email": result['Email']}):
        return jsonify({"error": "email address already in use"}), 400

    if loginCollection.insert_one(result):
       return render_template('Signup.html',data={"flag":True})
        #return redirect(url_for('signup',data=True))

    return jsonify({"error":"signup failed"})

@app.route("/protected", methods=["GET"]) # for testing
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
 
@app.route("/adminDashboard", methods=["GET"])
@jwt_required()
@role_required(allowed_roles=['Admin'])
def adminDashboard():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/Dashboard')
@jwt_required()
def Dashboard():
    return render_template('home.html')

@app.route('/leave',methods=['GET','POST']) #main endpoint
@jwt_required()
def leave():
    if request.method=='GET':
      #csrf_token_dup=request.cookies.get('csrf_access_token')
      return render_template('index.html')
    else:
        
       # dict_data={"c":csrf_token_dup,"flag":True}
        fname=(request.form.get('name'))
        reg_no=int(request.form.get('Reg'))
        room=request.form.get('Room')
        From=request.form.get('From')
        To=request.form.get('TO')
        reason=request.form.get('Reason')
        submitted='submitted'

        data={
            'Name':fname,
            'Register Number':reg_no,
            'Room Number': room,
            'From':From,
            'To':To,
            'Reason':reason,
            'status':submitted
        }
        #name,Reg,Room,From,To,Reason
        
        #data=request.form
        print(data)
        collection.insert_one(data)
        #mongo.db.record.insert(dict(Name=data['name'],Register_No=data['Reg'],Room_no=data['Room'],From=data['From'],To=data['TO'],Reason=data['Reason']))

        #return 'Your leave applied successfully'
        status="leave applied successfully"
        return render_template('index.html',data=status)

@app.route('/admin') #sub endpoint
@jwt_required()
@role_required(allowed_roles=['Admin'])
def admin():
    data=list(collection.find())
    print(data)
    return render_template('admin.html',data=data)

@app.route('/adminview') #main ednpoint
@jwt_required()
@role_required(allowed_roles=['Admin'])
def adminview():
    data=list(collection.find())
    return render_template('adminview.html',data=data)

@app.route('/student')
@jwt_required()
@role_required(allowed_roles=['Admin'])
def Studentleave():
    reg=int(request.args.get('ID'))
    data=collection.find_one({"Register Number":reg},{"_id":0})
    return render_template('admin.html',data=data)

@app.route('/adminlist') #test endpoint not in use
@jwt_required()
@role_required(allowed_roles=['Admin'])
def adminlist():
    cursor=collection.find({},{"Name": 1,"Register Number":1,"Room Number":1,"From":1,"To":1,"Reason":1})

    print(cursor)
    data = [document for document in cursor]
    #print(data)
    #return json.loads(json_util.dumps(data))
    #return jsonify(data)
    page_sanitized = json.loads(json_util.dumps(data))
    return page_sanitized


@app.route('/checkStatus',methods=['POST','GET']) #main endpoint
@jwt_required()
def checkStatus():
    if request.method=='POST':
        id=int(request.form.get('id'))
        # print(id)
        fdata=collection.find_one({"Register Number":id},{"_id":0})
        #print(fdata)
        return render_template('search.html',data=fdata)
    else:   
        return render_template('check.html')

@app.route('/approve')
@jwt_required()
@role_required(allowed_roles=['Admin'])
def approve():
    a=int(request.args.get('register_number'))
    cdata=collection.update_one({"Register Number":a}, {"$set": {"status":'Approved'}})
   
    return render_template_string('leave approved successfully')

@app.route('/reject')
@jwt_required()
@role_required(allowed_roles=['Admin'])
def reject():
    a=int(request.args.get('register_number'))
    cdata=collection.update_one({"Register Number":a}, {"$set": {"status":'Rejected'}})
   
    return render_template_string('Leave Rejected successfully')

if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True)
