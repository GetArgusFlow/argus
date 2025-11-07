from pydantic import BaseModel
from typing import List, Dict, Any, Union


class ParseRequest(BaseModel):
    html_snippet: str


# Define the structure of the response.
# This should match your schema.json to ensure consistency.
class ParseResponse(BaseModel):
    category: str
    details: Union[List[str], Dict[str, Any]]
