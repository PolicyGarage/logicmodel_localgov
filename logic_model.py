import os
import json
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv
from search_utils import combine_search_queries

# 環境変数の読み込み
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_logic_model(policy_name: str, outcome: str, municipality: str) -> Dict:
    """
    ロジックモデルを生成する
    
    Args:
        policy_name (str): 政策名
        outcome (str): 最終アウトカム
        municipality (str): 自治体名
        
    Returns:
        Dict: ロジックモデルの情報
    """
    # Web検索の実行
    search_results = combine_search_queries(policy_name, outcome, municipality)
    
    # 検索結果をテキストに変換
    search_text = "\n".join([f"タイトル: {r['title']}\n内容: {r['body']}" for r in search_results])
    
    # OpenAI APIを使用してロジックモデルを生成
    prompt = f"""
    以下の情報を基に、{municipality}の{policy_name}に関するロジックモデルを作成してください。
    最終アウトカムは「{outcome}」です。
    
    検索結果:
    {search_text}
    
    以下の形式でJSONを出力してください：
    {{
        "inputs": ["入力1", "入力2", ...],
        "activities": ["活動1", "活動2", ...],
        "outputs": ["出力1", "出力2", ...],
        "outcomes": ["成果1", "成果2", ...],
        "final_outcome": "{outcome}",
        "explanation": "ロジックモデルの説明文"
    }}

    なお、inputs、activities、outputs、outcomesは、それぞれ3～5個程度にとどめてください。
    """
    
    response = client.chat.completions.create(
        model="o4-mini-2025-04-16",
        messages=[
            {"role": "system", "content": "あなたは自治体の政策分析の専門家です。"},
            {"role": "user", "content": prompt}
        ],
    )
    
    # レスポンスをJSONとしてパース
    import re
    content = response.choices[0].message.content
    content_clean = re.sub(r"^```json\n|\n```$", "", content.strip())
    logic_model = json.loads(content_clean)
    return logic_model

def create_logic_model_mermaid(logic_model: Dict) -> str:
    """
    Mermaid記法でロジックモデルの図を作成する
    
    Args:
        logic_model (Dict): ロジックモデルの情報
        
    Returns:
        str: Mermaid記法の文字列
    """
    # Mermaid記法の開始
    mermaid = "graph LR\n"
    
    # スタイルの定義
    mermaid += "    classDef input fill:#1f77b4,stroke:#1f77b4,color:white\n"
    mermaid += "    classDef activity fill:#ff7f0e,stroke:#ff7f0e,color:white\n"
    mermaid += "    classDef output fill:#2ca02c,stroke:#2ca02c,color:white\n"
    mermaid += "    classDef outcome fill:#d62728,stroke:#d62728,color:white\n"
    mermaid += "    classDef final fill:#9467bd,stroke:#9467bd,color:white\n"
    
    # ノードの定義
    for i, input_item in enumerate(logic_model['inputs']):
        node_id = f"input_{i}"
        mermaid += f"    {node_id}[\"{input_item}\"]:::input\n"
    
    for i, activity in enumerate(logic_model['activities']):
        node_id = f"activity_{i}"
        mermaid += f"    {node_id}[\"{activity}\"]:::activity\n"
    
    for i, output in enumerate(logic_model['outputs']):
        node_id = f"output_{i}"
        mermaid += f"    {node_id}[\"{output}\"]:::output\n"
    
    for i, outcome in enumerate(logic_model['outcomes']):
        node_id = f"outcome_{i}"
        mermaid += f"    {node_id}[\"{outcome}\"]:::outcome\n"
    
    mermaid += f"    final[\"{logic_model['final_outcome']}\"]:::final\n"
    
    # エッジの定義
    for i in range(len(logic_model['inputs'])):
        for j in range(len(logic_model['activities'])):
            mermaid += f"    input_{i} --> activity_{j}\n"
    
    for i in range(len(logic_model['activities'])):
        for j in range(len(logic_model['outputs'])):
            mermaid += f"    activity_{i} --> output_{j}\n"
    
    for i in range(len(logic_model['outputs'])):
        for j in range(len(logic_model['outcomes'])):
            mermaid += f"    output_{i} --> outcome_{j}\n"
    
    for i in range(len(logic_model['outcomes'])):
        mermaid += f"    outcome_{i} --> final\n"
    
    return mermaid 

import streamlit.components.v1 as components

def display_mermaid_chart(mermaid_code: str):
    html = f"""
    <div class="mermaid">
    {mermaid_code}
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    """
    components.html(html, height=1000, scrolling=True)
