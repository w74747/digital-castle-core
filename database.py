import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """مدير قاعدة البيانات لـ Digital Castle S.P.C"""
    
    def __init__(self, db_path: str = 'digital_castle.db'):
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """تهيئة قاعدة البيانات وإنشاء الجداول"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            # جدول الوكلاء
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    name_ar TEXT NOT NULL,
                    sector TEXT NOT NULL,
                    description TEXT,
                    model_assignment TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول المشاريع
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    status TEXT DEFAULT 'planning',
                    description TEXT,
                    market_problem TEXT,
                    target_audience TEXT,
                    market_analysis TEXT,
                    feasibility_analysis TEXT,
                    specifications TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول المهام
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    project_id INTEGER NOT NULL,
                    task_name TEXT NOT NULL,
                    assigned_agent TEXT,
                    status TEXT DEFAULT 'pending',
                    description TEXT,
                    specifications TEXT,
                    result TEXT,
                    tokens_used INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            ''')
            
            # جدول المستندات المولدة
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    doc_type TEXT NOT NULL,
                    project_id INTEGER,
                    title TEXT NOT NULL,
                    file_path TEXT,
                    content TEXT,
                    status TEXT DEFAULT 'generated',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            ''')
            
            # جدول سجل استهلاك التوكنز
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS token_usage (
                    id INTEGER PRIMARY KEY,
                    provider TEXT NOT NULL,
                    tokens_used INTEGER NOT NULL,
                    task_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول السجلات والأحداث
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id INTEGER,
                    user_id TEXT,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول الإشعارات والتنبيهات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY,
                    alert_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    provider TEXT,
                    severity TEXT DEFAULT 'info',
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP
                )
            ''')
            
            # جدول المستخدمين والأذونات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id TEXT UNIQUE NOT NULL,
                    username TEXT,
                    role TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            logger.info("✅ Database initialized successfully")
            
        except sqlite3.Error as e:
            logger.error(f"❌ Database initialization error: {str(e)}")
            raise

    # ================ AGENTS ================
    
    def add_agent(self, name: str, name_ar: str, sector: str, description: str = '', model_assignment: str = ''):
        """إضافة وكيل جديد"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO agents (name, name_ar, sector, description, model_assignment)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, name_ar, sector, description, model_assignment))
            self.conn.commit()
            logger.info(f"Agent added: {name}")
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error adding agent: {str(e)}")
            return None

    def get_all_agents(self) -> List[Dict]:
        """الحصول على جميع الوكلاء"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM agents WHERE is_active = 1')
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching agents: {str(e)}")
            return []

    # ================ PROJECTS ================
    
    def create_project(
        self,
        name: str,
        description: str = '',
        market_problem: str = '',
        target_audience: str = ''
    ) -> Optional[int]:
        """إنشاء مشروع جديد"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO projects (name, description, market_problem, target_audience)
                VALUES (?, ?, ?, ?)
            ''', (name, description, market_problem, target_audience))
            self.conn.commit()
            project_id = cursor.lastrowid
            logger.info(f"Project created: {name} (ID: {project_id})")
            return project_id
        except sqlite3.Error as e:
            logger.error(f"Error creating project: {str(e)}")
            return None

    def update_project(self, project_id: int, **kwargs):
        """تحديث بيانات المشروع"""
        try:
            allowed_fields = {
                'name', 'status', 'description', 'market_problem',
                'target_audience', 'market_analysis', 'feasibility_analysis',
                'specifications'
            }
            fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not fields:
                return False
            
            fields['updated_at'] = datetime.now()
            
            set_clause = ', '.join([f"{k} = ?" for k in fields.keys()])
            values = list(fields.values()) + [project_id]
            
            cursor = self.conn.cursor()
            cursor.execute(f'UPDATE projects SET {set_clause} WHERE id = ?', values)
            self.conn.commit()
            logger.info(f"Project {project_id} updated")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating project: {str(e)}")
            return False

    def get_project(self, project_id: int) -> Optional[Dict]:
        """الحصول على بيانات المشروع"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error fetching project: {str(e)}")
            return None

    def get_all_projects(self, status: Optional[str] = None) -> List[Dict]:
        """الحصول على جميع المشاريع"""
        try:
            cursor = self.conn.cursor()
            if status:
                cursor.execute('SELECT * FROM projects WHERE status = ?', (status,))
            else:
                cursor.execute('SELECT * FROM projects')
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching projects: {str(e)}")
            return []

    # ================ TASKS ================
    
    def create_task(
        self,
        project_id: int,
        task_name: str,
        description: str = '',
        specifications: str = ''
    ) -> Optional[int]:
        """إنشاء مهمة جديدة"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO tasks (project_id, task_name, description, specifications)
                VALUES (?, ?, ?, ?)
            ''', (project_id, task_name, description, specifications))
            self.conn.commit()
            task_id = cursor.lastrowid
            logger.info(f"Task created: {task_name} (ID: {task_id})")
            return task_id
        except sqlite3.Error as e:
            logger.error(f"Error creating task: {str(e)}")
            return None

    def update_task(self, task_id: int, **kwargs):
        """تحديث بيانات المهمة"""
        try:
            allowed_fields = {
                'assigned_agent', 'status', 'result', 'tokens_used', 'completed_at'
            }
            fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not fields:
                return False
            
            set_clause = ', '.join([f"{k} = ?" for k in fields.keys()])
            values = list(fields.values()) + [task_id]
            
            cursor = self.conn.cursor()
            cursor.execute(f'UPDATE tasks SET {set_clause} WHERE id = ?', values)
            self.conn.commit()
            logger.info(f"Task {task_id} updated")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error updating task: {str(e)}")
            return False

    def get_project_tasks(self, project_id: int) -> List[Dict]:
        """الحصول على جميع مهام المشروع"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE project_id = ? ORDER BY created_at', (project_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching tasks: {str(e)}")
            return []

    # ================ DOCUMENTS ================
    
    def add_document(
        self,
        doc_type: str,
        title: str,
        file_path: str,
        project_id: Optional[int] = None,
        content: str = ''
    ) -> Optional[int]:
        """إضافة مستند جديد"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO documents (doc_type, project_id, title, file_path, content)
                VALUES (?, ?, ?, ?, ?)
            ''', (doc_type, project_id, title, file_path, content))
            self.conn.commit()
            doc_id = cursor.lastrowid
            logger.info(f"Document added: {title} (ID: {doc_id})")
            return doc_id
        except sqlite3.Error as e:
            logger.error(f"Error adding document: {str(e)}")
            return None

    def get_project_documents(self, project_id: int) -> List[Dict]:
        """الحصول على مستندات المشروع"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM documents WHERE project_id = ?', (project_id,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching documents: {str(e)}")
            return []

    # ================ TOKEN USAGE ================
    
    def log_token_usage(self, provider: str, tokens_used: int, task_id: str = ''):
        """تسجيل استهلاك التوكنز"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO token_usage (provider, tokens_used, task_id)
                VALUES (?, ?, ?)
            ''', (provider, tokens_used, task_id))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error logging token usage: {str(e)}")

    def get_token_usage_by_provider(self, provider: str, days: int = 30) -> int:
        """الحصول على إجمالي استهلاك التوكنز"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT SUM(tokens_used) as total FROM token_usage
                WHERE provider = ? AND timestamp >= datetime('now', '-' || ? || ' days')
            ''', (provider, days))
            result = cursor.fetchone()
            return result['total'] or 0 if result else 0
        except sqlite3.Error as e:
            logger.error(f"Error fetching token usage: {str(e)}")
            return 0

    # ================ AUDIT LOG ================
    
    def log_event(self, event_type: str, entity_type: str, entity_id: int = 0, user_id: str = '', details: str = ''):
        """تسجيل الحدث في السجل"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO audit_log (event_type, entity_type, entity_id, user_id, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_type, entity_type, entity_id, user_id, details))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error logging event: {str(e)}")

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """الحصول على سجل الأحداث"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching audit log: {str(e)}")
            return []

    # ================ ALERTS ================
    
    def create_alert(self, alert_type: str, message: str, provider: str = '', severity: str = 'info'):
        """إنشاء تنبيه جديد"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO alerts (alert_type, message, provider, severity)
                VALUES (?, ?, ?, ?)
            ''', (alert_type, message, provider, severity))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error creating alert: {str(e)}")
            return None

    def get_active_alerts(self) -> List[Dict]:
        """الحصول على التنبيهات النشطة"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM alerts WHERE status = "active" ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching alerts: {str(e)}")
            return []

    def close_alert(self, alert_id: int):
        """إغلاق تنبيه"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE alerts SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (alert_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error closing alert: {str(e)}")

    # ================ CLEANUP ================
    
    def close(self):
        """إغلاق اتصال قاعدة البيانات"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


# إنشاء instance عام من مدير قاعدة البيانات
db = DatabaseManager()
