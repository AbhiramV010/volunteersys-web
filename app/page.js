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

    return (
        <div>
            <button onClick={dir_addvol}>Add Volunteer</button>
            <br />
            <br />
            <button onClick={dir_addhrs}>Add Hours</button>
            <br />
            <br />
            <button onClick={dir_softcheck}>View Hours</button>
            <br />
            <br />
            <button onClick={dir_allrecords}>Compile All Shifts</button>
        </div>
    )
}

export default homepage;