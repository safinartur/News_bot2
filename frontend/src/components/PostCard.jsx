import React from 'react'
import { Link } from 'react-router-dom'

export default function PostCard({ post }) {
  if (!post) return null

  return (
    <article
      style={{
        border: '1px solid #eee',
        borderRadius: 10,
        padding: 14,
        marginBottom: 16,
        background: '#fff',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      }}
    >
      <h3 style={{ marginTop: 0, marginBottom: 8 }}>
        <Link
          to={`/post/${post.slug}`}
          style={{ color: '#0077cc', textDecoration: 'none' }}
        >
          {post.title}
        </Link>
      </h3>

      {post.cover && (
        <img
          src={post.cover}
          alt={post.title}
          style={{
            maxWidth: '100%',
            maxHeight: 300,
            objectFit: 'cover',
            borderRadius: 8,
            marginBottom: 8,
          }}
        />
      )}

      {post.created_at && (
        <p
          style={{
            opacity: 0.6,
            fontSize: 12,
            margin: 0,
            marginBottom: 10,
          }}
        >
          {new Date(post.created_at).toLocaleString()}
        </p>
      )}

      {post.tags?.length > 0 && (
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {post.tags.map((t) => (
            <Link
              key={t.slug}
              to={`/tag/${t.slug}`}
              style={{
                fontSize: 12,
                background: '#f2f2f2',
                padding: '2px 8px',
                borderRadius: 999,
                textDecoration: 'none',
                color: '#333',
              }}
            >
              {t.name}
            </Link>
          ))}
        </div>
      )}
    </article>
  )
}
