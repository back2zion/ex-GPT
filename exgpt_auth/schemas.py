from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str

class PermissionUpdate(BaseModel):
    department_code: str
    document_category: str
    access_type: int
    download_permission: int 