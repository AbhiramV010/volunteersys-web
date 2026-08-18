'use client';
import React from 'react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiUrl } from '../serverConfig';

function CompileShifts() {
    const navigate = useRouter();
    const dir_home = () => {
        navigate.push('/');
        setName('');
        setPhone('');
    };

    const filenameFrom = (header, fallback) => {
        const match = header && header.match(/filename="?([^";]+)"?/);
        return match ? match[1] : fallback;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setBusy(true);
        setMessage('Building the shift record...');

        const softcheck = {
            name: name.toLowerCase(),
            phone: phone.toLowerCase(),
        }

        try {
            const response = await fetch(apiUrl('/compile'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(softcheck),
            });

            if (!response.ok) {
                const result = await response.json();
                setMessage(`Error: ${result.detail}`);
                return;
            }

            const record = await response.blob();
            const url = window.URL.createObjectURL(record);
            const link = document.createElement('a');
            link.href = url;
            link.download = filenameFrom(response.headers.get('Content-Disposition'), 'shifts.pdf');
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);

            setMessage('Shift record downloaded as a PDF');
        }

        catch (err) {
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
            <input className="btn" type="submit" value={busy ? 'Compiling...' : 'Download PDF'} disabled={busy} />
            <button className="btn btn-secondary" type="button" onClick={dir_home}>Home</button>
        </div>
        {message && <p className="form-message">{message}</p>}

        </form>
        </div>
  );
}

export default CompileShifts;
