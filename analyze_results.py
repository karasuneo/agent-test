"""test_results.csvからstep2_called=Trueの行を分析"""

import csv
import random
from pathlib import Path

CSV_FILE = Path(__file__).parent / "test_results.csv"
OUTPUT_CSV_FILE = Path(__file__).parent / "sampled_results.csv"


def analyze_step2_called_cases(sample_size: int = 5000):
    """
    step2_called=Trueの行から無作為にサンプルを抽出し、
    expected_client_name、step1_client_name、step2_client_nameが
    全て一致したものを数える

    Args:
        sample_size: 抽出するサンプル数（デフォルト5000）
    """
    print("=" * 70)
    print(f"test_results.csv 分析（サンプルサイズ: {sample_size}）")
    print("=" * 70)

    # CSVファイルを読み込み
    step2_true_rows = []

    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # step2_called=Trueの行のみ抽出
            if row.get('step2_called', '').lower() == 'true':
                step2_true_rows.append(row)

    print(f"\nstep2_called=Trueの総行数: {len(step2_true_rows)}")

    if len(step2_true_rows) == 0:
        print("step2_called=Trueの行が見つかりませんでした")
        return

    # サンプルサイズを調整（データが少ない場合）
    actual_sample_size = min(sample_size, len(step2_true_rows))
    print(f"実際のサンプルサイズ: {actual_sample_size}")

    # 無作為に抽出
    sampled_rows = random.sample(step2_true_rows, actual_sample_size)

    # 抽出したデータをCSVに保存（test_case_idを1から連番で上書き）
    if sampled_rows:
        # test_case_idを1から順番に振り直す
        for idx, row in enumerate(sampled_rows, start=1):
            row['test_case_id'] = idx

        with open(OUTPUT_CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
            # 元のCSVと同じヘッダーを使用
            fieldnames = sampled_rows[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sampled_rows)
        print(f"\n抽出したデータを保存: {OUTPUT_CSV_FILE}")

    # 一致を確認
    match_count = 0
    mismatch_cases = []

    for row in sampled_rows:
        expected = row.get('expected_client_name', '')
        step1 = row.get('step1_client_name', '')
        step2 = row.get('step2_client_name', '')

        if expected == step1 == step2:
            match_count += 1
        else:
            mismatch_cases.append({
                'test_case_id': row.get('test_case_id', ''),
                'expected': expected,
                'step1': step1,
                'step2': step2
            })

    # 結果表示
    print("\n" + "=" * 70)
    print("分析結果")
    print("=" * 70)
    print(f"サンプル数: {actual_sample_size}")
    print(f"3つの値が全て一致: {match_count} 件")
    print(f"不一致: {len(mismatch_cases)} 件")
    print(f"一致率: {match_count / actual_sample_size * 100:.2f}%")

    # 不一致ケースの詳細表示
    if mismatch_cases:
        print(f"\n不一致ケース（最初の10件）:")
        for i, case in enumerate(mismatch_cases[:10], 1):
            print(f"\n{i}. テストケースID: {case['test_case_id']}")
            print(f"   expected_client_name: 「{case['expected']}」")
            print(f"   step1_client_name:    「{case['step1']}」")
            print(f"   step2_client_name:    「{case['step2']}」")


if __name__ == "__main__":
    analyze_step2_called_cases()
