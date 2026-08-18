'use client';
import { useEffect, useRef, useState } from 'react';
import {
    DEFAULT_SERVER, getAdminKey, getDatabase, getServer, listDatabases,
    normaliseServer, resetServer, setAdminKey, setDatabase, setServer,
} from './serverConfig';

const THEMES = [
    { value: 'light', label: 'Light' },
    { value: 'dark', label: 'Dark' },
    { value: 'temple', label: 'Temple' },
];

export default function SettingsMenu() {
    const [open, setOpen] = useState(false);
    const [view, setView] = useState('root');
    const [theme, setTheme] = useState('light');
    const [server, setServerState] = useState(DEFAULT_SERVER);
    const [draft, setDraft] = useState(DEFAULT_SERVER);
    const [note, setNote] = useState('');
    const [keySet, setKeySet] = useState(false);
    const [keyDraft, setKeyDraft] = useState('');
    const [database, setDatabaseState] = useState('');
    const [databases, setDatabases] = useState([]);
    const [databasesLoading, setDatabasesLoading] = useState(false);
    const root = useRef(null);

    // Read stored settings after mount so the first render matches the server output.
    useEffect(() => {
        const storedTheme = window.localStorage.getItem('theme') || 'light';
        setTheme(storedTheme);
        document.documentElement.setAttribute('data-theme', storedTheme);

        const storedServer = getServer();
        setServerState(storedServer);
        setDraft(storedServer);
        setKeySet(getAdminKey() !== '');
        setDatabaseState(getDatabase());
    }, []);

    useEffect(() => {
        if (!open) return undefined;

        const onPointerDown = (e) => {
            if (root.current && !root.current.contains(e.target)) closeMenu();
        };
        const onKeyDown = (e) => {
            if (e.key === 'Escape') closeMenu();
        };

        document.addEventListener('mousedown', onPointerDown);
        document.addEventListener('keydown', onKeyDown);
        return () => {
            document.removeEventListener('mousedown', onPointerDown);
            document.removeEventListener('keydown', onKeyDown);
        };
    }, [open]);

    const closeMenu = () => {
        setOpen(false);
        setView('root');
        setNote('');
    };

    const toggleMenu = () => {
        if (open) {
            closeMenu();
        } else {
            setDraft(getServer());
            setOpen(true);
        }
    };

    const chooseTheme = (next) => {
        setTheme(next);
        document.documentElement.setAttribute('data-theme', next);
        window.localStorage.setItem('theme', next);
    };

    const saveServer = (e) => {
        e.preventDefault();
        const normalised = normaliseServer(draft);
        if (!normalised) {
            setNote('That does not look like a valid address.');
            return;
        }
        setServer(normalised);
        setServerState(normalised);
        setDraft(normalised);
        setNote(`Requests now go to ${normalised}`);
    };

    const useDefaultServer = () => {
        const fallback = resetServer();
        setServerState(fallback);
        setDraft(fallback);
        setNote(`Back to ${fallback}`);
    };

    // Asked fresh each time the screen opens, against whichever backend address
    // and key are current, so it reflects a database the operator just added.
    const openServerView = async () => {
        setView('server');
        setDatabasesLoading(true);
        const names = await listDatabases();
        setDatabases(names);
        setDatabasesLoading(false);
    };

    const chooseDatabase = (name) => {
        const stored = setDatabase(name);
        setDatabaseState(stored);
        setNote(stored ? `Now using the '${stored}' database` : 'Back to the default database');
    };

    const saveKey = (e) => {
        e.preventDefault();
        const stored = setAdminKey(keyDraft);
        setKeySet(stored !== '');
        setKeyDraft('');
        setNote(stored ? 'Admin key saved on this device' : 'Admin key cleared');
    };

    const clearKey = () => {
        setAdminKey('');
        setKeySet(false);
        setKeyDraft('');
        setNote('Admin key cleared');
    };

    return (
        <div className="menu-root" ref={root}>
            <button
                className={`menu-toggle${open ? ' menu-toggle-open' : ''}`}
                type="button"
                onClick={toggleMenu}
                aria-expanded={open}
                aria-haspopup="menu"
                aria-label="Settings menu"
            >
                <span className="menu-bars">
                    <span />
                    <span />
                    <span />
                </span>
            </button>
            {open && (
                <div className="menu-panel" role="menu" aria-label="Settings">
                    {view === 'root' && (
                        <>
                            <button className="menu-item" type="button" onClick={() => setView('theme')}>
                                <span>Change theme</span>
                                <span className="menu-hint">{THEMES.find((t) => t.value === theme)?.label}</span>
                            </button>
                            <button className="menu-item" type="button" onClick={openServerView}>
                                <span>Change server</span>
                                <span className="menu-hint">{database || server.replace(/^https?:\/\//, '')}</span>
                            </button>
                            <button className="menu-item" type="button" onClick={() => setView('key')}>
                                <span>Admin key</span>
                                <span className="menu-hint">{keySet ? 'Saved' : 'Not set'}</span>
                            </button>
                        </>
                    )}

                    {view === 'theme' && (
                        <>
                            <div className="menu-head">
                                <button className="menu-back" type="button" onClick={() => setView('root')}
                                    aria-label="Back to menu">&larr;</button>
                                <span>Change theme</span>
                            </div>
                            {THEMES.map((option) => (
                                <button
                                    key={option.value}
                                    className={`menu-item${option.value === theme ? ' menu-item-active' : ''}`}
                                    type="button"
                                    onClick={() => chooseTheme(option.value)}
                                >
                                    <span>{option.label}</span>
                                    {option.value === theme && <span className="menu-hint">&#10003;</span>}
                                </button>
                            ))}
                        </>
                    )}

                    {view === 'server' && (
                        <>
                            <div className="menu-head">
                                <button className="menu-back" type="button" onClick={() => setView('root')}
                                    aria-label="Back to menu">&larr;</button>
                                <span>Change server</span>
                            </div>
                            <form className="menu-form" onSubmit={saveServer}>
                                <label className="menu-label" htmlFor="server-address">Backend address</label>
                                <input
                                    id="server-address"
                                    className="menu-input"
                                    type="text"
                                    value={draft}
                                    placeholder={DEFAULT_SERVER}
                                    onChange={(e) => { setDraft(e.target.value); setNote(''); }}
                                    autoComplete="off"
                                    spellCheck="false"
                                />
                                <div className="menu-form-actions">
                                    <button className="btn menu-save" type="submit">Save</button>
                                    <button className="btn btn-secondary menu-save" type="button"
                                        onClick={useDefaultServer}>Default</button>
                                </div>
                            </form>

                            <div className="menu-head">
                                <span>Database</span>
                            </div>
                            {databasesLoading && <p className="menu-note">Checking what's available...</p>}
                            {!databasesLoading && databases.length === 0 && (
                                <p className="menu-note">
                                    No database list from this backend yet. It uses its default until one is
                                    chosen here.
                                </p>
                            )}
                            {!databasesLoading && databases.map((name) => (
                                <button
                                    key={name}
                                    className={`menu-item${name === database ? ' menu-item-active' : ''}`}
                                    type="button"
                                    onClick={() => chooseDatabase(name)}
                                >
                                    <span>{name}</span>
                                    {name === database && <span className="menu-hint">&#10003;</span>}
                                </button>
                            ))}
                            {note && <p className="menu-note">{note}</p>}
                        </>
                    )}

                    {view === 'key' && (
                        <>
                            <div className="menu-head">
                                <button className="menu-back" type="button" onClick={() => setView('root')}
                                    aria-label="Back to menu">&larr;</button>
                                <span>Admin key</span>
                            </div>
                            <form className="menu-form" onSubmit={saveKey}>
                                <label className="menu-label" htmlFor="admin-key">
                                    {keySet ? 'A key is saved. Enter a new one to replace it.' : 'Key issued by your coordinator'}
                                </label>
                                <input
                                    id="admin-key"
                                    className="menu-input"
                                    type="password"
                                    value={keyDraft}
                                    placeholder={keySet ? '••••••••' : ''}
                                    onChange={(e) => { setKeyDraft(e.target.value); setNote(''); }}
                                    autoComplete="off"
                                    spellCheck="false"
                                />
                                <div className="menu-form-actions">
                                    <button className="btn menu-save" type="submit">Save</button>
                                    <button className="btn btn-secondary menu-save" type="button"
                                        onClick={clearKey}>Clear</button>
                                </div>
                            </form>
                            {note && <p className="menu-note">{note}</p>}
                        </>
                    )}
                </div>
            )}

        </div>
    );
}
