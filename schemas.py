from pydantic import BaseModel, Field
from typing import Optional, Literal

class ExtractionResult(BaseModel):
    payee: Optional[str]
    amount: Optional[float]
    amount_type: Optional[Literal["gross", "net", "unknown"]]
    iban: Optional[str]