'use client';

/*
    Where the frontend sends its requests. Kept in localStorage so a browser can be
    pointed at a remote deployment without rebuilding, and read at call time rather
    than at import time so a change takes effect on the very next request.
*/

export const DEFAULT_SERVER = 'http://localhost:8000';
const STORAGE_KEY = 'server';

const HOSTNAME = /^[a-z0-9.-]+$/i;
const IPV6 = /^\[[0-9a-f:]+\]$/i;

/*
    Returns a tidied absolute address, or '' if the input is not usable.
    URL() alone is far too forgiving here — it happily parses 'not a url!!'
    into a host — so the hostname is checked explicitly. Rebuilding from
    origin also drops any embedded credentials, query or fragment.
*/
export function normaliseServer(value) {
    // Trailing slashes are trimmed off the parsed pathname below, not here:
    // doing it up front turns a bare 'http://' into the hostname 'http'.
    const trimmed = (value || '').trim();
    if (!trimmed || /\s/.test(trimmed)) return '';

    const withScheme = /^[a-z][a-z0-9+.-]*:\/\//i.test(trimmed) ? trimmed : `http://${trimmed}`;

    let parsed;
    try {
        parsed = new URL(withScheme);
    } catch (err) {
        return '';
    }

    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') return '';
    if (!HOSTNAME.test(parsed.hostname) && !IPV6.test(parsed.hostname)) return '';

    const basePath = parsed.pathname.replace(/\/+$/, '');
    return `${parsed.origin}${basePath}`;
}

export function getServer() {
    if (typeof window === 'undefined') return DEFAULT_SERVER;
    return window.localStorage.getItem(STORAGE_KEY) || DEFAULT_SERVER;
}

export function setServer(value) {
    const normalised = normaliseServer(value);
    if (!normalised) return '';
    window.localStorage.setItem(STORAGE_KEY, normalised);
    return normalised;
}

export function resetServer() {
    if (typeof window !== 'undefined') window.localStorage.removeItem(STORAGE_KEY);
    return DEFAULT_SERVER;
}

export function apiUrl(path) {
    return `${getServer()}${path}`;
}
