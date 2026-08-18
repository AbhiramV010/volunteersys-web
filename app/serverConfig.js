'use client';

/*
    Where the frontend sends its requests. Kept in localStorage so a browser can be
    pointed at a remote deployment without rebuilding, and read at call time rather
    than at import time so a change takes effect on the very next request.
*/

/*
    Baked in at build time. A deployed site has no localhost to talk to, so set
    NEXT_PUBLIC_API_URL in the host's build environment to point at the hosted
    backend. The menu can still override it per browser at runtime.
*/
export const DEFAULT_SERVER = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
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

/*
    The shared key the backend expects once ADMIN_KEY is set on it. Held per
    browser, so each coordinator enters it once. Sent on every request; the
    backend ignores it when it is running without a key.
*/
const KEY_STORAGE = 'adminKey';

export function getAdminKey() {
    if (typeof window === 'undefined') return '';
    return window.localStorage.getItem(KEY_STORAGE) || '';
}

export function setAdminKey(value) {
    const trimmed = (value || '').trim();
    if (trimmed) {
        window.localStorage.setItem(KEY_STORAGE, trimmed);
    } else {
        window.localStorage.removeItem(KEY_STORAGE);
    }
    return trimmed;
}

export function apiHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    const key = getAdminKey();
    if (key) headers['X-Admin-Key'] = key;
    const db = getDatabase();
    if (db) headers['X-Database'] = db;
    return headers;
}

/*
    Which of the backend's configured databases this browser talks to, by name.
    Never a connection string: the backend maps names to connection strings
    itself (see DATABASES in backend.py), so a browser can only pick among
    databases the operator has already allowed, and no password ever reaches
    localStorage or the network.
*/
const DATABASE_KEY = 'database';

export function getDatabase() {
    if (typeof window === 'undefined') return '';
    return window.localStorage.getItem(DATABASE_KEY) || '';
}

export function setDatabase(name) {
    const trimmed = (name || '').trim();
    if (trimmed) {
        window.localStorage.setItem(DATABASE_KEY, trimmed);
    } else {
        window.localStorage.removeItem(DATABASE_KEY);
    }
    return trimmed;
}

/*
    Names the backend currently accepts for X-Database, fetched fresh each
    time the picker opens so a newly added database shows up without a
    frontend redeploy. Returns [] on any failure (unreachable server, no key
    yet, old backend without the route) rather than throwing, since the menu
    should still let someone type the backend address itself.
*/
export async function listDatabases() {
    try {
        const res = await fetch(apiUrl('/databases'), { headers: apiHeaders() });
        if (!res.ok) return [];
        const body = await res.json();
        return Array.isArray(body.databases) ? body.databases : [];
    } catch (err) {
        return [];
    }
}
