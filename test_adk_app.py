"""vertexai.preview.reasoning_engines.AdkAppを使ったroot_agentテスト"""

import csv
import random
import uuid
import warnings
from datetime import datetime
from pathlib import Path
from companies_12000_list import companies
from src.gov_doc_parser import root_agent
from vertexai.preview import reasoning_engines

# 警告を非表示にする
warnings.filterwarnings("ignore")

# ツール呼び出しを記録するグローバル変数
tool_calls = []

# CSVファイルのパス
CSV_FILE = Path(__file__).parent / "test_results.csv"


def save_test_result_to_csv(
    test_case_id: int,
    expected_client_name: str,
    step1_called: bool,
    step1_client_name: str,
    step1_result: dict,
    step2_called: bool,
    step2_client_name: str,
    step2_result: dict,
    verification_result: str,
    confirmation_message: str = "",
    error: str = ""
):
    """
    テスト結果をCSVファイルに1行追記

    Args:
        test_case_id: テストケース番号
        expected_client_name: 期待される顧問先名（ユーザー入力）
        step1_called: step1が呼び出されたか
        step1_client_name: step1に渡された顧問先名
        step1_result: step1の結果辞書
        step2_called: step2が呼び出されたか
        step2_client_name: step2に渡された顧問先名
        step2_result: step2の結果辞書
        verification_result: 検証結果（一致/不一致/判定不可）
        confirmation_message: 承認メッセージ
        error: エラーメッセージ
    """
    # CSVヘッダー
    headers = [
        "test_case_id",
        "timestamp",
        "expected_client_name",
        "step1_called",
        "step1_client_name",
        "step1_success",
        "step1_match_count",
        "step2_called",
        "step2_client_name",
        "step2_success",
        "step2_verified",
        "verification_result",
        "confirmation_message",
        "error"
    ]

    # ファイルが存在しない場合はヘッダーを書き込む
    file_exists = CSV_FILE.exists()

    # データ行を作成
    row = {
        "test_case_id": test_case_id,
        "timestamp": datetime.now().isoformat(),
        "expected_client_name": expected_client_name,
        "step1_called": step1_called,
        "step1_client_name": step1_client_name,
        "step1_success": step1_result.get("success", False) if step1_result else False,
        "step1_match_count": step1_result.get("count", 0) if step1_result else 0,
        "step2_called": step2_called,
        "step2_client_name": step2_client_name,
        "step2_success": step2_result.get("success", False) if step2_result else False,
        "step2_verified": step2_result.get("verified", False) if step2_result else False,
        "verification_result": verification_result,
        "confirmation_message": confirmation_message,
        "error": error
    }

    # CSVファイルに追記
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)

        # ヘッダーを書き込む（ファイルが新規作成の場合のみ）
        if not file_exists:
            writer.writeheader()

        # データ行を書き込む
        writer.writerow(row)

    print(f"\n✅ テスト結果をCSVに記録しました: {CSV_FILE}")


def format_agent_response(response: dict) -> str:
    """
    エージェント応答から必須情報のみを抽出して整形

    必須情報:
    - author: エージェント名
    - text: テキスト応答
    - function_call: ツール呼び出し（name, args）
    - function_response: ツール応答結果
    """
    if not isinstance(response, dict):
        return str(response)

    lines = []

    # author（エージェント名）
    if 'author' in response:
        lines.append(f"エージェント: {response['author']}")

    # content.parts の解析
    content = response.get('content', {})
    parts = content.get('parts', [])

    for part in parts:
        # テキスト応答
        if 'text' in part:
            lines.append(f"応答: {part['text']}")

        # ツール呼び出し
        if 'function_call' in part:
            fc = part['function_call']
            lines.append(f"ツール呼び出し: {fc.get('name', 'unknown')}")
            lines.append(f"  引数: {fc.get('args', {})}")

        # ツール応答
        if 'function_response' in part:
            fr = part['function_response']
            lines.append(f"ツール応答: {fr.get('name', 'unknown')}")
            lines.append(f"  結果: {fr.get('response', {})}")

    return "\n".join(lines) if lines else str(response)


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
    print("\n【ツール呼び出し検出】")
    print(f"  ツール名: {tool_call_info['tool_name']}")
    print(f"  引数: {tool_call_info['args']}")
    print(f"  結果: {tool_call_info['result']}")
    return result


