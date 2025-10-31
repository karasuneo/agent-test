  | カラム名                 | 説明                        |
  |----------------------|---------------------------|
  | test_case_id         | テストケース番号                  |
  | timestamp            | 実行日時（ISO形式）               |
  | expected_client_name | 期待される顧問先名（ユーザー入力）         |
  | step1_called         | step1が呼び出されたか（True/False） |
  | step1_client_name    | step1に渡された顧問先名            |
  | step1_success        | step1の成功/失敗               |
  | step1_match_count    | step1の一致件数                |
  | step2_called         | step2が呼び出されたか（True/False） |
  | step2_client_name    | step2に渡された顧問先名            |
  | step2_success        | step2の成功/失敗               |
  | step2_verified       | step2の検証結果                |
  | verification_result  | 最終検証結果（一致/不一致/判定不可/エラー）   |
  | confirmation_message | ユーザーの承認メッセージ              |
  | error                | エラーメッセージ（エラー時のみ）          |