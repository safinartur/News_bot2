import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import Layout from './Layout.jsx'
import PostCard from '../components/PostCard.jsx'

const API = import.meta.env.VITE_API_BASE

export default function Tag() {
  const { slug } = useParams()
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchPosts() {
      try {
        setLoading(true)
        setError(null)
        const r = await fetch(`${API}/posts/?tags__slug=${slug}`)
        if (!r.ok) throw new Error(`Ошибка загрузки (${r.status})`)
        const data = await r.json()
        setPosts(data.results || [])
      } catch (e) {
        setError(String(e))
      } finally {
        setLoading(false)
      }
    }
    fetchPosts()
  }, [slug])

  return (
    <Layout>
      <h2>Тег: {slug}</h2>
      {loading && <p>Загрузка…</p>}
      {error && <p style={{ color: 'red' }}>Ошибка: {error}</p>}
      {!loading && !error && posts.length === 0 && <p>Постов нет.</p>}
      {posts.map((p) => (
        <PostCard key={p.id} post={p} />
      ))}
    </Layout>
  )
}
