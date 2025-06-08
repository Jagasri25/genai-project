# backend/app/models/base.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship("Role", back_populates="users")
    projects = relationship("ProjectMember", back_populates="user")
    tasks = relationship("TaskAssignment", back_populates="user")
    messages = relationship("ChatMessage", back_populates="user")

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    permissions = Column(JSON)  # {'read': True, 'write': True, ...}
    
    # Relationships
    users = relationship("User", back_populates="role")

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(20), default='active')  # active, completed, paused
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    members = relationship("ProjectMember", back_populates="project")
    tasks = relationship("Task", back_populates="project")
    documents = relationship("ProjectDocument", back_populates="project")

class ProjectMember(Base):
    __tablename__ = 'project_members'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    role = Column(String(50))  # member, lead, etc.
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="projects")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    title = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), default='todo')  # todo, in_progress, done
    priority = Column(String(20))  # low, medium, high
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignments = relationship("TaskAssignment", back_populates="task")
    comments = relationship("TaskComment", back_populates="task")

class TaskAssignment(Base):
    __tablename__ = 'task_assignments'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="assignments")
    user = relationship("User", back_populates="tasks")

class TaskComment(Base):
    __tablename__ = 'task_comments'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User")

class ProjectDocument(Base):
    __tablename__ = 'project_documents'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    name = Column(String(100), nullable=False)
    file_path = Column(String(255), nullable=False)
    uploader_id = Column(Integer, ForeignKey('users.id'))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    uploader = relationship("User")

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text, nullable=False)
    is_bot = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="messages")

# Additional tables would include:
# - Meeting, MeetingAttendance, Notification, TimeLog, Skill, UserSkill, 
# - Department, Team, TeamMember, Client, ClientProject, AuditLog, 
# - LeaveRequest, WorkSchedule, etc.

# Initialize database
DATABASE_URL = "postgresql+psycopg2://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()