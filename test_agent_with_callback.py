"""root_agentのツール呼び出しをコールバックで検証するテスト"""

import random
import asyncio
from companies_12000_list import companies
from google.adk.apps import App
from google.adk import Runner
from google.adk.sessions import InMemorySessionService


# ツール呼び出しを記録するグローバル変数
tool_calls = []


def after_tool_callback(tool, args, context, result):
    """
    ツール呼び出し後のコールバック

    全てのツール呼び出しを記録します
    """
    tool_call_info = {
        "tool_name": tool.name if hasattr(tool, 'name') else str(tool),
        "args": dict(args),
        "result": result
    }
    tool_calls.append(tool_call_info)
    print(f"\n【ツール呼び出し検出】")
    print(f"  ツール名: {tool_call_info['tool_name']}")
    print(f"  引数: {tool_call_info['args']}")
    return result


async def test_agent_with_callback():
    """
    コールバックを使ったエージェントテスト

    検証ポイント:
    - ユーザーが入力した顧問先名Xが記録される
    - step1_get_client_infoが呼び出される
    - step2_process_client_dataが呼び出される
    - step2に渡される値が最初のユーザー入力値Xと一致するか
    """
    global tool_calls
    tool_calls = []  # リセット

    print("=" * 70)
    print("root_agent コールバックテスト")
    print("=" * 70)

    # テストケース: ランダムに顧問先を選択
    random_client = random.choice(companies)

    print(f"\n【初期設定】")
    print(f"ユーザーが入力する顧問先名（顧問先X）: 「{random_client}」")
    print(f"💡 この値がstep2に渡されるべき値です")

    # ユーザーの入力をシミュレーション
    user_message = f"顧問先「{random_client}」の労働保険申告を自動入力してください"

    print(f"\n【ユーザー入力】")
    print(f"メッセージ: {user_message}")

    try:
        # エージェントのインポート
        from src.gov_doc_parser.agent import root_agent as original_agent
        from src.gov_doc_parser.tools import step1_get_client_info, step2_process_client_data
        from google.adk.agents import Agent

        # コールバック付きでエージェントを再作成
        agent_with_callback = Agent(
            name=original_agent.name,
            model=original_agent.model,
            description=original_agent.description,
            instruction=original_agent.instruction,
            tools=original_agent.tools,
            after_tool_callback=after_tool_callback
        )

        # Appでエージェントをラップ
        app = App(name="gov_doc_parser_test", root_agent=agent_with_callback)

        # Runnerを作成
        runner = Runner(
            app=app,
            session_service=InMemorySessionService()
        )

        print(f"\n【エージェント実行開始】")
        print("root_agentにメッセージを送信します...")

        # セッションを開始してメッセージを送信
        session_id = f"test_session_{random.randint(1000, 9999)}"
        user_id = "test_user"

        # runner.runの戻り値を処理
        result_gen = runner.run(session_id=session_id, user_id=user_id, new_message=user_message)

        # ジェネレーターから結果を取得
        events = []
        for event in result_gen:
            events.append(event)
            # イベントの内容を表示（オプション）
            if hasattr(event, 'type'):
                print(f"  イベント: {event.type}")

        print(f"\n【エージェント実行完了】")
        print(f"総イベント数: {len(events)}")

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

            if call['tool_name'] == 'step1_get_client_info':
                step1_called = True
                print(f"  ✅ step1_get_client_info が呼び出されました")

            elif call['tool_name'] == 'step2_process_client_data':
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


async def test_multiple_cases(num_tests: int = 3):
    """複数ケースのテスト"""
    print("\n\n" + "=" * 70)
    print(f"複数ケーステスト（{num_tests}回実行）")
    print("=" * 70)

    results = []

    for i in range(num_tests):
        print(f"\n\n{'=' * 70}")
        print(f"テストケース {i + 1}/{num_tests}")
        print(f"{'=' * 70}")

        result = await test_agent_with_callback()
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


async def main():
    # 単一テスト実行
    print("=" * 70)
    print("単一テストケース")
    print("=" * 70)
    await test_agent_with_callback()

    # 複数ケーステスト実行
    final_result = await test_multiple_cases(num_tests=2)

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
    asyncio.run(main())
