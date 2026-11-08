'use client';
import React from 'react';
import { useRouter } from 'next/navigation';

function homepage() {
    const navigate = useRouter();
    const dir_addvol = () => {
        navigate.push('/addvolunteer')
    };
    const dir_addhrs = () => {
        navigate.push('/addhours')
    };
    const dir_softcheck = () => {
        navigate.push('/viewhours')
    };
    const dir_allrecords = () => {
        navigate.push('/compile')
    }

    const buttonStyle = {
        maxWidth: '90vw',
        fontSize: '1.5rem',
        padding: '1rem 2rem',
        width: '20rem',
        borderRadius: '0.75rem',
        border: '1px solid var(--border)',
        background: 'var(--accent)',
        color: 'var(--accent-foreground)',
        cursor: 'pointer',
    };

    return (
        <div
            className="home-stack"
            style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '1.5rem',
                minHeight: '100vh',
                paddingBottom: '3rem',
            }}
        >
            <button className="home-btn" style={buttonStyle} onClick={dir_addvol}>Add Volunteer</button>
            <button className="home-btn" style={buttonStyle} onClick={dir_addhrs}>Add Hours</button>
            <button className="home-btn" style={buttonStyle} onClick={dir_softcheck}>View Hours</button>
            <button className="home-btn" style={buttonStyle} onClick={dir_allrecords}>Compile All Shifts</button>
        </div>
    )
}

export default homepage;