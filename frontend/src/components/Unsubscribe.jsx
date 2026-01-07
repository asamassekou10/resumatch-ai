import React, { useEffect, useState } from 'react';

const Unsubscribe = () => {
  const [status, setStatus] = useState('pending'); // pending | success | error
  const [message, setMessage] = useState('');

  const unsubscribe = async () => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    if (!token) {
      setStatus('error');
      setMessage('Missing unsubscribe token');
      return;
    }

    try {
      const res = await fetch('/api/user/unsubscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      });
      const data = await res.json();
      if (res.ok) {
        setStatus('success');
        setMessage('You have been unsubscribed from all emails.');
      } else {
        setStatus('error');
        setMessage(data.error || 'Unsubscribe failed');
      }
    } catch (err) {
      setStatus('error');
      setMessage('Unsubscribe failed');
    }
  };

  useEffect(() => {
    unsubscribe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-2xl font-semibold mb-3">Email Preferences</h1>
      {status === 'pending' && <p>Processing your request...</p>}
      {status !== 'pending' && <p>{message}</p>}
    </div>
  );
};

export default Unsubscribe;
