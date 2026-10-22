# spec: {{SPEC_ID}}
# model-of: {{MODEL_OF}}
#
# 承認済み LAWS.bend ({{LAWS_HASH}}) を満たすよう書いた参照モデル。
# 実装ではなく小さな純粋関数での書き直し。LAWS.bend の '# model-api:' 行に厳密に従う。
# '# model-of:' は spec の 'impl-of:' 宣言の写し（status.impl.paths。1 行 1 パス、ソースコードのみ）。

import Base

{{MODEL_FUNCTIONS}}
