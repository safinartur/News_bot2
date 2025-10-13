import React from 'react'
import { createRoot } from 'react-dom/client'
import { createHashRouter, RouterProvider } from 'react-router-dom'

import App from './pages/App.jsx'
import Post from './pages/Post.jsx'
import Tag from './pages/Tag.jsx'

// Определяем маршруты
const router = createHashRouter([
  { path: '/', element: <App /> },
  { path: '/post/:slug', element: <Post /> },
  { path: '/tag/:slug', element: <Tag /> },
])

// Безопасная инициализация приложения
const container = document.getElementById('root')
if (container) {
  const root = createRoot(container)
  root.render(
    <React.StrictMode>
      <RouterProvider router={router} />
    </React.StrictMode>
  )
} else {
  console.error('❌ Не найден элемент с id="root" в index.html')
}
