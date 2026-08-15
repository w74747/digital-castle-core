import { useState, useEffect, useRef } from 'react'

export function WebSocketChat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const ws = useRef(null)

  useEffect(() => {
    const token = localStorage.getItem('token')
    ws.current = new WebSocket(`ws://localhost:8001/api/v2/ws/${token}`)
    
    ws.current.onmessage = (event) => {
      setMessages(prev => [...prev, JSON.parse(event.data)])
    }

    return () => ws.current?.close()
  }, [])

  const send = () => {
    if (input && ws.current) {
      ws.current.send(input)
      setInput('')
    }
  }

  return (
    <div>
      <h2>Real-time Chat</h2>
      <div style={{ height: '300px', border: '1px solid #ccc', overflowY: 'auto', padding: '10px' }}>
        {messages.map((msg, i) => <div key={i}>{JSON.stringify(msg)}</div>)}
      </div>
      <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type message..." />
      <button onClick={send}>Send</button>
    </div>
  )
}
