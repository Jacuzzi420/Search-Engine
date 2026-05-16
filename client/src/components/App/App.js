import './App.css'
import { useState } from 'react'
import SearchBar from '../SearchBar/SearchBar'
import SearchResult from '../SearchResult/SearchResult'

export default function App() {
  const [result, setResult] = useState({})

  return (
    <div className='main-wrapper'>
      <SearchBar setResult={setResult}/>
      <SearchResult result={result}/>
    </div>
  )
}
