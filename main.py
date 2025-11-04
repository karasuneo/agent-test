"""メインエントリーポイント"""

from src.test_agent import root_agent, step1_get_client_info, step2_process_client_data


def test_tools():
    """ツールの動作テスト"""
    print("=" * 50)
    print("顧問先情報取得・処理ツールのテスト")
    print("=" * 50)

    # テスト1: 【ステップ1】顧問先情報取得（部分一致）
    print("\n【テスト1】【ステップ1】顧問先情報取得 - 「株式会社」で検索")
    result1 = step1_get_client_info("株式会社")
    print(f"検索結果: {result1['count']}件")
    print(f"最初の5件: {result1['matches'][:5]}")

    # テスト2: 【ステップ1】顧問先情報取得（具体的な名前）
    print("\n【テスト2】【ステップ1】顧問先情報取得 - 「株式会社青空」で検索")
    result2 = step1_get_client_info("株式会社青空")
    print(f"検索結果: {result2['count']}件")
    print(f"一致: {result2['matches']}")

    # テスト3: 【ステップ2】顧問先情報処理（完全一致）
    print("\n【テスト3】【ステップ2】顧問先情報処理 - 「株式会社青空」への自動入力")
    result3 = step2_process_client_data(client_name="株式会社青空")
    print(f"処理結果: {result3['message']}")
    print(f"検証: {result3['verified']}")
    print(f"詳細: {result3['details']}")

    # テスト4: 【ステップ2】顧問先情報処理（完全一致検証）
    print("\n【テスト4】【ステップ2】顧問先情報処理 - 「青空」で検索（完全一致なし）")
    result4 = step2_process_client_data(client_name="青空")
    print(f"処理結果: {result4['message']}")
    print(f"検証: {result4['verified']}")
    print(f"成功: {result4['success']}")

    # テスト5: 【ステップ2】顧問先情報処理（存在しない顧問先）
    print("\n【テスト5】【ステップ2】顧問先情報処理 - 存在しない顧問先")
    result5 = step2_process_client_data(client_name="存在しない会社")
    print(f"処理結果: {result5['message']}")
    print(f"成功: {result5['success']}")

    print("\n" + "=" * 50)
    print("テスト完了")
    print("=" * 50)


def main():
    """メイン処理"""
    print("agent-test: 顧問先情報取得・処理システム\n")

    # ツールのテスト実行
    test_tools()

    print("\n\nエージェント情報:")
    print(f"名前: {root_agent.name}")
    print(f"説明: {root_agent.description}")
    print(f"ツール数: {len(root_agent.tools)}")
    print(f"ツール: {[tool.__name__ for tool in root_agent.tools]}")


if __name__ == "__main__":
    main()
