'use client';
import React from 'react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

function ViewHours() {
    const navigate = useRouter();
    const dir_home = () => {
        navigate.push('/');
        setName('');
        setPhone('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const softcheck = {
            name: name.toLowerCase(),
            phone: phone.toLowerCase(),
        }

        try {
        const response = await fetch('http://localhost:8000/viewhours', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(softcheck),
        });

        const result = await response.json();
        if (response.ok) {
            setMessage(result.detail);
        } 
        else {setMessage(`Error: ${result.detail}`);}
        }

        catch (err) {
            let errormsg = err.message;
            if (errormsg.length === 0) {
                setMessage("An unexpected error occurred");
            } else {
                setMessage(`Error: ${errormsg}`);
            }
        }
    };


    const [name, setName] = useState('');
    const [phone, setPhone] = useState('');
    const [message, setMessage] = useState('');

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
            <input className="btn" type="submit" value="Submit" />
            <button className="btn btn-secondary" type="button" onClick={dir_home}>Home</button>
        </div>
        {message && <p className="form-message">{message}</p>}

        </form>
        </div>
  );
}

export default ViewHours;

