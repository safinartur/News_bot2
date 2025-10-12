import React, { useEffect, useState, useState } from 'react'
import { useParams } from 'react-router-dom'
import Layout from './Layout.jsx'
import PostCard from '../components/PostCard.jsx'
const API = import.meta.env.VITE_API_BASE

export default function Tag(){
  const { slug } = useParams()
  const [posts, setPosts] = useState([])

  useEffect, useState(()=>{
    (async ()=>{
      const r = await fetch(`${API}/posts/?tag=${slug}`)
      const data = await r.json()
      setPosts(data.results)
    })()
  }, [slug])

  return (
    <Layout>
      <h2>Тег: {slug}</h2>
      {posts.map(p => <PostCard key={p.id} post={p} />)}
    </Layout>
  )
}
