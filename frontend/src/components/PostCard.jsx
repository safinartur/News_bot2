import React from 'react'
import { Link } from 'react-router-dom'

export default function PostCard({ post }) {
  return (
    <article style={{border:'1px solid #eee', borderRadius:10, padding:14, marginBottom:12}}>
      <h3 style={{marginTop:0}}><Link to={`/post/${post.slug}`}>{post.title}</Link></h3>
      {post.cover && <img src={post.cover} alt="" style={{maxWidth:'100%', borderRadius:8}} />}
      <p style={{opacity:0.8, fontSize:12}}>{new Date(post.created_at).toLocaleString()}</p>
      <div style={{display:'flex', gap:8, flexWrap:'wrap'}}>
        {post.tags?.map(t => <Link key={t.slug} to={`/tag/${t.slug}`} style={{fontSize:12, background:'#f2f2f2', padding:'2px 8px', borderRadius:999}}>{t.name}</Link>)}
      </div>
    </article>
  )
}
