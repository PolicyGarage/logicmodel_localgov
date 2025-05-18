import streamlit as st
import os
from logic_model import generate_logic_model, display_mermaid_chart, create_logic_model_mermaid
from search_utils import combine_search_queries

# ページ設定
st.set_page_config(
    page_title="自治体施策・事業ロジックモデル作成ツール",
    page_icon="🏛️",
    layout="wide"
)

# タイトル
st.title("🏛️ 自治体施策・事業ロジックモデル作成ツール")

# 説明文
st.markdown("""
このツールは、自治体の施策や事業に関するロジックモデルを自動生成するツールです。
政策名、最終アウトカム、自治体名を入力することで、関連情報を収集し、ロジックモデルを作成します。
""")

# 入力フォーム
with st.form("logic_model_form"):
    policy_name = st.text_input("政策名", placeholder="例：子育て支援事業")
    outcome = st.text_input("最終アウトカム", placeholder="例：子育て世帯の生活満足度向上")
    municipality = st.text_input("自治体名", placeholder="例：東京都渋谷区")
    
    submitted = st.form_submit_button("ロジックモデルを作成する")

if submitted:
    if not all([policy_name, outcome, municipality]):
        st.error("すべての項目を入力してください。")
    else:
        try:
            # 検索の実行
            with st.spinner("関連情報を検索中..."):
                search_results = combine_search_queries(policy_name, outcome, municipality)
                
                # 検索結果の表示
                st.markdown("### 検索結果")
                for i, result in enumerate(search_results[:10], 1):
                    with st.expander(f"{i}. {result['title']}"):
                        st.markdown(f"**URL:** [{result['link']}]({result['link']})")
                        st.markdown(f"**内容:** {result['body']}")
            
            # ロジックモデルの生成
            with st.spinner("ロジックモデルを生成中..."):
                logic_model = generate_logic_model(policy_name, outcome, municipality)
                
                # 結果の表示
                st.success("ロジックモデルの生成が完了しました！")
                
                # 説明文の表示
                st.markdown("### ロジックモデルの説明")
                st.write(logic_model["explanation"])
                
                # テキストベースのロジックモデル表示（縦一列）
                st.markdown("### ロジックモデル（テキスト）")
                
                st.markdown("#### インプット")
                for input_item in logic_model["inputs"]:
                    st.write(f"- {input_item}")
                
                st.markdown("#### アクティビティ")
                for activity in logic_model["activities"]:
                    st.write(f"- {activity}")
                
                st.markdown("#### アウトプット")
                for output in logic_model["outputs"]:
                    st.write(f"- {output}")
                
                st.markdown("#### アウトカム")
                for outcome in logic_model["outcomes"]:
                    st.write(f"- {outcome}")
                
                st.markdown("#### 最終アウトカム")
                st.write(f"- {logic_model['final_outcome']}")
                
                # Mermaid図の生成と表示
                with st.spinner("ロジックモデル図を生成中..."):
                    mermaid_code = create_logic_model_mermaid(logic_model)
                    st.markdown("### ロジックモデル図")
                    display_mermaid_chart(mermaid_code)
        
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}") 