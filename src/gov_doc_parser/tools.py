"""顧問先情報取得・処理ツール"""

from typing import Any
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from companies_12000_list import companies


def step1_get_client_info(client_name: str) -> dict[str, Any]:
    """
    【ステップ1】顧問先情報取得ツール

    ⚠️ 重要: このツールは必ずstep2_process_client_dataの前に実行してください

    顧問先事業所リストから指定された名前に完全一致する顧問先を検索します。
    完全一致検索を行い、該当する顧問先を全て返します。

    Args:
        client_name: 検索する顧問先名（完全一致）

    Returns:
        dict: 検索結果
            - success: 検索の成功/失敗
            - matches: 一致した顧問先のリスト
            - count: 一致件数
            - query: 検索クエリ
    """
    # 完全一致検索
    matches = [company for company in companies if client_name == company]

    result = {
        "success": len(matches) > 0,
        "matches": matches,
        "count": len(matches),
        "query": client_name,
    }

    return result


def step2_process_client_data(
    client_name: str
) -> dict[str, Any]:
    """
    【ステップ2】顧問先情報をもとに処理をするツール

    ⚠️ 重要: このツールはstep1_get_client_infoの実行後にのみ使用してください
    ⚠️ 必ずstep1で取得した正確な顧問先名を使用してください

    指定された顧問先に対して自動入力処理を実行します。
    実際の処理の前に、顧問先が正しいことを検証します。

    Args:
        client_name: 処理対象の顧問先名（完全一致が必須）

    Returns:
        dict: 処理結果
            - success: 処理の成功/失敗
            - client_name: 処理対象の顧問先名
            - verified: 顧問先の検証結果
            - message: 処理結果のメッセージ
            - details: 処理の詳細情報
    """
    # 顧問先の存在確認と検証（完全一致）
    exact_match = client_name in companies

    if not exact_match:
        return {
            "success": False,
            "client_name": client_name,
            "verified": False,
            "message": f"顧問先「{client_name}」が見つかりません。完全一致する顧問先名を指定してください",
            "details": {
                "error": "client_not_found",
                "note": "完全一致検索を使用しています"
            }
        }

    # 完全一致した場合
    verified_client = client_name

    # 自動入力処理の実行（シミュレーション）
    details = {
        "verified_client": verified_client,
        "timestamp": "2025-10-31T16:00:00+09:00",
    }

    return {
        "success": True,
        "client_name": client_name,
        "verified": True,
        "message": f"顧問先「{verified_client}」への自動入力処理が完了しました",
        "details": details
    }
