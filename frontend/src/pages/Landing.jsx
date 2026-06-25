/**
 * Landing.jsx — Beautiful animated landing page.
 */
import { PlayCircle, MessageSquare, Zap, Shield, Search, ArrowRight, Code } from 'lucide-react'

const Landing = ({ onNavigate }) => {
  return (
    <div style={{
      minHeight: '100dvh',
      background: 'var(--bg-primary)',
      overflowY: 'auto',
      overflowX: 'hidden',
      position: 'relative',
    }}>
      {/* ── Background Orbs ── */}
      <div className="orb animate-orb" style={{
        width: 600, height: 600, background: 'rgba(99,102,241,0.15)',
        top: '-100px', left: '-200px',
      }} />
      <div className="orb animate-orb2" style={{
        width: 500, height: 500, background: 'rgba(139,92,246,0.15)',
        bottom: '10%', right: '-150px', animationDelay: '-5s',
      }} />

      {/* ── Navbar ── */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
        height: 'var(--topbar-height)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 2rem',
        background: 'rgba(11,15,25,0.7)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255,255,255,0.05)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{
            width: 28, height: 28, borderRadius: 8,
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <PlayCircle size={15} color="#fff" strokeWidth={2.5} />
          </div>
          <span style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff', letterSpacing: '-0.02em' }}>
            VideoMind <span style={{ color: 'var(--accent-hover)' }}>AI</span>
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>

          <button onClick={() => onNavigate('app')} className="btn-primary" style={{ padding: '0.4rem 1rem', fontSize: '0.8rem' }}>
            Open App
          </button>
        </div>
      </nav>

      {/* ── Hero Section ── */}
      <section style={{
        padding: '8rem 2rem 5rem',
        display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center',
        position: 'relative', zIndex: 10,
        maxWidth: '900px', margin: '0 auto',
      }}>
        <div className="animate-fade-slide-up" style={{
          display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
          padding: '0.3rem 0.8rem', borderRadius: '99px',
          background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)',
          marginBottom: '1.5rem',
        }}>
          <SparklesIcon />
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--accent-hover)' }}>
            Powered by Google Gemini
          </span>
        </div>

        <h1 className="animate-fade-slide-up" style={{ animationDelay: '0.1s', fontSize: 'clamp(2.5rem, 5vw, 4.5rem)', fontWeight: 800, lineHeight: 1.1, letterSpacing: '-0.03em', marginBottom: '1.5rem', color: '#fff' }}>
          Chat with any <br/>
          <span className="gradient-text-accent">YouTube Video</span>
        </h1>
        
        <p className="animate-fade-slide-up" style={{ animationDelay: '0.2s', fontSize: '1.1rem', color: 'var(--text-secondary)', maxWidth: '600px', lineHeight: 1.6, marginBottom: '2.5rem' }}>
          Turn any YouTube video into an intelligent AI assistant. Paste a URL, ask questions, and get instant answers grounded perfectly in the video's transcript.
        </p>

        <div className="animate-fade-slide-up" style={{ animationDelay: '0.3s', display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
          <button onClick={() => onNavigate('app')} className="btn-primary" style={{ padding: '0.8rem 2rem', fontSize: '1rem', borderRadius: '99px' }}>
            Start Chatting Free <ArrowRight size={18} />
          </button>
          <button onClick={() => document.getElementById('features').scrollIntoView()} className="btn-secondary" style={{ padding: '0.8rem 2rem', fontSize: '1rem', borderRadius: '99px' }}>
            View Features
          </button>
        </div>

        {/* ── Mockup / UI Preview ── */}
        <div className="animate-fade-slide-up" style={{ animationDelay: '0.4s', marginTop: '4rem', width: '100%', position: 'relative' }}>
          <div style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border)',
            borderRadius: '16px',
            padding: '1rem',
            boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5), 0 0 0 1px rgba(99,102,241,0.1)',
            overflow: 'hidden',
          }}>
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ef4444' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#f59e0b' }} />
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#10b981' }} />
            </div>
            {/* Fake chat */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', textAlign: 'left' }}>
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <div style={{ background: 'var(--user-bubble)', color: '#fff', padding: '0.6rem 1rem', borderRadius: '12px', borderTopRightRadius: 2, fontSize: '0.85rem' }}>
                  What are the 3 main takeaways from this lecture?
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--text-primary)', padding: '0.6rem 1rem', borderRadius: '12px', borderTopLeftRadius: 2, fontSize: '0.85rem' }}>
                  Based on the transcript, the 3 main takeaways are: <br/><br/>
                  1. **Transformers revolutionized NLP** by replacing RNNs.<br/>
                  2. **Attention is all you need** is the core mechanism.<br/>
                  3. **Parallelization** allows training massive models.
                </div>
              </div>
            </div>
          </div>
          {/* Gradient floor glow */}
          <div style={{ position: 'absolute', bottom: '-20px', left: '10%', right: '10%', height: '40px', background: 'var(--accent)', filter: 'blur(40px)', opacity: 0.3, zIndex: -1 }} />
        </div>
      </section>

      {/* ── Features Grid ── */}
      <section id="features" style={{ padding: '6rem 2rem', maxWidth: '1100px', margin: '0 auto', position: 'relative', zIndex: 10 }}>
        <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
          <h2 style={{ fontSize: '2.2rem', fontWeight: 800, color: '#fff', marginBottom: '1rem' }}>Engineered for Excellence</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>Everything you need to extract knowledge from video content.</p>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {[
            { icon: <Zap size={24}/>, title: 'Ultra-Fast Inference', text: 'Powered by Google Gemini, answers stream back to you instantly.' },
            { icon: <Shield size={24}/>, title: 'Zero Hallucinations', text: 'Strictly grounded RAG architecture ensures the AI only uses facts from the video transcript.' },
            { icon: <Search size={24}/>, title: 'Source Citations', text: 'Every answer includes exact transcript chunks so you can verify the information instantly.' },
            { icon: <MessageSquare size={24}/>, title: 'Natural Conversations', text: 'Ask follow-up questions and chat naturally. The AI remembers the context of the video.' },
          ].map((f, i) => (
            <div key={i} className="feature-card glass-elevated">
              <div style={{ width: 48, height: 48, borderRadius: 12, background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-light)', marginBottom: '1.5rem' }}>
                {f.icon}
              </div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '0.5rem' }}>{f.title}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.6 }}>{f.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer ── */}
      <footer style={{ borderTop: '1px solid var(--border)', padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        <p>© 2026 VideoMind AI. Built with FastAPI, LangChain, FAISS & React.</p>
      </footer>
    </div>
  )
}

const SparklesIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
    <path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/>
  </svg>
)

export default Landing
