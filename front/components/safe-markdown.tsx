"use client"

import ReactMarkdown from 'react-markdown'
import rehypeSanitize, { defaultSchema } from 'rehype-sanitize'
import type { ReactNode } from 'react'

const schema = {
  ...defaultSchema,
  attributes: {
    ...defaultSchema.attributes,
    code: [...(defaultSchema.attributes?.code ?? []), "className"],
  },
}

type SafeMarkdownProps = {
  children: string
  className?: string
}

/**
 * Renders markdown with rehype-sanitize (no raw HTML / limited tag surface).
 */
export function SafeMarkdown({ children, className }: SafeMarkdownProps): ReactNode {
  return (
    <div className={className}>
      <ReactMarkdown rehypePlugins={[[rehypeSanitize, schema]]}>{children}</ReactMarkdown>
    </div>
  )
}
