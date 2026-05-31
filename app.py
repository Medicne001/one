from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# 配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# 初始化数据库
db = SQLAlchemy(app)

# ========== 数据模型 ==========
class Todo(db.Model):
    """Todo 任务模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    priority = db.Column(db.String(10), default='medium')  # low, medium, high
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'priority': self.priority
        }

# ========== 路由 ==========
@app.route('/')
def index():
    """主页"""
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return render_template('index.html', todos=todos)

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """获取所有任务（API）"""
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return jsonify([todo.to_dict() for todo in todos])

@app.route('/api/todos', methods=['POST'])
def create_todo():
    """创建新任务"""
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': '任务标题不能为空'}), 400
    
    new_todo = Todo(
        title=data['title'],
        description=data.get('description', ''),
        priority=data.get('priority', 'medium')
    )
    
    db.session.add(new_todo)
    db.session.commit()
    
    return jsonify(new_todo.to_dict()), 201

@app.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """获取单个任务"""
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': '任务不存在'}), 404
    return jsonify(todo.to_dict())

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """更新任务"""
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': '任务不存在'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        todo.title = data['title']
    if 'description' in data:
        todo.description = data['description']
    if 'completed' in data:
        todo.completed = data['completed']
    if 'priority' in data:
        todo.priority = data['priority']
    
    db.session.commit()
    return jsonify(todo.to_dict())

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """删除任务"""
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': '任务不存在'}), 404
    
    db.session.delete(todo)
    db.session.commit()
    
    return jsonify({'message': '任务已删除'}), 200

@app.route('/api/todos/<int:todo_id>/toggle', methods=['PUT'])
def toggle_todo(todo_id):
    """切换任务完成状态"""
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': '任务不存在'}), 404
    
    todo.completed = not todo.completed
    db.session.commit()
    
    return jsonify(todo.to_dict())

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计信息"""
    total = Todo.query.count()
    completed = Todo.query.filter_by(completed=True).count()
    pending = total - completed
    
    return jsonify({
        'total': total,
        'completed': completed,
        'pending': pending
    })

# ========== 错误处理 ==========
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '页面不存在'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': '服务器错误'}), 500

# ========== 初始化数据库 ==========
with app.app_context():
    db.create_all()
    print("✅ 数据库已初始化")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
