from pydantic import BaseModel
from typing import List,Dict,Any, Optional
from datetime import datetime

class Ingestdata(BaseModel):
    collection_name: str
    documents: List[str] 
    metadata: List[Dict[str, Any]] 

class SearchRequest(BaseModel):
    collection_name: str
    query :str 
    from_date:Optional[datetime] =None
    to_date:Optional[datetime] = None
