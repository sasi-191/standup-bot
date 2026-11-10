import './App.css'
import { useState, useEffect } from 'react'

const API_URL = "http://127.0.0.1:8000"

function App(){
  const [standups, setStandups] = useState([])
  const [missing, setMissing] = useState([])
  // "today" or "all" — which standups to show
  const [view, setView] = useState("today")
  const [searchName, setSearchName] = useState("")
  const [searchDay, setSearchDay] = useState("")

  function loadStandups() {
    let url = API_URL + "/standups/today"
    if (view === "all") {
      url = API_URL + "/standups?name=" + searchName
      if (searchDay !== "") {
        url = url + "&day=" + searchDay
      }
    }

    fetch(url)
      .then((response) => response.json())
      .then((data) => {
        setStandups(data)
      })

    fetch(API_URL + "/standups/missing")
      .then((response) => response.json())
      .then((data) => {
        setMissing(data)
      })
  }

  useEffect(() => {
    loadStandups()

    const timer = setInterval(() => {
      loadStandups()
    }, 5000)

    return () => {
      clearInterval(timer)
    }
  }, [view, searchName, searchDay])

  let emptyMessage = null
  if (standups.length === 0) {
    emptyMessage = <p>No standups yet.</p>
  }

  let missingMessage = <p>Everyone has sent today's standup.</p>
  if (missing.length > 0) {
    missingMessage = <p className='missing'>Missing today: {missing.join(", ")}</p>
  }

return(
  <div className='page'>
      <h1>Team standups</h1>
      <p>Total Standups: {standups.length}</p>
      {missingMessage}

      <button onClick={() => setView("today")}>Today</button>
      <button onClick={() => setView("all")}>All</button>
      <p>Showing: {view}</p>

      {view === "all" && (
        <div className='filters'>
          <input placeholder='Search by name' value={searchName}
                 onChange={(e) => setSearchName(e.target.value)} />
          <input type='date' value={searchDay}
                 onChange={(e) => setSearchDay(e.target.value)} />
        </div>
      )}

      {emptyMessage}
      {standups.map((standup) => (
        <div key={standup.id} className="card">
          <h3>{standup.name}</h3>
          <p><b>Yesterday:</b> {standup.yesterday}</p>
          <p><b>Today:</b> {standup.today}</p>
          <p><b>Blockers:</b> {standup.blockers}</p>
          <p className='date'><small>{standup.created_at}</small></p>
        </div>
      ))}

  </div>
)
}
export default App
