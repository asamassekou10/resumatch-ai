import React, { useEffect, useState } from 'react';

/**
 * Email preferences settings
 * Allows users to toggle marketing/weekly/trial update emails and unsubscribe
 */
const Settings = () => {
  const [prefs, setPrefs] = useState({ marketing: true, weekly: true, trial_updates: true });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const token = localStorage.getItem('token');

  const authHeaders = token
    ? {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      }
    : { 'Content-Type': 'application/json' };

  const fetchPreferences = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/user/email-preferences', { headers: authHeaders });
      const data = await res.json();
      if (res.ok && data.email_preferences) {
        setPrefs(data.email_preferences);
      } else {
        setMessage(data.error || 'Failed to load preferences');
      }
    } catch (err) {
      setMessage('Failed to load preferences');
    } finally {
      setLoading(false);
    }
  };

  const savePreferences = async () => {
    setSaving(true);
    setMessage('');
    try {
      const res = await fetch('/api/user/email-preferences', {
        method: 'PUT',
        headers: authHeaders,
        body: JSON.stringify(prefs),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage('Preferences saved');
      } else {
        setMessage(data.error || 'Save failed');
      }
    } catch (err) {
      setMessage('Save failed');
    } finally {
      setSaving(false);
    }
  };

  const unsubscribeAll = async () => {
    setSaving(true);
    setMessage('');
    try {
      const res = await fetch('/api/user/unsubscribe', {
        method: 'POST',
        headers: authHeaders,
        body: JSON.stringify({}),
      });
      const data = await res.json();
      if (res.ok) {
        setPrefs({ marketing: false, weekly: false, trial_updates: false });
        setMessage('Unsubscribed from all emails');
      } else {
        setMessage(data.error || 'Unsubscribe failed');
      }
    } catch (err) {
      setMessage('Unsubscribe failed');
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    fetchPreferences();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) {
    return <div>Loading preferences...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h2 className="text-xl font-semibold mb-4">Email Preferences</h2>
      <div className="space-y-4">
        {['marketing', 'weekly', 'trial_updates'].map((key) => (
          <label key={key} className="flex items-center justify-between p-3 border rounded">
            <div>
              <p className="font-medium capitalize">{key.replace('_', ' ')}</p>
            </div>
            <input
              type="checkbox"
              checked={!!prefs[key]}
              onChange={(e) => setPrefs({ ...prefs, [key]: e.target.checked })}
              className="h-5 w-5"
            />
          </label>
        ))}
      </div>

      <div className="flex gap-3 mt-6">
        <button
          onClick={savePreferences}
          disabled={saving}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-60"
        >
          {saving ? 'Saving...' : 'Save'}
        </button>
        <button
          onClick={unsubscribeAll}
          disabled={saving}
          className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 disabled:opacity-60"
        >
          Unsubscribe All
        </button>
      </div>

      {message && <p className="mt-4 text-sm text-gray-700">{message}</p>}
    </div>
  );
};

export default Settings;
