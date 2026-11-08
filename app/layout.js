import { Inter, Roboto_Mono } from "next/font/google";
import "./globals.css";
import SettingsMenu from "./SettingsMenu";

const geistSans = Inter({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Roboto_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "EZ-VolunteerSys",
  description: "Volunteer registration, shift logging and hour verification.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        <script
          dangerouslySetInnerHTML={{
            __html: `try{document.documentElement.setAttribute('data-theme', localStorage.getItem('theme') || 'light');}catch(e){}`,
          }}
        />
        <SettingsMenu />
        <div className="brand" aria-label="Guruvayurappan Temple of Brampton">
          <svg className="brand-mark" viewBox="0 0 32 32" width="26" height="26" aria-hidden="true">
            <g fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round">
              <path d="M16 5c3 4 3 9 0 13-3-4-3-9 0-13z" />
              <path d="M16 18c-1-5-5-8-10-8 0 5 4 9 10 8z" />
              <path d="M16 18c1-5 5-8 10-8 0 5-4 9-10 8z" />
              <path d="M8 24c5 3 11 3 16 0" />
            </g>
          </svg>
          <span className="brand-text">Guruvayurappan Temple of Brampton</span>
        </div>
        <main className="page-fade">{children}</main>
        <footer className="brand-footer">Hare Krishna &middot; Guruvayurappan Temple of Brampton</footer>
      </body>
    </html>
  );
}
