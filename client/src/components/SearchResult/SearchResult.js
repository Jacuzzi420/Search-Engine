import './SearchResult.css'

export default function SearchResult({result}){
    return (
        <div className='search-result'>
            {result.results.map(([title, url]) => (
                <a href={url} key={url}> {title} </a>
            ))}
        </div>
    )
}