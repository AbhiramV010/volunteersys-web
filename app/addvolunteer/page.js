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

      <label className="form-field">
        Address
        <input
          onChange={(e) => setAddress(e.target.value)}
          type="text"
          value={address}
          required
        />
      </label>

      <label className="form-field">
        Admin
        <input
          onChange={(e) => setAdmin(e.target.value)}
          type="text"
          value={admin}
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

export default AddVolunteer;