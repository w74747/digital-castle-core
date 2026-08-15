import { useState, useEffect } from 'react'
import { TaskList } from './components/TaskList'
import './App.css'

function App() {
  const [data, setData] = useState(null)
  const [agents, setAgents] = useState([])

  useEffect(() => {
    fetch('http://localhost:8000/api/status')
      .then(r => r.json())
      .then(setData)
    
    fetch('http://localhost:8000/api/agents')
      .then(r => r.json())
      .then(d => setAgents(d.agents || []))
  }, [])

  return (
    <div className="App">
      <h1>🏰 Digital Castle</h1>
      <div>
        <h2>Status</h2>
        <pre>{data ? JSON.stringify(data, null, 2) : 'Loading...'}</pre>
      </div>
      <div>
        <h2>Agents ({agents.length})</h2>
        <ul>
          {agents.map(agent => <li key={agent}>{agent}</li>)}
        </ul>
      </div>
      <TaskList />
    </div>
  )
}

export default App
