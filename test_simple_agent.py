"""シンプルなroot_agentテスト"""

import random
from companies_12000_list import companies
from src.gov_doc_parser import root_agent

# ツール呼び出しを記録するグローバル変数
tool_calls = []

def after_tool_callback(tool, **kwargs):
    """ツール呼び出し後のコールバック"""
    # 引数を柔軟に取得
    args = kwargs.get('args', kwargs.get('tool_context', {}))
    result = kwargs.get('tool_response', kwargs.get('result'))

    tool_call_info = {
        "tool_name": tool.__name__ if hasattr(tool, '__name__') else str(tool),
        "args": dict(args) if args and not isinstance(args, dict) else (args or {}),
        "result": result
    }
    tool_calls.append(tool_call_info)
    print(f"\n【ツール呼び出し検出】")
    print(f"  ツール名: {tool_call_info['tool_name']}")
    print(f"  引数: {tool_call_info['args']}")
    return result

def test_agent_simple():
    """シンプルなエージェントテスト"""
    global tool_calls
    tool_calls = []

    print("=" * 70)
    print("root_agent シンプルテスト")
    print("=" * 70)

    # ランダムに顧問先を選択
    random_client = random.choice(companies)

    print(f"\n【初期設定】")
    print(f"ユーザーが入力する顧問先名（顧問先X）: 「{random_client}」")

    # エージェントのコールバックを設定
    from google.adk.agents import Agent

    agent_with_callback = Agent(
        name=root_agent.name,
        model=root_agent.model,
        description=root_agent.description,
        instruction=root_agent.instruction,
        tools=root_agent.tools,
        after_tool_callback=after_tool_callback
    )

    # メッセージを作成
    user_message = f"顧問先「{random_client}」の労働保険申告を自動入力してください"
    print(f"\n【ユーザー入力】")
    print(f"メッセージ: {user_message}")

    print(f"\n【エージェント実行開始】")

    try:
        # Agentのgenerate_contentを直接使用
        response = agent_with_callback.generate_content(user_message)

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
            return None

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    for i in range(3):
        print(f"\n\n{'=' * 70}")
        print(f"テストケース {i + 1}/3")
        print(f"{'=' * 70}")
        result = test_agent_simple()
        if result:
            print(f"\n✅ テストケース {i + 1}: 成功")
        elif result is False:
            print(f"\n❌ テストケース {i + 1}: 失敗")
        else:
            print(f"\n⚠️  テストケース {i + 1}: 判定不可")

if __name__ == "__main__":
    main()
