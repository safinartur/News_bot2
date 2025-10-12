import React from 'react'
import { createRoot } from 'react-dom/client'
import { createHashRouter, RouterProvider } from 'react-router-dom'
import App from './pages/App.jsx'
import Post from './pages/Post.jsx'
import Tag from './pages/Tag.jsx'

const router = createHashRouter([
  { path: "/", element: <App /> },
  { path: "/post/:slug", element: <Post /> },
  { path: "/tag/:slug", element: <Tag /> },
])

createRoot(document.getElementById('root')).render(<RouterProvider router={router} />)
