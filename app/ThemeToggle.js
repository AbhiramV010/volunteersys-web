'use client';
import { useEffect, useState } from 'react';

export default function ThemeToggle() {
    const [theme, setTheme] = useState('light');

    useEffect(() => {
        const stored = window.localStorage.getItem('theme');
        const initial = stored || 'light';
        setTheme(initial);
        document.documentElement.setAttribute('data-theme', initial);
    }, []);

    const handleChange = (e) => {
        const next = e.target.value;
        setTheme(next);
        document.documentElement.setAttribute('data-theme', next);
        window.localStorage.setItem('theme', next);
    };

    return (
        <select className="theme-select" value={theme} onChange={handleChange} aria-label="Theme selector">
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="temple">Temple</option>
        </select>
    );
}
