from pydantic import BaseModel, Field
from typing import List

class LogicModel(BaseModel):
    inputs: List[str]
    activities: List[str]
    outputs: List[str]
    outcomes: List[str]
    final_outcome: str
    explanation: str

class LogicGraphModel(BaseModel):
    """
    エッジ構造のみ（EdgeGeneratorが返す形式）
    - エッジは [["node_id_1", "node_id_2"], ...] の形
    """
    edges: List[List[str]] = Field(
        ..., 
        description="ノードID間の接続。各要素は2要素のリスト（[from_id, to_id]）"
    )
