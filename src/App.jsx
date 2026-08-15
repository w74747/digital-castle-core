import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('http://localhost:8000/api/status')
      .then(r => r.json())
      .then(setData)
  }, [])

  return (
    <div className="App">
      <h1>🏰 Digital Castle</h1>
      <p>{data ? JSON.stringify(data) : 'Loading...'}</p>
    </div>
  )
}

export default App