def test_agent_with_adk_app(test_case_id: int = 1):
    """
    AdkAppを使ったエージェントテスト

    検証ポイント:
    - ユーザーが入力した顧問先名Xが記録される
    - step1_get_client_infoが呼び出される
    - step2_process_client_dataが呼び出される
    - step2に渡される値が最初のユーザー入力値Xと一致するか

    Args:
        test_case_id: テストケース番号（CSV記録用）
    """
    global tool_calls
    tool_calls = []

    print("=" * 70)
    print("root_agent AdkAppテスト")
    print("=" * 70)

    # ランダムに顧問先を選択
    random_client = random.choice(companies)

    print("\n【初期設定】")
    print(f"ユーザーが入力する顧問先名（顧問先X）: 「{random_client}」")
    print("💡 この値がstep2に渡されるべき値です")

    # ユーザーの入力をシミュレーション
    user_message = f"顧問先「{random_client}」の労働保険申告を自動入力してください"

    print("\n【ユーザー入力】")
    print(f"メッセージ: {user_message}")

    # CSV記録用の変数を初期化
    confirmation_message = ""
    error_message = ""

    try:
        # エージェントのコールバックを設定（元のinstructionを使用）
        from google.adk.agents import Agent

        agent_with_callback = Agent(
            name=root_agent.name,
            model=root_agent.model,
            description=root_agent.description,
            instruction=root_agent.instruction,  # 元のinstructionを使用（確認フェーズ含む）
            tools=root_agent.tools,
            after_tool_callback=after_tool_callback
        )

        # AdkAppでエージェントをラップ（トレーシングを無効化して警告を抑制）
        app = reasoning_engines.AdkApp(
            agent=agent_with_callback,
            enable_tracing=False,
        )

        print("\n【エージェント実行開始】")
        print("root_agentにメッセージを送信します...")

        # セッションを作成（UUID形式）
        session_id = f"test_{uuid.uuid4()}"
        user_id = "test_user"
        app.create_session(session_id=session_id, user_id=user_id)

        # メッセージを送信
        response_stream = app.stream_query(session_id=session_id, user_id=user_id, message=user_message)

        # ストリーム結果を収集（辞書形式を保持）
        responses = []
        for chunk in response_stream:
            responses.append(chunk)

        print("\n【エージェント応答（1回目）】")
        for idx, response in enumerate(responses):
            print(f"\n--- 応答チャンク {idx + 1} ---")
            print(format_agent_response(response))

        # エージェントが確認を求めているかチェック（「よろしいですか」などの文言を含む）
        all_responses_text = " ".join([str(r) for r in responses])
        if "よろしいですか" in all_responses_text or "よろしいでしょうか" in all_responses_text:
            print("\n【確認フェーズ検出】")
            print("エージェントが確認を求めています。自動的に承認します...")

            # 承認メッセージのバリエーション（10種類）
            confirmation_messages = [
                "はい",
                "Yes",
                "お願い",
                "大丈夫",
                "ok",
                "うん",
                "はい、大丈夫です",
                "はい、進めてください",
                "問題ありません",
                "⭕️"
            ]
            confirmation_message = random.choice(confirmation_messages)  # CSV記録用に保存
            print(f"承認メッセージ: 「{confirmation_message}」")

            response_stream2 = app.stream_query(session_id=session_id, user_id=user_id, message=confirmation_message)

            # 2回目の応答を収集（辞書形式を保持）
            responses2 = []
            for chunk in response_stream2:
                responses2.append(chunk)

            print("\n【エージェント応答（2回目：確認後）】")
            for idx, response in enumerate(responses2):
                print(f"\n--- 応答チャンク {idx + 1} ---")
                print(format_agent_response(response))

        # ツール呼び出しの検証
        print("\n【ツール呼び出し履歴の検証】")
        print(f"総ツール呼び出し数: {len(tool_calls)}")

        step1_called = False
        step2_called = False
        step1_client_name = ""
        step2_client_name = ""
        step1_result = None
        step2_result = None

        for idx, call in enumerate(tool_calls):
            print(f"\nツール呼び出し {idx + 1}:")
            print(f"  ツール名: {call['tool_name']}")
            print(f"  引数: {call['args']}")

            if 'step1_get_client_info' in call['tool_name']:
                step1_called = True
                step1_client_name = call['args'].get('client_name', '')
                step1_result = call['result']
                print("  ✅ step1_get_client_info が呼び出されました")

            elif 'step2_process_client_data' in call['tool_name']:
                step2_called = True
                step2_client_name = call['args'].get('client_name', '')
                step2_result = call['result']
                print("  ✅ step2_process_client_data が呼び出されました")

        # 検証結果
        print("\n【検証結果】")
        print(f"step1呼び出し: {'✅' if step1_called else '❌'}")
        print(f"step2呼び出し: {'✅' if step2_called else '❌'}")

        # 検証結果を判定
        verification_result = "判定不可"
        test_result = None

        if step2_called and step2_client_name:
            print("\n⚠️ 【最重要検証ポイント】")
            print(f"  最初のユーザー入力: 「{random_client}」")
            print(f"  step2に渡された値: 「{step2_client_name}」")

            if step2_client_name == random_client:
                print("  ✅ 一致: 顧問先情報が正しく渡されています！")
                verification_result = "一致"
                test_result = True
            else:
                print("  ❌ 不一致: 顧問先情報が正しく渡されていません！")
                verification_result = "不一致"
                test_result = False
        else:
            print("\n⚠️ step2が呼び出されませんでした")
            print("エージェントが指示通りに動作しなかった可能性があります")
            verification_result = "判定不可"
            test_result = None

        # CSV記録
        save_test_result_to_csv(
            test_case_id=test_case_id,
            expected_client_name=random_client,
            step1_called=step1_called,
            step1_client_name=step1_client_name,
            step1_result=step1_result or {},
            step2_called=step2_called,
            step2_client_name=step2_client_name,
            step2_result=step2_result or {},
            verification_result=verification_result,
            confirmation_message=confirmation_message,
            error=""
        )

        return test_result

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"\n❌ エラーが発生しました: {error_msg}")
        import traceback
        traceback.print_exc()

        # エラー時もCSV記録
        save_test_result_to_csv(
            test_case_id=test_case_id,
            expected_client_name=random_client,
            step1_called=False,
            step1_client_name="",
            step1_result={},
            step2_called=False,
            step2_client_name="",
            step2_result={},
            verification_result="エラー",
            confirmation_message=confirmation_message,
            error=error_msg
        )

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

        result = test_agent_with_adk_app(test_case_id=i + 1)
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
