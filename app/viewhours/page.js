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
            Phone Number ---  
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

export default ViewHours;

