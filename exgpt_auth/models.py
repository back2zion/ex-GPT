from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(String(50), primary_key=True)
    department_code = Column(String(20), nullable=False)
    position_level = Column(Integer, nullable=False)
    system_access_level = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP)

class DocumentPermission(Base):
    __tablename__ = "document_permissions"
    document_id = Column(String(100), primary_key=True)
    source_system = Column(String(50))
    owner_department = Column(String(20))
    access_departments = Column(JSON)
    access_type = Column(Integer, nullable=False)
    download_permission = Column(Integer, nullable=False)
    is_sensitive = Column(Boolean, default=False)
    metadata = Column(JSON)
    created_at = Column(TIMESTAMP)

class PermissionMatrix(Base):
    __tablename__ = "permission_matrix"
    department_code = Column(String(20), primary_key=True)
    document_category = Column(String(50), primary_key=True)
    access_type = Column(Integer)
    download_permission = Column(Integer)

class AccessLog(Base):
    __tablename__ = "access_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50))
    document_id = Column(String(100))
    action = Column(String(20))
    result = Column(String(20))
    ip_address = Column(String(50))
    timestamp = Column(TIMESTAMP) 