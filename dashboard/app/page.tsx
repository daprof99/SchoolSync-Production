'use client'

import { useEffect, useState } from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface DashboardStats {
    totalRevenue: number
    totalOutstanding: number
    totalDebtors: number
    totalStudents: number
    recentPayments: Array<{ date: string, amount: number }>
    pendingMessages: number
}

export default function Dashboard() {
    const [stats, setStats] = useState<DashboardStats | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        // Mock data - replace with API call to your FastAPI backend
        const mockStats: DashboardStats = {
            totalRevenue: 5450000,
            totalOutstanding: 1230000,
            totalDebtors: 45,
            totalStudents: 150,
            recentPayments: [
                { date: 'Mon', amount: 120000 },
                { date: 'Tue', amount: 150000 },
                { date: 'Wed', amount: 95000 },
                { date: 'Thu', amount: 180000 },
                { date: 'Fri', amount: 140000 },
            ],
            pendingMessages: 8
        }

        setTimeout(() => {
            setStats(mockStats)
            setLoading(false)
        }, 500)
    }, [])

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-2xl font-bold text-gray-600">Loading...</div>
            </div>
        )
    }

    if (!stats) return null

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        SchoolSync 2.0 Dashboard
                    </h1>
                    <p className="text-gray-600 mt-2">AI-Powered School Management</p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div className="stat-card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                        <div>
                            <p className="text-blue-100 text-sm">Total Revenue</p>
                            <p className="text-3xl font-bold">₦{(stats.totalRevenue / 1000000).toFixed(1)}M</p>
                        </div>
                        <div className="text-5xl opacity-20">💰</div>
                    </div>

                    <div className="stat-card bg-gradient-to-br from-red-500 to-red-600 text-white">
                        <div>
                            <p className="text-red-100 text-sm">Outstanding</p>
                            <p className="text-3xl font-bold">₦{(stats.totalOutstanding / 1000000).toFixed(1)}M</p>
                        </div>
                        <div className="text-5xl opacity-20">📉</div>
                    </div>

                    <div className="stat-card bg-gradient-to-br from-yellow-500 to-orange-600 text-white">
                        <div>
                            <p className="text-yellow-100 text-sm">Debtors</p>
                            <p className="text-3xl font-bold">{stats.totalDebtors}</p>
                        </div>
                        <div className="text-5xl opacity-20">⚠️</div>
                    </div>

                    <div className="stat-card bg-gradient-to-br from-green-500 to-green-600 text-white">
                        <div>
                            <p className="text-green-100 text-sm">Students</p>
                            <p className="text-3xl font-bold">{stats.totalStudents}</p>
                        </div>
                        <div className="text-5xl opacity-20">🎓</div>
                    </div>
                </div>

                {/* Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    <div className="card">
                        <h3 className="text-lg font-semibold mb-4">Weekly Revenue</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={stats.recentPayments}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" />
                                <YAxis />
                                <Tooltip />
                                <Line type="monotone" dataKey="amount" stroke="#3b82f6" strokeWidth={2} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="card">
                        <h3 className="text-lg font-semibold mb-4">Payment Breakdown</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={stats.recentPayments}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="amount" fill="#8b5cf6" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="card">
                    <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <button className="btn-primary">
                            📢 Send Broadcast
                        </button>
                        <button className="btn-primary">
                            📊 Export Reports
                        </button>
                        <button className="btn-primary">
                            📬 Messages ({stats.pendingMessages})
                        </button>
                        <button className="btn-primary">
                            📤 Upload Results
                        </button>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-8 text-center text-gray-500 text-sm">
                    <p>Built with ❤️ using Llama 3.3, LangGraph & Next.js</p>
                </div>
            </div>
        </div>
    )
}
