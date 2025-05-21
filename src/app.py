import streamlit as st
from logic_model import (
    generate_logic_model_with_agents,
    generate_edges_from_nodes,
    create_mermaid_from_logic_model,
    display_mermaid_chart,
)
from search_utils import (
    search_policy_logic_model_related,
    search_municipality_policy,
)

SEARCH_LIMIT = 10

# --- ページ設定 ---
st.set_page_config(
    page_title="ロジックモデル作成支援ツール",
    page_icon="🏛️",
    layout="wide"
)

st.title("ロジックモデル作成支援ツール")

st.markdown("""
このツールは、自治体の施策や事業に関するロジックモデルを自動生成します。  
政策名・最終アウトカム・自治体名を入力すると、Web検索により関連情報を収集し、AIがロジックモデルを構築します。
""")

# --- 入力フォーム ---
with st.form("logic_model_form"):
    policy_name = st.text_input("政策名・分野", placeholder="例：子育て支援")
    outcome = st.text_input("最終アウトカム", placeholder="例：子育て世帯の生活満足度向上")
    municipality = st.text_input("自治体名", placeholder="例：東京都渋谷区")

    submitted = st.form_submit_button("ロジックモデルを作成する")

# --- 処理本体 ---
if submitted:
    if not all([policy_name, outcome, municipality]):
        st.error("すべての項目を入力してください。")
    else:
        try:
            # Step 1: ロジックモデル関連情報検索
            with st.spinner("ロジックモデル関連情報を検索中..."):
                logic_results = search_policy_logic_model_related(policy_name, outcome)

                st.markdown("### 当該政策のロジックモデル関連情報の検索結果")
                for i, result in enumerate(logic_results[:SEARCH_LIMIT], 1):
                    with st.expander(f"{i}. {result['title']}"):
                        st.markdown(f"**URL:** [{result['link']}]({result['link']})")
                        st.markdown(f"**内容:** {result['body']}")

            # Step 2: 自治体政策情報検索
            with st.spinner("自治体政策情報を検索中..."):
                muni_results = search_municipality_policy(policy_name, municipality)

                st.markdown("### 当該政策の自治体情報の検索結果")
                for i, r in enumerate(muni_results[:SEARCH_LIMIT]):
                    with st.expander(f"{i+1}. {r['title']}"):
                        st.markdown(f"**URL:** [{r['link']}]({r['link']})")
                        st.markdown(r['body'])

            # Step 3: 検索情報統合
            combined_results = logic_results + muni_results
            search_summary = "\n\n".join([
                f"タイトル: {r['title']}\n内容: {r['body']}" for r in combined_results[:SEARCH_LIMIT*2]
            ])

            # Step 4: ロジックモデル生成
            with st.spinner("ロジックモデルを生成中..."):
                logic_model = generate_logic_model_with_agents(
                    policy_name, outcome, municipality, search_summary
                )

            # Step 6: 結果表示
            st.success("ロジックモデルの生成が完了しました！")
            st.markdown("### モデルの説明")
            st.write(logic_model["explanation"])

            st.markdown("### ロジックモデル構成")
            st.markdown("#### インプット")
            st.markdown("\n".join(f"- {x}" for x in logic_model["inputs"]))

            st.markdown("#### アクティビティ")
            st.markdown("\n".join(f"- {x}" for x in logic_model["activities"]))

            st.markdown("#### アウトプット")
            st.markdown("\n".join(f"- {x}" for x in logic_model["outputs"]))

            st.markdown("#### アウトカム")
            st.markdown("\n".join(f"- {x}" for x in logic_model["outcomes"]))

            st.markdown("#### 最終アウトカム")
            st.markdown(f"- {logic_model['final_outcome']}")

            # Step 5: エッジ生成
            with st.spinner("因果構造を分析中..."):
                edges = generate_edges_from_nodes(logic_model)

            # Step 7: Mermaid可視化
            with st.spinner("ロジックモデル図を描画中..."):
                mermaid_code = create_mermaid_from_logic_model(logic_model, edges)
                st.markdown("### ロジックモデル図")
                display_mermaid_chart(mermaid_code)

        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
