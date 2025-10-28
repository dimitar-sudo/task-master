from datetime import datetime

class TaskManager:
    
    @staticmethod
    def validate_task_data(content, category, deadline_str=None):
        errors = []
        
        if not content or len(content.strip()) == 0:
            errors.append('Task content cannot be empty')
        
        if len(content) > 500:
            errors.append('Task content cannot exceed 500 characters')
        
        valid_categories = ['Work', 'Study', 'Personal', 'Health', 'Finance', 'Other']
        if category not in valid_categories:
            errors.append(f'Invalid category. Choose from: {", ".join(valid_categories)}')
        
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str)
                if deadline < datetime.utcnow():
                    errors.append('Deadline cannot be in the past')
            except ValueError:
                errors.append('Invalid deadline format')
        
        return errors, deadline
    
    @staticmethod
    def get_category_choices():
        return ['Work', 'Study', 'Personal', 'Health', 'Finance', 'Other']
