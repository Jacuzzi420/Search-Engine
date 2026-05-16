import { useState } from 'react'
import './SearchBar.css'
import SearchIcon from './search.png'

export default function SearchBar({ setResult }) {
    const [search, setSearch] = useState('')

    function handleSubmit(e) {
        e.preventDefault()
        console.log('subimitted')
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