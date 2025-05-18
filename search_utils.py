from duckduckgo_search import DDGS
from typing import List, Dict

def search_web(query: str, max_results: int = 10) -> List[Dict]:
    """
    DuckDuckGoを使用してWeb検索を実行し、結果を返す
    
    Args:
        query (str): 検索クエリ
        max_results (int): 取得する結果の最大数
        
    Returns:
        List[Dict]: 検索結果のリスト
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            # 結果の形式を統一
            formatted_results = []
            for result in results:
                formatted_result = {
                    'title': result.get('title', ''),
                    'body': result.get('body', ''),
                    'link': result.get('href', '')  # 'link'を'href'に変更
                }
                formatted_results.append(formatted_result)
            return formatted_results
    except Exception as e:
        print(f"検索中にエラーが発生しました: {e}")
        return []

def combine_search_queries(policy_name: str, outcome: str, municipality: str) -> List[Dict]:
    """
    政策名、最終アウトカム、自治体名を組み合わせて検索を実行
    
    Args:
        policy_name (str): 政策名
        outcome (str): 最終アウトカム
        municipality (str): 自治体名
        
    Returns:
        List[Dict]: 検索結果のリスト
    """
    queries = [
        f"{policy_name} {municipality}",
        f"{outcome} {municipality}",
        f"{policy_name} {outcome} {municipality}"
    ]
    
    all_results = []
    for query in queries:
        results = search_web(query)
        all_results.extend(results)
    
    # 重複を除去（URLベース）
    seen_urls = set()
    unique_results = []
    for result in all_results:
        if result['link'] not in seen_urls:
            seen_urls.add(result['link'])
            unique_results.append(result)
    
    return unique_results 