import { useState, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

interface CodeBlockProps {
  language: string
  children: string
}

function CodeBlock({ language, children }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(children)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      console.error('Failed to copy code')
    }
  }, [children])

  return (
    <div className="relative group my-2">
      <div
        className="flex items-center justify-between text-xs px-3 py-1.5 rounded-t-lg"
        style={{
          background: 'var(--token-surface-tertiary)',
          color: 'var(--token-text-secondary)',
        }}
      >
        <span>{language || 'code'}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 px-2 py-1 rounded transition-colors"
          style={{ background: 'transparent' }}
          title="Copy code"
        >
          {copied ? (
            <>
              <svg
                className="w-4 h-4"
                style={{ color: 'var(--color-success)' }}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span style={{ color: 'var(--color-success)' }}>Copied!</span>
            </>
          ) : (
            <>
              <svg
                className="w-4 h-4"
                style={{ color: 'var(--token-text-tertiary)' }}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span style={{ color: 'var(--token-text-tertiary)' }}>Copy</span>
            </>
          )}
        </button>
      </div>
      <SyntaxHighlighter
        language={language || 'text'}
        style={oneDark}
        customStyle={{
          margin: 0,
          borderTopLeftRadius: 0,
          borderTopRightRadius: 0,
          borderTop: 'none',
        }}
        showLineNumbers={true}
      >
        {children}
      </SyntaxHighlighter>
    </div>
  )
}

interface MarkdownRendererProps {
  content: string
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <div className="markdown-content prose prose-sm max-w-none dark:prose-invert">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '')
            const isInline = !match && !String(children).includes('\n')

            if (isInline) {
              return (
                <code
                  className="px-1 py-0.5 rounded font-mono"
                  style={{
                    background: 'var(--token-surface-tertiary)',
                    color: 'var(--token-text-primary)',
                  }}
                  {...props}
                >
                  {children}
                </code>
              )
            }

            return (
              <CodeBlock language={match ? match[1] : ''}>
                {String(children).replace(/\n$/, '')}
              </CodeBlock>
            )
          },
          pre({ children }) {
            return <>{children}</>
          },
          a({ href, children }) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="underline"
                style={{ color: '#3b82f6' }}
              >
                {children}
              </a>
            )
          },
          table({ children }) {
            return (
              <div className="overflow-x-auto my-2">
                <table
                  className="min-w-full divide-y"
                  style={{
                    borderColor: 'var(--token-border-light)',
                    border: '1px solid var(--token-border-light)',
                  }}
                >
                  {children}
                </table>
              </div>
            )
          },
          th({ children }) {
            return (
              <th
                className="px-2 py-1.5 text-left font-semibold"
                style={{
                  background: 'var(--token-surface-secondary)',
                  borderBottom: '1px solid var(--token-border-light)',
                }}
              >
                {children}
              </th>
            )
          },
          td({ children }) {
            return (
              <td
                className="px-2 py-1.5"
                style={{ borderBottom: '1px solid var(--token-border-extra-light)' }}
              >
                {children}
              </td>
            )
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
