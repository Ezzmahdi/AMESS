from flask import Flask, redirect, render_template, request, flash
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__,static_url_path='', static_folder='static')
app.config['SECRET_KEY'] = "#$Geg4535%^%tERDFHd4@%$#"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
socketio = SocketIO(app)
sockets = {}
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Template(db.Model):
    _id = db.Column("id",db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    spatula = db.Column(db.Integer)
    knife = db.Column(db.Integer)
    scissors = db.Column(db.Integer)
    def __init__(self, name, spatula, knife, scissors):
        super().__init__()
        self.name = name
        self.spatula = spatula
        self.knife = knife
        self.scissors = scissors
    def __str__(self):
        return self.name

class StorageColumn(db.Model):
    _id = db.Column("id",db.Integer, primary_key = True)
    type = db.Column(db.String(50))
    filled_cells = db.Column(db.Integer)
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.filled_cells = 0
    def Removetools(self, removedtools):
        if self.filled_cells >= int(removedtools):
            self.filled_cells = int(self.filled_cells) - int(removedtools)
            return True
        else:
            return False
    def Addtools(self, addedtools):
        self.filled_cells += addedtools
        

if not db.session.query(StorageColumn).first():
    Spatula_column = StorageColumn('Spatula')
    knife_column = StorageColumn('knife')
    scissors_column = StorageColumn('scissors')
    db.session.add(Spatula_column)
    db.session.add(knife_column)
    db.session.add(scissors_column)
    db.session.commit()
else:
    Spatula_column = StorageColumn.query.filter_by(type="Spatula").first()
    knife_column = StorageColumn.query.filter_by(type="knife").first()
    scissors_column = StorageColumn.query.filter_by(type="scissors").first()

@app.route("/")
def home():
    currently_stored = StorageColumn.query.all()
    return render_template("home.html", templates = Template.query.all(), currently_stored = currently_stored)


@app.route("/create", methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        Name = request.form["floatingInput"]
        spatula = request.form["spatula"]
        if not spatula:
            spatula = 0
        knife = request.form["knife"]
        if not knife:
            knife = 0
        scissors = request.form["scissors"]
        if not scissors:
            scissors = 0
        template = Template(Name, spatula, knife, scissors)
        db.session.add(template)
        db.session.commit()
        return redirect("/")
    else:
        return render_template("create.html")

@socketio.on('order')
def retrieve_template(id):
    template_id = int(id)
    found_template = Template.query.filter_by(_id=template_id+1).first()
    if Spatula_column.Removetools(found_template.spatula) and knife_column.Removetools(found_template.knife) and scissors_column.Removetools(found_template.scissors):
        sockets[request.sid].emit('order-response', {'accepted':True})
    else: 
        sockets[request.sid].emit('order-response',{'accepted':False})

def upatecategory_func(type):
    if type == 'spatula':
        Spatula_column.filled_cells += 1
        socketio.emit("update-column",{'data': {"type":"spatula"}})
    elif type == 'knife':
        knife_column.filled_cells += 1
        socketio.emit("update-column",{'data': {"type":"knife"}})
    elif type == 'scissors':
        scissors_column.filled_cells += 1
        socketio.emit("update-column",{'data': {"type":"scissors"}})

@socketio.on('message')
def updatecategory(message):
    type = ""
    upatecategory_func(type)
    return
    
@socketio.on('connected')
def connected():
    print( "%s connected" % (request.sid))
    sockets[request.sid] = Socket(request.sid)
    
@socketio.on('disconnect')
def disconnect():
    print( "%s disconnected" % (request.sid))
    del sockets[request.sid]
class Socket:
    def __init__(self, sid):
        self.sid = sid
        self.connected = True

    # Emits data to a socket's unique room
    def emit(self, event, data = None):
        socketio.emit(event, data, room=self.sid)
if __name__ == '__main__':
    db.create_all()
    socketio.run(app)
