/**
 * ChatArea.jsx — Scrollable message list container.
 */
import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import WelcomeScreen from './WelcomeScreen'
import TypingIndicator from './TypingIndicator'

const ChatArea = ({ messages, isLoading, videoUrl, sendMessage }) => {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const isEmpty = messages.length === 0

  return (
    <div style={{
      flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column',
      position: 'relative', scrollbarGutter: 'stable',
    }}>
      {isEmpty && <WelcomeScreen videoUrl={videoUrl} />}

      {!isEmpty && (
        <div style={{ padding: '1rem 0', display: 'flex', flexDirection: 'column', maxWidth: '850px', margin: '0 auto', width: '100%' }}>
          {messages.map((msg, idx) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              onRegenerate={msg.role === 'assistant' && idx === messages.length - 1 ? () => sendMessage(messages[idx-1].content) : undefined}
            />
          ))}
          {isLoading && <TypingIndicator />}
        </div>
      )}

      {/* Anchor */}
      <div ref={bottomRef} style={{ height: '1rem', flexShrink: 0 }} />
    </div>
  )
}

export default ChatArea
