import { useState, useEffect } from 'react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export function Analytics() {
  const [analytics, setAnalytics] = useState(null)

  useEffect(() => {
    fetch('http://localhost:8001/api/v2/analytics/advanced', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(r => r.json())
      .then(setAnalytics)
  }, [])

  if (!analytics) return <div>Loading...</div>

  const data = [
    { name: 'Completed', value: analytics.summary.completed },
    { name: 'Failed', value: analytics.summary.failed },
    { name: 'Running', value: analytics.summary.running }
  ]

  return (
    <div>
      <h2>Analytics Dashboard</h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div>
          <h3>Task Status</h3>
          <pre>{JSON.stringify(analytics.summary, null, 2)}</pre>
        </div>
        <div>
          <h3>By Agent</h3>
          <pre>{JSON.stringify(analytics.by_agent, null, 2)}</pre>
        </div>
      </div>
    </div>
  )
}
