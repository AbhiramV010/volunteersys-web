'use client';
import React from 'react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiUrl, apiHeaders } from '../serverConfig';

function CompileShifts() {
    const navigate = useRouter();
    const dir_home = () => {
        navigate.push('/');
        setName('');
        setPhone('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setBusy(true);
        setFallback('');
        setMessage('Building the shift record...');

        const softcheck = {
            name: name.toLowerCase(),
            phone: phone.toLowerCase(),
        }

        // Opened up front, while the click is still the active user gesture. A tab
        // opened after the await below counts as a popup and gets blocked.
        const tab = window.open('', '_blank');

        try {
            const response = await fetch(apiUrl('/compile'), {
                method: 'POST',
                headers: apiHeaders(),
                body: JSON.stringify(softcheck),
            });

            if (!response.ok) {
                if (tab) tab.close();
                const result = await response.json();
                setMessage(`Error: ${result.detail}`);
                return;
            }

            const record = await response.blob();
            const url = window.URL.createObjectURL(record);

            if (tab) {
                tab.location.href = url;
                setMessage('Shift record opened in a new tab');
                // The new tab is still reading from this URL, so it can only be
                // released once the viewer has had time to load it.
                window.setTimeout(() => window.URL.revokeObjectURL(url), 60000);
            } else {
                // Popup blocked. Offer a link instead, which opens on a fresh click.
                setFallback(url);
                setMessage('Your browser blocked the new tab.');
            }
        }

        catch (err) {
            if (tab) tab.close();
            let errormsg = err.message;
            if (errormsg.length === 0) {
                setMessage("An unexpected error occurred");
            } else {
                setMessage(`Error: ${errormsg}`);
            }
        }

        finally {
            setBusy(false);
        }
    };


    const [name, setName] = useState('');
    const [phone, setPhone] = useState('');
    const [message, setMessage] = useState('');
    const [busy, setBusy] = useState(false);
    const [fallback, setFallback] = useState('');

    return (
        <div className="page-container">
        <form className="form-card" onSubmit={handleSubmit}>
        <label className="form-field">
            Volunteer name
            <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            />
        </label>

        <label className="form-field">
            Phone Number
            <input
            onChange={(e) => setPhone(e.target.value)}
            type="text"
            value={phone}
            required
            />
        </label>

        <div className="form-actions">
            <input className="btn" type="submit" value={busy ? 'Compiling...' : 'Open PDF'} disabled={busy} />
            <button className="btn btn-secondary" type="button" onClick={dir_home}>Home</button>
        </div>
        {message && <p className="form-message">{message}</p>}
        {fallback && (
            <p className="form-message">
                <a href={fallback} target="_blank" rel="noreferrer">Open the shift record</a>
            </p>
        )}

        </form>
        </div>
  );
}

export default CompileShifts;
