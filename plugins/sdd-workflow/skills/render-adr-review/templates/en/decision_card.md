<section class="decision-card {decision_status_class}" id="{decision_anchor}">
  <div class="decision-header">
    <span class="decision-badge">{decision_badge_label}</span>
    <h2 class="decision-title">{decision_title}</h2>
  </div>
  <p class="decision-meta">{decision_date}</p>
{decision_supersession}
  <p class="decision-rationale"><strong>Rationale:</strong> {decision_rationale}</p>
  <table class="alternatives-comparison">
    <thead>
      <tr><th>Option</th><th>Summary</th><th>Reason</th><th>Verdict</th></tr>
    </thead>
    <tbody>
{alternative_rows}
    </tbody>
  </table>
</section>
