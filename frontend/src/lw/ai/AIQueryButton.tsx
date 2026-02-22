import React, { useState } from 'react';
import { isFeatureEnabled } from '../flags';

export const AIQueryButton = ({ onQueryGenerated }: { onQueryGenerated: (sql: string) => void }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isFeatureEnabled('AI_SQL_GENERATION')) return null;

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/ai/generate-sql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ natural_language: prompt })
      });
      const data = await res.json();
      onQueryGenerated(data.sql);
      setIsOpen(false);
    } catch (e) {
      console.error(e);
      alert('Error generando SQL desde AI.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'inline-block', marginLeft: '1rem' }}>
      <button
        style={{ background: 'var(--mb-color-brand, #0F766E)', color: 'white', padding: '6px 12px', borderRadius: '4px', border: 'none', cursor: 'pointer', fontWeight: 'bold' }}
        onClick={() => setIsOpen(!isOpen)}
      >
        ✨ Ask AI
      </button>

      {isOpen && (
        <div style={{ position: 'absolute', zIndex: 1000, background: 'white', padding: '16px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', marginTop: '8px', width: '300px' }}>
          <h4 style={{ marginTop: 0 }}>Generar SQL con IA</h4>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ej: Muéstrame ventas del último trimestre por región"
            style={{ width: '100%', height: '80px', marginBottom: '8px', padding: '4px' }}
          />
          <button
            disabled={loading}
            onClick={handleGenerate}
            style={{ background: 'var(--mb-color-brand, #0F766E)', color: 'white', border: 'none', padding: '6px 16px', borderRadius: '4px', cursor: 'pointer', width: '100%' }}
          >
            {loading ? "Pensando..." : "Generar Query"}
          </button>
        </div>
      )}
    </div>
  );
};
