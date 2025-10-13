import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import Layout from './Layout.jsx'

const API = import.meta.env.VITE_API_BASE

export default function Post() {
  const { slug } = useParams()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [post, setPost] = useState(null)

  useEffect(() => {
    async function fetchPost() {
      try {
        setLoading(true)
        setError(null)
        const r = await fetch(`${API}/posts/${slug}/`)
        if (!r.ok) throw new Error(`Ошибка загрузки (${r.status})`)
        const data = await r.json()
        setPost(data)
      } catch (e) {
        setError(String(e))
      } finally {
        setLoading(false)
      }
    }
    fetchPost()
  }, [slug])

  if (loading) return <Layout>Загрузка…</Layout>
  if (error) return <Layout>Ошибка: {error}</Layout>
  if (!post) return <Layout>Пост не найден.</Layout>

  return (
    <Layout>
      <h2>{post.title}</h2>
      {post.cover && (
        <img
          src={post.cover}
          alt=""
          style={{ maxWidth: '100%', borderRadius: 8, marginBottom: 10 }}
        />
      )}
      <p style={{ opacity: 0.6 }}>
        {new Date(post.created_at).toLocaleString()}
      </p>
      <div
        dangerouslySetInnerHTML={{
          __html: post.body.replace(/\n/g, '<br/>'),
        }}
      />
      <div style={{ marginTop: 20 }}>
        {post.tags?.map((t) => (
          <Link
            key={t.slug}
            to={`/tag/${t.slug}`}
            style={{
              fontSize: 12,
              background: '#f2f2f2',
              padding: '2px 8px',
              borderRadius: 999,
              marginRight: 6,
            }}
          >
            {t.name}
          </Link>
        ))}
      </div>
    </Layout>
  )
}
