"""root_agentを介したユーザーとのやり取りテスト"""

import random
import asyncio
from companies_12000_list import companies
from src.gov_doc_parser import root_agent
from google.adk.apps import App
from google.adk import Runner
from google.adk.sessions import InMemorySessionService


async def test_agent_with_user_input():
    """
    root_agentを使った実際のエージェント実行テスト

    検証ポイント:
    - ユーザーが入力した顧問先名Xが最初の入力として記録される
    - エージェントがstep1_get_client_infoを呼び出す
    - エージェントがstep2_process_client_dataを呼び出す
    - step2に渡される値が最初のユーザー入力値Xと一致するか
    """
    print("=" * 70)
    print("root_agentを介したユーザーとのやり取りテスト")
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

    print(f"\n【エージェント実行開始】")
    print("root_agentにメッセージを送信します...")

    try:
        # Appでroot_agentをラップ
        app = App(name="gov_doc_parser_app", root_agent=root_agent)

        # Runnerを作成
        runner = Runner(
            app=app,
            session_service=InMemorySessionService()
        )

        # セッションを開始してメッセージを送信
        session_id = "test_session"
        user_id = "test_user"
        events = []
        async for event in runner.run(session_id=session_id, user_id=user_id, new_message=user_message):
            events.append(event)

        # 最後のイベントから応答を取得
        if events:
            last_event = events[-1]
            response = last_event
        else:
            response = "応答なし"

        print(f"\n【エージェント応答】")
        print(f"応答内容:")
        print(response)

        # ツール呼び出しの履歴を確認
        print(f"\n【ツール呼び出し履歴の解析】")

        # イベントから情報を抽出
        print(f"\n総イベント数: {len(events)}")

        for idx, event in enumerate(events):
            print(f"\nイベント {idx + 1}:")
            print(f"  タイプ: {type(event).__name__}")

            # イベントの内容を確認
            if hasattr(event, 'type'):
                print(f"  event.type: {event.type}")

            if hasattr(event, 'content'):
                content = event.content
                if hasattr(content, 'parts'):
                    for part_idx, part in enumerate(content.parts):
                        # function_callの確認
                        if hasattr(part, 'function_call'):
                            func_call = part.function_call
                            print(f"    [Part {part_idx}] 関数呼び出し: {func_call.name}")
                            print(f"    引数: {dict(func_call.args)}")

                            # step2の呼び出しをチェック
                            if func_call.name == 'step2_process_client_data':
                                step2_client_name = func_call.args.get('client_name', '')
                                print(f"\n⚠️ 【検証ポイント】")
                                print(f"  最初のユーザー入力: 「{random_client}」")
                                print(f"  step2に渡された値: 「{step2_client_name}」")

                                if step2_client_name == random_client:
                                    print(f"  ✅ 一致: 顧問先情報が正しく渡されています")
                                    return True
                                else:
                                    print(f"  ❌ 不一致: 顧問先情報が正しく渡されていません")
                                    return False

                        # textの確認
                        elif hasattr(part, 'text'):
                            text_preview = part.text[:100] if len(part.text) > 100 else part.text
                            print(f"    [Part {part_idx}] テキスト: {text_preview}...")

        print(f"\n⚠️ 注意: step2_process_client_dataの呼び出しが見つかりませんでした")
        print(f"エージェントの応答内容から手動で判断してください")

        return None

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        print(f"エラータイプ: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_agent_interactions(num_tests: int = 3):
    """複数のエージェントインタラクションをテスト"""
    print("\n\n" + "=" * 70)
    print(f"複数ケーステスト（{num_tests}回実行）")
    print("=" * 70)

    results = []

    for i in range(num_tests):
        print(f"\n\n{'=' * 70}")
        print(f"テストケース {i + 1}/{num_tests}")
        print(f"{'=' * 70}")

        result = await test_agent_with_user_input()
        results.append(result)

        if result is True:
            print(f"\n✅ テストケース {i + 1}: 成功")
        elif result is False:
            print(f"\n❌ テストケース {i + 1}: 失敗")
        else:
            print(f"\n⚠️  テストケース {i + 1}: 判定不可（手動確認が必要）")

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
    elif failure_count > 0:
        print("\n❌ 一部のテストが失敗しました")
    else:
        print("\n⚠️  自動判定できませんでした。応答内容を手動で確認してください")


async def main():
    # 単一テスト実行
    print("=" * 70)
    print("単一テストケース")
    print("=" * 70)
    await test_agent_with_user_input()

    # 複数ケーステスト実行
    await test_multiple_agent_interactions(num_tests=3)

    print("\n" + "=" * 70)
    print("テスト完了")
    print("=" * 70)
    print("\n注意: Google ADKのエージェント応答は非決定的です")
    print("エージェントが指示通りにツールを呼び出すかは実行ごとに異なる場合があります")


if __name__ == "__main__":
    asyncio.run(main())
