import React, { useState } from 'react';
import { isFeatureEnabled, getAIMiddlewareURL } from '../flags';

export const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<{ role: string, text: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isFeatureEnabled('AI_CHAT_WIDGET')) return null;

  const handleSend = async () => {
    if (!input.trim()) return;
    const newMessages = [...messages, { role: 'user', text: input }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const aiUrl = getAIMiddlewareURL();
      const res = await fetch(`${aiUrl}/api/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });
      const data = await res.json();
      setMessages([...newMessages, { role: 'ai', text: data.reply }]);
    } catch (e) {
      console.error('Chat API error:', e);
      setMessages([...newMessages, { role: 'ai', text: "Error de conexión con el modelo Grok." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        style={{
          position: 'fixed', bottom: '24px', right: '24px',
          background: 'var(--mb-color-brand, #0F766E)', color: 'white',
          width: '56px', height: '56px', borderRadius: '50%',
          border: 'none', cursor: 'pointer', fontSize: '24px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)', zIndex: 9999
        }}
        onClick={() => setIsOpen(!isOpen)}
      >
        🤖
      </button>

      {isOpen && (
        <div style={{
          position: 'fixed', bottom: '90px', right: '24px',
          width: '350px', height: '500px', background: 'white',
          borderRadius: '12px', boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
          display: 'flex', flexDirection: 'column', zIndex: 9999,
          overflow: 'hidden'
        }}>
          <div style={{ background: 'var(--mb-color-brand, #0F766E)', color: 'white', padding: '16px', fontWeight: 'bold' }}>
            Data Assistant (Grok)
          </div>
          <div style={{ flex: 1, padding: '16px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {messages.length === 0 && <span style={{ color: '#888', textAlign: 'center', marginTop: 'auto', marginBottom: 'auto' }}>Pregúntame sobre tus datos...</span>}
            {messages.map((m, i) => (
              <div key={i} style={{
                alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                background: m.role === 'user' ? 'var(--mb-color-brand, #0F766E)' : '#F1F5F9',
                color: m.role === 'user' ? 'white' : 'black',
                padding: '8px 12px', borderRadius: '16px', maxWidth: '80%'
              }}>
                {m.text}
              </div>
            ))}
            {loading && <div style={{ alignSelf: 'flex-start', background: '#F1F5F9', padding: '8px 12px', borderRadius: '16px' }}>...</div>}
          </div>
          <div style={{ padding: '12px', borderTop: '1px solid #eee', display: 'flex', gap: '8px' }}>
            <input
              value={input} onChange={e => setInput(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && handleSend()}
              placeholder="Escribe un mensaje..."
              style={{ flex: 1, padding: '8px 12px', borderRadius: '20px', border: '1px solid #ccc', outline: 'none' }}
            />
            <button onClick={handleSend} style={{ background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '20px' }}>🚀</button>
          </div>
        </div>
      )}
    </>
  );
};
