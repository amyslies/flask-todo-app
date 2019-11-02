from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import sys
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://amyly@localhost:5432/amyly'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class TodoList(db.Model):
  __name__ = "todolists"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  # todos = db.relationship('Todo', backref='list', lazy=True) #name of the class, custom name representing name of parent...

class Todo(db.Model):
  __name__ = "todos"
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)
  completed = db.Column(db.Boolean, nullable=False, default=False)
  # list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

  def __repr__(self):
    return f'<Todo {self.id} {self.description}>'

@app.route('/todos/<todo_id>/delete', methods=['DELETE'])
def delete_todo(todo_id):
  error = False
  try:
    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
  except:
    print('Error')
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(400)
  return redirect(url_for('index'))

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/todos/create', methods=['POST'])
def create_todo():
  error = False
  body = {}
  try: 
    description = request.get_json()['description']
    todo = Todo(description=description)
    db.session.add(todo)
    db.session.commit()
    body['description'] = todo.description
    body['id'] = todo.id
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    return jsonify(body)

@app.route('/')
def index():
  return render_template('index.html', data=Todo.query.order_by('id').all())


