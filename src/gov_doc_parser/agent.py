"""Agent definition for gov_doc_parser"""

from google.adk.agents import Agent
from .tools import get_client_info, process_client_data

root_agent = Agent(
    name="gov_doc_parser",
    model="gemini-2.5-pro",
    description="顧問先名が記載された政府文書を解析し、顧問先名を抽出します。また、顧問先情報の取得と処理を行います。",
    instruction="""
あなたは社労士の業務をサポートするAIエージェントです。

主な役割:
1. 顧問先名を確認し、正確な情報を取得する
2. 取得した顧問先情報をもとに自動入力などの処理を実行する

重要な注意事項:
- 顧問先名を処理する前に、必ずget_client_infoツールで顧問先を確認してください
- 複数の候補がある場合は、ユーザーに正確な顧問先名を確認してください
- process_client_dataツールを実行する前に、ユーザーに最終確認を求めてください
- 処理結果は明確に報告してください
    """,
    tools=[
        get_client_info,
        process_client_data,
    ],
)
