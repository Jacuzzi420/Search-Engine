import { useState } from 'react'
import axios from 'axios'
import './SearchBar.css'
import SearchIcon from './search.png'

export default function SearchBar({ setResult }) {
    const [search, setSearch] = useState('')

    async function handleSubmit(e) {
        e.preventDefault()

        try {
            const { data } = await axios.get(`http://localhost:8000/search?query=${search.split(' ').join('+')}`)
            setResult(data)
            console.log(data)
        } catch(error) {
            console.log(error)
        }
    }

    function handleChange(e) {
        setSearch(e.target.value)
    }
    
    return (
        <div className='search-bar'>
            <form className='search-bar-input-wrapper' onSubmit={handleSubmit}>
                <button className='search-bar-input-wrapper-button'> 
                    <img className='search-bar-input-wrapper-button-image' src={SearchIcon} alt='Search icon'/>
                </button>
                <input type='text' placeholder='Search...' value={search} onChange={handleChange}
                className='search-bar-input-wrapper-input'/>
            </form>
        </div>
    )
}