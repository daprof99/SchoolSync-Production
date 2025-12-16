import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
    title: 'SchoolSync 2.0 - Admin Dashboard',
    description: 'AI-powered school management dashboard',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className="bg-gray-50">{children}</body>
        </html>
    )
}
