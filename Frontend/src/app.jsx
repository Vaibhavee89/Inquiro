import React, {useState} from 'react'
import { search } from './api'
import ReactFlow, { MiniMap, Controls } from 'react-flow-renderer'

export default function App(){
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSearch(){
    setLoading(true)
    try{
      const data = await search(query,5)
      setResults(data)
    }catch(e){
      console.error(e)
      alert('Search failed')
    }finally{ setLoading(false) }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">AI Research Assistant</h1>
      <div className="mt-4">
        <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Enter topic" className="border p-2 w-2/3" />
        <button onClick={handleSearch} className="ml-2 p-2 bg-slate-700 text-white">Search</button>
      </div>

      {loading && <p>Loading...</p>}

      {results && (
        <div className="mt-6 grid grid-cols-2 gap-4">
          <div>
            <h2 className="font-semibold">Papers</h2>
            {results.papers.map((p, idx) => (
              <div key={idx} className="border p-3 my-2">
                <a href={p.link} target="_blank" rel="noreferrer" className="font-medium">{p.title}</a>
                <p className="text-sm">{p.published} — {p.authors.join(', ')}</p>
                <details>
                  <summary>Summary</summary>
                  <pre>{JSON.stringify(results.summaries[idx], null, 2)}</pre>
                </details>
                <details>
                  <summary>Citation</summary>
                  <pre>{results.citations[idx].apa}</pre>
                </details>
              </div>
            ))}
          </div>
          <div>
            <h2 className="font-semibold">Mind Map</h2>
            {/* Lightweight node mapping: each paper -> node with bullets as children */}
            <div style={{height:400}}>
              <ReactFlow elements={buildFlowElements(results)}>
                <MiniMap />
                <Controls />
              </ReactFlow>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function buildFlowElements(results){
  if(!results) return []
  const nodes = []
  const edges = []
  results.papers.forEach((p, i) => {
    nodes.push({ id: 'p'+i, type: 'default', data: { label: p.title }, position: { x: 50, y: i*80 } })
    const bullets = (results.summaries[i] && results.summaries[i].bullets) || []
    bullets.forEach((b, j) => {
      const id = `p${i}b${j}`
      nodes.push({ id, data: { label: b }, position: { x: 350, y: i*80 + j*20 } })
      edges.push({ id: `e-${i}-${j}`, source: 'p'+i, target: id })
    })
  })
  return [...nodes, ...edges]
}