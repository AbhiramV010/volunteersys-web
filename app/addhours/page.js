'use client';
import React from 'react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

function AddHours() {
    const navigate = useRouter();
    const dir_home = () => {
        navigate.push('/');
        setName('');
        setPhone('');
        setAdmin('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const shiftdata = {
            dte: new Date().toISOString().slice(0, 10),
            name: name.toLowerCase(),
            start: start.toLowerCase(),
            end: end.toLowerCase(),
            admin: admin.toLowerCase(),
            phone: phone.toLowerCase(),
        }

        try {
        const response = await fetch('http://localhost:8000/addhours', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(shiftdata),
        });

        const result = await response.json();
        if (response.ok) {
            setMessage('Shift logged successfully');
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
    const [start, setStart] = useState('');
    const [end, setEnd] = useState('');
    const [admin, setAdmin] = useState('');
    const [phone, setPhone] = useState('');
    const [message, setMessage] = useState('');


    return (
        <form onSubmit={handleSubmit}>
        <label>
            Volunteer name ---  
            <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            />
        </label>
        <br />
        <br />
        <br />

        <label>
            Start Time in 24 hr format ---  
            <input
            onChange={(e) => setStart(e.target.value)}
            type="text"
            value={start}
            required
            />
        </label>
        <br />
        <br />
        <br />

        <label>
            End Time in 24 hr format ---  
            <input
            onChange={(e) => setEnd(e.target.value)}
            type="text"
            value={end}
            required
            />
        </label>
        <br />
        <br />
        <br />

        <label>
            Phone ---  
            <input
            onChange={(e) => setPhone(e.target.value)}
            type="text"
            value={phone}
            required
            />
        </label>
        <br />
        <br />
        <br />

        <label>
            Admin ---
            <input
            onChange={(e) => setAdmin(e.target.value)}
            type="text"
            value={admin}
            required
            />
        </label>
        <br />
        <br />
        <br />

        <input type="submit" />
        <br />
        <br />
        <button onClick={dir_home}>Home</button>
        <br/>
        <br/>
        <br/>
        {message && <p>{message}</p>}

        </form>
  );

    
}

export default AddHours;

