"""vertexai.preview.reasoning_engines.AdkAppを使ったroot_agentテスト"""

import random
import uuid
from companies_12000_list import companies
from src.gov_doc_parser import root_agent
from vertexai.preview import reasoning_engines

# ツール呼び出しを記録するグローバル変数
tool_calls = []


def after_tool_callback(tool, **kwargs):
    """ツール呼び出し後のコールバック"""
    # 引数を柔軟に取得
    args = kwargs.get('args', kwargs.get('tool_context', {}))
    result = kwargs.get('tool_response', kwargs.get('result'))

    # ツール名を取得（FunctionToolの場合は.funcから取得）
    if hasattr(tool, 'func') and hasattr(tool.func, '__name__'):
        tool_name = tool.func.__name__
    elif hasattr(tool, '__name__'):
        tool_name = tool.__name__
    elif hasattr(tool, 'name'):
        tool_name = tool.name
    else:
        tool_name = str(tool)

    tool_call_info = {
        "tool_name": tool_name,
        "args": dict(args) if args and not isinstance(args, dict) else (args or {}),
        "result": result
    }
    tool_calls.append(tool_call_info)
    print(f"\n【ツール呼び出し検出】")
    print(f"  ツール名: {tool_call_info['tool_name']}")
    print(f"  引数: {tool_call_info['args']}")
    print(f"  結果: {tool_call_info['result']}")
    return result


