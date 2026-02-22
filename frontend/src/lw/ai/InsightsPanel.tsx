import React, { useEffect, useState } from 'react';
import { isFeatureEnabled } from '../flags';

export const InsightsPanel = ({ dashboardId, chartData }: { dashboardId: number, chartData: any }) => {
  const [insight, setInsight] = useState<string | null>(null);

  useEffect(() => {
    if (!isFeatureEnabled('AI_INSIGHTS')) return;
    if (!chartData) return;

    fetch('/api/ai/insights', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ dashboard_id: dashboardId, data_json: JSON.stringify(chartData).substring(0, 1000) })
    })
    .then(r => r.json())
    .then(data => setInsight(data.text))
    .catch(console.error);

  }, [dashboardId, chartData]);

  if (!insight) return null;

  return (
    <div style={{ marginTop: '12px', padding: '12px', background: '#F8FAFC', borderLeft: '4px solid var(--mb-color-brand, #0F766E)', borderRadius: '4px', fontSize: '13px', color: '#334155' }}>
      <strong>💡 AI Insight:</strong> {insight}
    </div>
  );
};
