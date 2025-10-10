'use client';
import React from 'react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

function AddVolunteer() {
    const navigate = useRouter();
    const dir_home = () => {
        navigate.push('/');
        setName('');
        setPhone('');
        setAddress('');
        setAdmin('');
    };
    const handleSubmit = async (e) => {
      e.preventDefault();

    const volunteerdata = {
      fullname: name.toLowerCase(),
      phone: phone.toLowerCase(),
      address: address.toLowerCase(),
      admin: admin.toLowerCase(),
      date: new Date().toISOString().slice(0, 10),
    };

    try {
      const response = await fetch('http://localhost:8000/addvolunteer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(volunteerdata),
      });

      const result = await response.json();
      if (response.ok) {
        setMessage('Volunteer added successfully');
      } else {
        setMessage(`Error: ${result.detail}`);
      }
    } catch (err) {
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
  const [address, setAddress] = useState('');
  const [admin, setAdmin] = useState('');
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

      <label>
        Address ---
        <input
          onChange={(e) => setAddress(e.target.value)}
          type="text"
          value={address}
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

export default AddVolunteer;