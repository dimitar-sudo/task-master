from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from . import db
from .models import Task
from .forms import TaskManager
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '')
    sort_by = request.args.get('sort', 'date_created')
    show_completed = request.args.get('completed', 'all')
    
    query = Task.query
    
    if search_query:
        query = query.filter(Task.content.ilike(f'%{search_query}%'))
    
    if category_filter:
        query = query.filter(Task.category == category_filter)
    
    if show_completed == 'active':
        query = query.filter(Task.completed == False)
    elif show_completed == 'completed':
        query = query.filter(Task.completed == True)
    
    if sort_by == 'deadline':
        query = query.order_by(Task.deadline.asc().nullslast())
    elif sort_by == 'category':
        query = query.order_by(Task.category.asc())
    elif sort_by == 'completed':
        query = query.order_by(Task.completed.asc())
    else:
        query = query.order_by(Task.date_created.desc())
    
    tasks = query.all()
    categories = TaskManager.get_category_choices()
    
    return render_template('index.html', 
                         tasks=tasks, 
                         categories=categories,
                         now=datetime.utcnow())

@main.route('/add', methods=['POST'])
def add_task():
    try:
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'Personal')
        deadline_str = request.form.get('deadline', '')
        
        errors, deadline = TaskManager.validate_task_data(content, category, deadline_str)
        
        if errors:
            flash(' '.join(errors), 'error')
            return redirect(url_for('main.index'))
        
        new_task = Task(
            content=content,
            category=category,
            deadline=deadline
        )
        
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding task: {str(e)}', 'error')
    
    return redirect(url_for('main.index'))

@main.route('/delete/<int:task_id>')
def delete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting task: {str(e)}', 'error')
    
    return redirect(url_for('main.index'))

@main.route('/update/<int:task_id>', methods=['GET', 'POST'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'POST':
        try:
            content = request.form.get('content', '').strip()
            category = request.form.get('category', 'Personal')
            deadline_str = request.form.get('deadline', '')
            
            errors, deadline = TaskManager.validate_task_data(content, category, deadline_str)
            
            if errors:
                flash(' '.join(errors), 'error')
                return render_template('update.html', 
                                     task=task, 
                                     categories=TaskManager.get_category_choices())
            
            task.content = content
            task.category = category
            task.deadline = deadline
            
            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating task: {str(e)}', 'error')
    
    return render_template('update.html', 
                         task=task, 
                         categories=TaskManager.get_category_choices())

@main.route('/toggle/<int:task_id>')
def toggle_complete(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        task.completed = not task.completed
        db.session.commit()
        flash('Task status updated!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating task: {str(e)}', 'error')
    
    return redirect(url_for('main.index'))

@main.route('/api/tasks')
def api_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])
