
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Task
from datetime import datetime, timedelta

class TaskMasterTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('development')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task Master', response.data)
    
    def test_add_task(self):
        response = self.client.post('/add', data={
            'content': 'Test task',
            'category': 'Work',
            'deadline': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test task', response.data)
    
    def test_add_task_with_deadline(self):
        future_date = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        response = self.client.post('/add', data={
            'content': 'Task with deadline',
            'category': 'Study',
            'deadline': future_date
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_delete_task(self):
        with self.app.app_context():
            task = Task(content='Task to delete', category='Personal')
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        response = self.client.get(f'/delete/{task_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_toggle_complete(self):
        with self.app.app_context():
            task = Task(content='Task to complete', category='Work')
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        response = self.client.get(f'/toggle/{task_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with self.app.app_context():
            task = Task.query.get(task_id)
            self.assertTrue(task.completed)
    
    def test_update_task(self):
        with self.app.app_context():
            task = Task(content='Original content', category='Personal')
            db.session.add(task)
            db.session.commit()
            task_id = task.id
        
        response = self.client.post(f'/update/{task_id}', data={
            'content': 'Updated content',
            'category': 'Work',
            'deadline': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with self.app.app_context():
            task = Task.query.get(task_id)
            self.assertEqual(task.content, 'Updated content')
            self.assertEqual(task.category, 'Work')
    
    def test_is_overdue(self):
        with self.app.app_context():
            past_date = datetime.utcnow() - timedelta(days=1)
            task = Task(content='Overdue task', category='Work', deadline=past_date)
            self.assertTrue(task.is_overdue())
            
            future_date = datetime.utcnow() + timedelta(days=1)
            task2 = Task(content='Future task', category='Work', deadline=future_date)
            self.assertFalse(task2.is_overdue())

if __name__ == '__main__':
    unittest.main()
