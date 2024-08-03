import React, { useState } from 'react';
import { FaPlus, FaTrash, FaChartLine } from 'react-icons/fa';
import { AiOutlineLoading3Quarters } from 'react-icons/ai';
import './App.css';

function App() {
  const [activities, setActivities] = useState([]);
  const [name, setName] = useState('');
  const [optimisticTime, setOptimisticTime] = useState('');
  const [mostLikelyTime, setMostLikelyTime] = useState('');
  const [pessimisticTime, setPessimisticTime] = useState('');
  const [precedents, setPrecedents] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const addActivity = () => {
    setActivities([
      ...activities,
      { name, optimisticTime, mostLikelyTime, pessimisticTime, precedents }
    ]);
    setName('');
    setOptimisticTime('');
    setMostLikelyTime('');
    setPessimisticTime('');
    setPrecedents('');
  };

  const deleteActivity = (index) => {
    setActivities(activities.filter((_, i) => i !== index));
  };

  const analyzeActivities = async () => {
    setLoading(true);
    setResults(null);
    try {
      const response = await fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ activities })
      });
      const data = await response.json();
      setTimeout(() => {
        setLoading(false);
        setResults(data);
      }, 4000);
    } catch (error) {
      setLoading(false);
      console.error(error);
    }
  };

  return (
    <div className="app">
      <h1>PERT Analysis</h1>
      {loading ? (
        <div className="loading"><AiOutlineLoading3Quarters className="loading-icon" /> Analyzing...</div>
      ) : results ? (
        <div className="results">
          <h2>Estimated Duration: {results.estimatedDuration}</h2>
          <button onClick={() => setResults({ ...results, currentGraph: 'forwardPassGraph' })}>Forward Pass Graph</button>
          <button onClick={() => setResults({ ...results, currentGraph: 'backwardPassGraph' })}>Backward Pass Graph</button>
          <button onClick={() => setResults({ ...results, currentGraph: 'criticalPathGraph' })}>Critical Path Graph</button>
          {results.currentGraph && (
            <div className="graph">
              <img src={`data:image/png;base64,${results[results.currentGraph]}`} alt="Graph" />
            </div>
          )}
        </div>
      ) : (
        <>
          <div className="input-container">
            <div className="input-box">
              <input type="text" value={name} onChange={e => setName(e.target.value)} placeholder="Activity Name" />
              <input type="number" value={optimisticTime} onChange={e => setOptimisticTime(e.target.value)} placeholder="Optimistic Time" />
              <input type="number" value={mostLikelyTime} onChange={e => setMostLikelyTime(e.target.value)} placeholder="Most Likely Time" />
              <input type="number" value={pessimisticTime} onChange={e => setPessimisticTime(e.target.value)} placeholder="Pessimistic Time" />
              <input type="text" value={precedents} onChange={e => setPrecedents(e.target.value)} placeholder="Precedents (comma separated)" />
              <button onClick={addActivity}><FaPlus /> Add Activity</button>
            </div>
            <div className="activity-table">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Optimistic Time</th>
                    <th>Most Likely Time</th>
                    <th>Pessimistic Time</th>
                    <th>Precedents</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {activities.map((activity, index) => (
                    <tr key={index}>
                      <td>{activity.name}</td>
                      <td>{activity.optimisticTime}</td>
                      <td>{activity.mostLikelyTime}</td>
                      <td>{activity.pessimisticTime}</td>
                      <td>{activity.precedents}</td>
                      <td><button onClick={() => deleteActivity(index)}><FaTrash /></button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="analyze-button">
            <button onClick={analyzeActivities}><FaChartLine /> Analyze</button>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
