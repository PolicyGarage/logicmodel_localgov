from duckduckgo_search import DDGS
from typing import List, Dict

def search_web(query: str, max_results: int = 10) -> List[Dict]:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', ''),
                    'body': result.get('body', ''),
                    'link': result.get('href', '')
                })
            return formatted_results
    except Exception as e:
        print(f"検索中にエラーが発生しました: {e}")
        return []

# 🔍 検索①: ロジックモデル関連情報を引く
def search_policy_logic_model_related(policy_name: str, outcome: str) -> List[Dict]:
    queries = [
        f"{policy_name} {outcome} ロジックモデル",
        f"{policy_name} ロジックモデル",
        f"{outcome} ロジックモデル"
    ]
    all_results = []
    for query in queries:
        all_results.extend(search_web(query))
    return _deduplicate_results(all_results)

# 🔍 検索②: 自治体×政策名での地域事例検索
def search_municipality_policy(policy_name: str, municipality: str) -> List[Dict]:
    queries = [
        f"{policy_name} {municipality}",
        f"{municipality} {policy_name}"
    ]
    all_results = []
    for query in queries:
        all_results.extend(search_web(query))
    return _deduplicate_results(all_results)

# ✅ 共通の重複除去ロジック
def _deduplicate_results(results: List[Dict]) -> List[Dict]:
    seen = set()
    unique = []
    for r in results:
        if r['link'] not in seen:
            seen.add(r['link'])
            unique.append(r)
    return unique
