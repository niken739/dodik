import React, { useEffect, useState } from 'react'
import { API_URL } from '../api'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const METRICS = [
  { key: 'temperature', label: 'Температура' },
  { key: 'humidity', label: 'Вологість' },
  { key: 'voltage', label: 'Напруга' },
  { key: 'co', label: 'CO' },
  { key: 'light', label: 'Освітленість' },
  { key: 'no2', label: 'NO₂' },
]

const Dashboard: React.FC = () => {
  const [status, setStatus] = useState('loading...')
  const [locations, setLocations] = useState<string[]>([])
  const [sensors, setSensors] = useState<any[]>([])
  const [selectedLocation, setSelectedLocation] = useState<string>('')
  const [selectedSensor, setSelectedSensor] = useState<string>('')
  const [timestamps, setTimestamps] = useState<string[]>([])
  const [fromTs, setFromTs] = useState<string>('')
  const [toTs, setToTs] = useState<string>('')
  const [data, setData] = useState<any[]>([])
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['temperature'])

  useEffect(() => {
    ;(async () => {
      try {
        const res = await fetch(`${API_URL}/health_check`)
        if (res.ok) {
          const body = await res.json()
          setStatus(body.status || 'ok')
        } else {
          setStatus('error')
        }
      } catch (err) {
        setStatus('network error')
      }
    })()
  }, [])

  useEffect(() => {
    ;(async () => {
      try {
        const res = await fetch(`${API_URL}/locations`)
        if (res.ok) setLocations(await res.json())
      } catch (e) {
        console.error(e)
      }
    })()
  }, [])

  useEffect(() => {
    if (!selectedLocation) return
    ;(async () => {
      try {
        const res = await fetch(`${API_URL}/sensors?location=${encodeURIComponent(selectedLocation)}`)
        if (res.ok) setSensors(await res.json())
        else setSensors([])
      } catch (e) {
        console.error(e)
      }
    })()
  }, [selectedLocation])

  useEffect(() => {
    if (!selectedSensor) return
    ;(async () => {
      try {
        const res = await fetch(`${API_URL}/measurements/${selectedSensor}/timestamps`)
        if (res.ok) {
          const ts = await res.json()
          setTimestamps(ts || [])
          if (ts && ts.length >= 2) {
            setFromTs(ts[0])
            setToTs(ts[ts.length - 1])
          }
        }
      } catch (e) {
        console.error(e)
      }
    })()
  }, [selectedSensor])

  const toggleMetric = (key: string) => {
    setSelectedMetrics((prev) => (prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]))
  }

  const show = async () => {
    if (!selectedSensor) return
    const params = new URLSearchParams()
    if (fromTs) params.append('from', fromTs)
    if (toTs) params.append('to', toTs)
    const url = `${API_URL}/measurements/${selectedSensor}?${params.toString()}`
    try {
      const res = await fetch(url)
      if (!res.ok) return
      const rows = await res.json()
      // Normalize data: ensure ts is a readable label
      const normalized = (rows || []).map((r: any) => ({
        ts: r.ts || r.time || r.timestamp || '',
        ...r,
      }))
      setData(normalized)
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div className="container">
      <h2>Dashboard</h2>
      <div className="api-status">API status: {status}</div>

      <div className="dashboard-layout">
        <div className="dashboard-inputs">
          <h3>Inputs</h3>
          
          <div className="form-group">
            <label>Location:</label>
            <select value={selectedLocation} onChange={(e) => setSelectedLocation(e.target.value)}>
              <option value="">--select--</option>
              {locations.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Sensor:</label>
            <select value={selectedSensor} onChange={(e) => setSelectedSensor(e.target.value)}>
              <option value="">--select--</option>
              {sensors.map((s) => (
                <option key={s.id || s.sensor_id || JSON.stringify(s)} value={s.id || s.sensor_id || s.id}>
                  {s.name || s.id || s.sensor_id}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>From:</label>
            <select value={fromTs} onChange={(e) => setFromTs(e.target.value)}>
              <option value="">--</option>
              {timestamps.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>To:</label>
            <select value={toTs} onChange={(e) => setToTs(e.target.value)}>
              <option value="">--</option>
              {timestamps.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Metrics:</label>
            <div className="metrics-group">
              {METRICS.map((m) => (
                <label key={m.key}>
                  <input type="checkbox" checked={selectedMetrics.includes(m.key)} onChange={() => toggleMetric(m.key)} />
                  {m.label}
                </label>
              ))}
            </div>
          </div>

          <button onClick={show}>Show Data</button>
        </div>

        <div className="dashboard-stats">
          <h3>Data</h3>
          <div style={{ height: 400, marginTop: 16 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="ts" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip contentStyle={{ backgroundColor: '#3a3a3a', border: '1px solid #555', borderRadius: '4px', color: '#e0e0e0' }} />
                <Legend wrapperStyle={{ color: '#e0e0e0' }} />
                {selectedMetrics.map((m, idx) => (
                  <Line key={m} type="monotone" dataKey={m} stroke={["#8884d8", "#82ca9d", "#ff7300", "#ff0000", "#00bfff", "#8a2be2"][idx % 6]} dot={false} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
