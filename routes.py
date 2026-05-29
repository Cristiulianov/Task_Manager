from app import app, db
from flask import render_template, request, redirect
from models import User, Task
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from flask import flash, session
from datetime import datetime, date




@app.route('/')
def home():
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')
    
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            session.pop("last_deleted", None)
            return redirect('/dashboard')
        else:
            flash("Invalid unsername or password!")

       
    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop("last_deleted", None)
    return redirect('/login')



@app.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id, deleted=False).all()

    return render_template('dashboard.html', tasks=tasks, date=date)



@app.route('/add-task', methods=['POST'])
@login_required
def add_task():

    title = request.form['title']
    description = request.form['description']
    due_date_str = request.form.get('due_date')

    due_date = None

    if due_date_str:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

    new_task = Task(
        title=title,
        description=description,
        due_date=due_date,
        user_id=current_user.id
    )

    db.session.add(new_task)
    db.session.commit()

    return redirect('/dashboard')



@app.route('/delete-task/<int:id>')
@login_required
def delete_task(id):

    task = Task.query.get_or_404(id)

    if task.user_id != current_user.id:
        return redirect('/dashboard')
    
    task.deleted = True
    db.session.commit()
    session["last_deleted"] = task.id
    

    return redirect('/dashboard')



@app.route('/complete-task/<int:id>')
@login_required
def complete_task(id):

    task = Task.query.get_or_404(id)

    if task.user_id != current_user.id:
        return redirect('/dashboard')

    task.completed = True
    db.session.commit()

    return redirect('/dashboard')



@app.route('/edit-task/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):

    task = Task.query.get_or_404(id)

    if task.user_id != current_user.id:
        return redirect('/dashboard')

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']

        due_date_str = request.form.get('due_date')

        if due_date_str:
            task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        else:
            task.due_date = None

        db.session.commit()

        return redirect('/dashboard')
    
    return render_template('edit_task.html', task=task)



@app.route('/undo-delete/<int:id>')
@login_required
def undo_delete(id):

    task = Task.query.get_or_404(id)

    if task.user_id != current_user.id:
        return redirect('/dashboard')
    
    task.deleted = False
    db.session.commit()

    session.pop("last_deleted", None)

    return redirect('/dashboard')
