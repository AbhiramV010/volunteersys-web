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
        {children}
      </body>
    </html>
  );
}
