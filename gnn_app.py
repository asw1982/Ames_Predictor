# -*- coding: utf-8 -*-

from flask import Flask, render_template, url_for ,request , redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from smiles2ames import *

# create empty model with the hyperparameter 
nCV = 10
num_layer = 3
dropout_rate=0.2051210302624803
hidden_channels = 64 
num_node_features = 79 
num_classes = 1

list_trained_model =[]
for i in range(10):
    loaded_model = GCN(hidden_channels,num_node_features, num_classes, dropout_rate, num_layer) 
    loaded_model.load_state_dict(torch.load("model_GNN"+ str(i)+ ".pth"))
    list_trained_model.append(loaded_model)



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200),nullable=False)
    prediction = db.Column(db.String(200),nullable=False)
    completed =db.Column(db.Integer,default =0)
    date_created =db.Column(db.DateTime,default =datetime.utcnow)
    
    def __repr__(self):
        return '<Task %r>' % self.id 
    
    
@app.route('/', methods= ['POST','GET'])

def index():
    if request.method =='POST':
        task_content = request.form['content']
        
        pred_result = smiles_to_ames(task_content)
        
        new_task = Todo(content=task_content, prediction = pred_result)
        
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'there was an issue adding your task '
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks= tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete= Todo.query.get_or_404(id)
    
    
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    
    except:
        return 'there was a problem deleting that task'
    
@app.route('/update/<int:id>', methods = ['GET','POST'])
def update(id):  
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content= request.form['content']
        
        try : 
            db.session.commit()
            return redirect('/')
        except:
            return 'there was an issue updating this task '
    else :
        return render_template('update.html', task=task)
    
if __name__=="__main__":
    #==================
    app.app_context().push()
    db.create_all()
    #===================
    app.run(debug=True)
