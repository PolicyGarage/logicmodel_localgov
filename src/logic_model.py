import json
import asyncio
from typing import Dict, List
import streamlit.components.v1 as components
from agents import Agent, Runner
from logic_schema import LogicModel, LogicGraphModel
import textwrap


# --- Agent定義 ---

logic_agent = Agent(
    name="LogicModelBuilder",
    model="gpt-4.1-2025-04-14", #o4-mini-2025-04-16
    instructions="""
あなたは自治体の政策分析に特化したアシスタントです。
以下のJSON形式でロジックモデル要素を生成してください：

{
  "inputs": [input1, input2 ...],
  "activities": [activity1, activity2 ...],
  "outputs": [output1, output2 ...],
  "outcomes": [outcome1, outcome2 ...],
  "final_outcome": "final_outcome",
  "explanation": "explanation"
}

各カテゴリの要素は3〜5個程度にまとめて、論理的に一貫性のある内容にしてください。
各カテゴリの要素の表記は簡潔なものにしてください。（）で情報源を示す必要はありません。
""",
    output_type=LogicModel
)

edge_generator_agent = Agent(
    name="EdgeGenerator",
    model="gpt-4.1-2025-04-14", #o4-mini-2025-04-16
    instructions="""
あなたはロジックモデル設計の専門家です。
以下のノード群に基づき、各要素間の因果関係を表す "edges"（接続）を構成してください。

出力形式（JSON）:
{
  "edges": [
    ["input_0", "activity_0"],
    ["activity_0", "output_0"],
    ["output_0", "outcome_0"],
    ["outcome_0", "final_outcome"]
  ]
}
""",
    output_type=LogicGraphModel
)


# --- ロジックモデル生成 ---

def generate_logic_model_with_agents(
    policy_name: str,
    outcome: str,
    municipality: str,
    search_summary: str
) -> Dict:
    prompt = f"""
政策名: {policy_name}
最終アウトカム: {outcome}
自治体名: {municipality}

以下の情報をもとに、{municipality}ならではの現状分析や特徴を反映した将来の{outcome}の達成に向けたロジックモデルを具体的に生成してください
なお、必ず情報源の情報に基づき記載し、数字を中心にハルシネーションに気をつけること


{search_summary}

以下はロジックモデル作成のポイントです
・最終アウトカムの設定：誰のどんな課題をどう変えたいか？最終的に目指す社会的成果を明確にする。
・中間・初期アウトカムの整理：最終アウトカムに至るまでに必要な段階的変化を洗い出す。
・活動・アウトプットの具体化：成果を生むために「誰に」「どんなサービスを」「どう提供するか」を考える。
・インプットの明示：活動に必要な人材・資金・設備などを挙げる。
・整合性チェック：縦：因果関係が筋道立っているか？横：各階層で抜け漏れがないか？


"""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    result = Runner.run_sync(logic_agent, prompt)
    return result.final_output.dict()


# --- ノード名（日本語）→ ID 変換マップを作成 ---

def build_node_id_map(logic_model: Dict) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    prefix_map = {
        "inputs": "input",
        "activities": "activity",
        "outputs": "output",
        "outcomes": "outcome"
    }
    for category, prefix in prefix_map.items():
        for i, label in enumerate(logic_model.get(category, [])):
            mapping[label] = f"{prefix}_{i}"
    mapping[logic_model["final_outcome"]] = "final_outcome"
    return mapping


# --- エッジ生成（EdgeGenerator経由） ---

def generate_edges_from_nodes(logic_model: Dict) -> List[List[str]]:
    label_to_id = build_node_id_map(logic_model)
    valid_ids = set(label_to_id.values()) | {"final_outcome"}

    # ← ここで prompt を定義
    prompt = f"ノード一覧:\n{json.dumps(label_to_id, ensure_ascii=False, indent=2)}"

    # EdgeGenerator 呼び出し
    result = Runner.run_sync(edge_generator_agent, prompt)
    label_edges: List[List[str]] = result.final_output.edges

    id_edges = []
    for src, dst in label_edges:
        if src in valid_ids and dst in valid_ids:
            id_edges.append([src, dst])
        elif src in label_to_id and dst in label_to_id:
            id_edges.append([label_to_id[src], label_to_id[dst]])
        else:
            print(f"⚠️ 未知のノード: {src} -> {dst}")
    return id_edges

# --- Mermaid ノード名エスケープ ---

def escape_mermaid_label(text: str) -> str:
    return text.replace('"', '\\"').replace("\n", " ").strip()


# --- Mermaidコード生成 ---

def create_mermaid_from_logic_model(
    logic_model: Dict,
    edges: List[List[str]]
) -> str:
    mermaid = "graph LR\n"

    # スタイル
    mermaid += "classDef input fill:#1f77b4,stroke:#1f77b4,color:white;\n"
    mermaid += "classDef activity fill:#ff7f0e,stroke:#ff7f0e,color:white;\n"
    mermaid += "classDef output fill:#2ca02c,stroke:#2ca02c,color:white;\n"
    mermaid += "classDef outcome fill:#d62728,stroke:#d62728,color:white;\n"
    mermaid += "classDef final fill:#9467bd,stroke:#9467bd,color:white;\n"

    # ノード
    for prefix, category in [
        ("input", "inputs"),
        ("activity", "activities"),
        ("output", "outputs"),
        ("outcome", "outcomes")
    ]:
        for i, label in enumerate(logic_model.get(category, [])):
            node_id = f"{prefix}_{i}"
            mermaid += f'{node_id}["{escape_mermaid_label(label)}"]:::{prefix}\n'

    mermaid += f'final_outcome["{escape_mermaid_label(logic_model["final_outcome"])}"]:::final\n'

    # エッジ
    for from_id, to_id in edges:
        mermaid += f"{from_id} --> {to_id}\n"

    return mermaid


# --- Mermaid表示（Streamlit）

def display_mermaid_chart(mermaid_code: str):
    # これを入れるだけで、先頭スペースが落ちます
    mermaid_code = textwrap.dedent(mermaid_code).strip()

    # ESM ではなく UMD 版を読み込む（後述）
    html = textwrap.dedent(f"""
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
      mermaid.initialize({{ startOnLoad: true }});
    </script>
    <div class="mermaid">
    {mermaid_code}
    </div>
    """)
    components.html(html, height=600, scrolling=True)
