import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { API_URL } from '../api'

const Register: React.FC = () => {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      const res = await fetch(`${API_URL}/auth/registration`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login, password })
      })
      if (res.status === 201) {
        alert('Registration successful — please login')
        navigate('/login')
      } else {
        const body = await res.json()
        setError(body.error || 'Registration failed')
      }
    } catch (err) {
      setError('Network error')
    }
  }

  return (
    <div className="form-centered">
      <div className="form-card">
        <h2>Register</h2>
        <form onSubmit={submit}>
          <input value={login} onChange={e => setLogin(e.target.value)} placeholder="Login" />
          <input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="Password" />
          <button type="submit">Register</button>
          {error && <div className="error">{error}</div>}
        </form>
      </div>
    </div>
  )
}

export default Register