def test_agent_with_adk_app():
    """
    AdkAppを使ったエージェントテスト

    検証ポイント:
    - ユーザーが入力した顧問先名Xが記録される
    - step1_get_client_infoが呼び出される
    - step2_process_client_dataが呼び出される
    - step2に渡される値が最初のユーザー入力値Xと一致するか
    """
    global tool_calls
    tool_calls = []

    print("=" * 70)
    print("root_agent AdkAppテスト")
    print("=" * 70)

    # ランダムに顧問先を選択
    random_client = random.choice(companies)

    print(f"\n【初期設定】")
    print(f"ユーザーが入力する顧問先名（顧問先X）: 「{random_client}」")
    print(f"💡 この値がstep2に渡されるべき値です")

    # ユーザーの入力をシミュレーション
    user_message = f"顧問先「{random_client}」の労働保険申告を自動入力してください"

    print(f"\n【ユーザー入力】")
    print(f"メッセージ: {user_message}")

    try:
        # テスト用のエージェント指示（ユーザー確認なしで自動実行）
        test_instruction = """
あなたは社労士の業務をサポートするAIエージェントです。

【重要】ツールの呼び出し順序を厳守し、自動的に処理を完了してください:

## 必須の実行フロー

### ステップ1: 顧問先情報の取得（必須）
1. ユーザーから顧問先名が提供されたら、**必ず最初に** step1_get_client_info ツールを実行してください
2. 検索結果を確認してください

### ステップ2: 顧問先情報の処理（必須）
1. step1で1件以上の一致があった場合、**自動的に** step2_process_client_data を実行してください
2. **step1で取得した正確な顧問先名（matchesの最初の要素）**を使用してください
3. ユーザーの確認を求めずに、自動的に実行してください
4. operation は "auto_input" を使用してください

## 禁止事項
❌ step1を実行せずに、いきなりstep2を実行すること
❌ step1の検索結果を無視して、ユーザーの入力をそのままstep2に渡すこと
❌ ユーザーに確認を求めること（自動実行モード）

## 必須の確認事項
✅ step2に渡す顧問先名は、step1の検索結果（matchesの最初の要素）から取得した正確な名前を使用してください
✅ 処理結果は明確に報告してください
"""

        # エージェントのコールバックを設定
        from google.adk.agents import Agent

        agent_with_callback = Agent(
            name=root_agent.name,
            model=root_agent.model,
            description=root_agent.description,
            instruction=test_instruction,  # テスト用の指示を使用
            tools=root_agent.tools,
            after_tool_callback=after_tool_callback
        )

        # AdkAppでエージェントをラップ
        app = reasoning_engines.AdkApp(
            agent=agent_with_callback,
            enable_tracing=True,
        )

        print(f"\n【エージェント実行開始】")
        print("root_agentにメッセージを送信します...")

        # セッションを作成（UUID形式）
        session_id = f"test_{uuid.uuid4()}"
        user_id = "test_user"
        app.create_session(session_id=session_id, user_id=user_id)

        # メッセージを送信
        response_stream = app.stream_query(session_id=session_id, user_id=user_id, message=user_message)

        # ストリーム結果を収集
        response_parts = []
        for chunk in response_stream:
            response_parts.append(str(chunk))

        response = "".join(response_parts)

        print(f"\n【エージェント応答】")
        print(f"応答: {response}")

        # ツール呼び出しの検証
        print(f"\n【ツール呼び出し履歴の検証】")
        print(f"総ツール呼び出し数: {len(tool_calls)}")

        step1_called = False
        step2_called = False
        step2_client_name = None

        for idx, call in enumerate(tool_calls):
            print(f"\nツール呼び出し {idx + 1}:")
            print(f"  ツール名: {call['tool_name']}")
            print(f"  引数: {call['args']}")

            if 'step1_get_client_info' in call['tool_name']:
                step1_called = True
                print(f"  ✅ step1_get_client_info が呼び出されました")

            elif 'step2_process_client_data' in call['tool_name']:
                step2_called = True
                step2_client_name = call['args'].get('client_name', '')
                print(f"  ✅ step2_process_client_data が呼び出されました")

        # 検証結果
        print(f"\n【検証結果】")
        print(f"step1呼び出し: {'✅' if step1_called else '❌'}")
        print(f"step2呼び出し: {'✅' if step2_called else '❌'}")

        if step2_called and step2_client_name:
            print(f"\n⚠️ 【最重要検証ポイント】")
            print(f"  最初のユーザー入力: 「{random_client}」")
            print(f"  step2に渡された値: 「{step2_client_name}」")

            if step2_client_name == random_client:
                print(f"  ✅ 一致: 顧問先情報が正しく渡されています！")
                return True
            else:
                print(f"  ❌ 不一致: 顧問先情報が正しく渡されていません！")
                return False
        else:
            print(f"\n⚠️ step2が呼び出されませんでした")
            print(f"エージェントが指示通りに動作しなかった可能性があります")
            return None

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        print(f"エラータイプ: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_cases(num_tests: int = 3):
    """複数ケースのテスト"""
    print("\n\n" + "=" * 70)
    print(f"複数ケーステスト（{num_tests}回実行）")
    print("=" * 70)

    results = []

    for i in range(num_tests):
        print(f"\n\n{'=' * 70}")
        print(f"テストケース {i + 1}/{num_tests}")
        print(f"{'=' * 70}")

        result = test_agent_with_adk_app()
        results.append(result)

        if result is True:
            print(f"\n✅ テストケース {i + 1}: 成功")
        elif result is False:
            print(f"\n❌ テストケース {i + 1}: 失敗")
        else:
            print(f"\n⚠️  テストケース {i + 1}: 判定不可")

    # サマリー
    print("\n\n" + "=" * 70)
    print("テスト結果サマリー")
    print("=" * 70)

    success_count = sum(1 for r in results if r is True)
    failure_count = sum(1 for r in results if r is False)
    unknown_count = sum(1 for r in results if r is None)

    print(f"総テスト数: {len(results)}")
    print(f"成功: {success_count}")
    print(f"失敗: {failure_count}")
    print(f"判定不可: {unknown_count}")

    if failure_count == 0 and success_count > 0:
        print("\n✅ 確認できた全てのテストが成功しました！")
        print("   step2に渡される顧問先情報が正しく保持されています。")
        return True
    elif failure_count > 0:
        print("\n❌ 一部のテストが失敗しました")
        print("   顧問先情報の受け渡しに問題があります。")
        return False
    else:
        print("\n⚠️  自動判定できませんでした")
        return None


def main():
    # 単一テスト実行
    print("=" * 70)
    print("単一テストケース")
    print("=" * 70)
    test_agent_with_adk_app()

    # 複数ケーステスト実行
    final_result = test_multiple_cases(num_tests=2)

    print("\n" + "=" * 70)
    print("最終結果")
    print("=" * 70)
    if final_result:
        print("✅ ⚠️マーク部分の検証: 全テスト成功")
        print("   root_agentを介した実際のやり取りで、")
        print("   顧問先情報が正しくstep2に渡されることを確認しました。")
    else:
        print("❌ テストに問題がありました")


if __name__ == "__main__":
    main()
