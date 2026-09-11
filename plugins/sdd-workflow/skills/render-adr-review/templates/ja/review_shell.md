<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>ADRレビュー: {header_title}</title>
<style>
  body { font-family: -apple-system, "Hiragino Kaku Gothic ProN", "Segoe UI", sans-serif; margin: 2rem auto; max-width: 860px; color: #1f2328; line-height: 1.7; }
  header.review-header { border-bottom: 2px solid #1f2328; padding-bottom: 1rem; margin-bottom: 2rem; }
  header.review-header h1 { margin-bottom: 0.25rem; }
  header.review-header .header-meta { color: #57606a; font-size: 0.9rem; }
  section.decision-card { border: 1px solid #d0d7de; border-radius: 8px; padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; }
  .decision-header { display: flex; align-items: baseline; gap: 0.75rem; margin-bottom: 0.25rem; }
  .decision-badge { background: #0969da; color: #fff; font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 999px; }
  .decision-title { margin: 0; font-size: 1.15rem; }
  .decision-meta { color: #57606a; font-size: 0.85rem; margin: 0 0 0.75rem; }
  .decision-rationale { margin: 0.25rem 0 1rem; }
  .decision-supersession { font-size: 0.85rem; margin: 0 0 0.75rem; padding: 0.4rem 0.65rem; border-left: 3px solid #9a6700; background: #fff8c5; }
  .decision-supersession a { color: #7d4e00; }
  section.decision-card.superseded { border-style: dashed; background: #f6f8fa; }
  section.decision-card.superseded .decision-title { color: #57606a; }
  section.decision-card.superseded .decision-badge { background: #6e7781; }
  section.decision-card.superseded .decision-supersession { border-left-color: #6e7781; background: #eaeef2; }
  table.alternatives-comparison { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  table.alternatives-comparison th, table.alternatives-comparison td { border: 1px solid #d0d7de; padding: 0.5rem 0.75rem; text-align: left; vertical-align: top; }
  table.alternatives-comparison th { background: #f6f8fa; }
  tr.verdict-adopted { background: #e6f4ea; }
  tr.verdict-rejected { background: #fdf2f1; color: #57606a; }
  tr.verdict-rejected .option-name { text-decoration: line-through; }
  .verdict-pill { font-size: 0.75rem; padding: 0.1rem 0.5rem; border-radius: 999px; font-weight: 600; }
  .verdict-adopted .verdict-pill { background: #1a7f37; color: #fff; }
  .verdict-rejected .verdict-pill { background: #cf222e; color: #fff; }
  footer.scratch-notice { margin-top: 2rem; padding-top: 1rem; border-top: 1px dashed #d0d7de; color: #57606a; font-size: 0.85rem; }
</style>
</head>
<body>
<header class="review-header">
  <h1>ADRレビュー: {header_title}</h1>
  <p class="header-meta">{header_meta}</p>
</header>
<main>
{decision_cards}
</main>
<footer class="scratch-notice">
  これは <code>render-adr-review</code> スキルが生成した一時的なレビュー資料です。
  AI-SDDの永続ドキュメントには含まれず、リポジトリにコミットしてはいけません。
</footer>
</body>
</html>
