import React from 'react'
import { Link } from 'react-router-dom'

export default function Layout({children}){
  return (
    <div style={{maxWidth:900, margin:'0 auto', padding:16}}>
      <header style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20}}>
        <h1 style={{margin:0}}><Link to="/">Новости</Link></h1>
        <nav><a href="https://t.me/" target="_blank" rel="noreferrer">Мы в Telegram</a></nav>
      </header>
      {children}
      <footer style={{marginTop:40, opacity:0.7}}>© {new Date().getFullYear()}</footer>
    </div>
  )
}
