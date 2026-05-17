import './SearchResult.css'

export default function SearchResult({result}){
    return (
        <div className='search-result'>
            {result.results.map(([title, url]) => (
                <a href={url}> {title} </a>
            ))}
        </div>
    )
}