'use client';

import React, { type ComponentProps } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import 'katex/dist/katex.min.css';
import type { Element } from 'hast';

interface CodeProps extends ComponentProps<'code'> {
  node?: Element;
  inline?: boolean;
}

export const MarkdownRenderer = ({ content }: { content: string }) => {
  return (
    <div className="prose dark:prose-invert max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          // Enhanced code rendering
          code({ node, inline, className, children, ...props }: CodeProps) {
            const match = /language-(\w+)/.exec(className || "");
            const codeString = String(children).replace(/\n$/, "");
            const { ref: _ref, ...rest } = props;

            if (!inline && match) {
              return (
                <div className="my-6 rounded-lg overflow-hidden border border-gray-300 dark:border-gray-600">
                  <div className="bg-gray-100 dark:bg-gray-800 px-4 py-2 flex justify-between items-center text-xs">
                    <span className="font-medium text-gray-600 dark:text-gray-400">{match[1]}</span>
                    <button
                      onClick={() => navigator.clipboard.writeText(codeString)}
                      className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                      aria-label="Copy code"
                    >
                      Copy
                    </button>
                  </div>
                  <SyntaxHighlighter
                    style={vscDarkPlus as unknown as NonNullable<ComponentProps<typeof SyntaxHighlighter>["style"]>}
                    language={match[1]}
                    PreTag="div"
                    className="!m-0"
                  >
                    {codeString}
                  </SyntaxHighlighter>
                </div>
              );
            }

            return !inline ? (
              <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-lg my-4 overflow-x-auto border" {...rest}>
                <code className="text-gray-800 dark:text-gray-200 text-sm">{children}</code>
              </pre>
            ) : (
              <code className="bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 px-2 py-1 rounded text-sm font-mono border" {...rest}>
                {children}
              </code>
            );
          },

          // Enhanced heading rendering with better spacing
          h1: ({ children }) => (
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4 mt-8 pb-2 border-b border-gray-300 dark:border-gray-600">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3 mt-6">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200 mb-3 mt-5">
              {children}
            </h3>
          ),

          // Enhanced paragraph rendering with Tamil support
          p: ({ children }) => (
            <div className="text-base leading-7 text-gray-700 dark:text-gray-300 mb-4 whitespace-pre-wrap">
              {children}
            </div>
          ),

          // Unwrap pre tags to prevent nesting issues with code blocks
          pre: ({ children }) => <>{children}</>,

          // Enhanced list rendering
          ul: ({ children }) => (
            <ul className="list-disc pl-6 mb-4 space-y-2 text-gray-700 dark:text-gray-300">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal pl-6 mb-4 space-y-2 text-gray-700 dark:text-gray-300">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-base leading-6 mb-1">{children}</li>
          ),

          // Enhanced table rendering
          table: ({ children }) => (
            <div className="my-6 overflow-x-auto rounded-lg border border-gray-300 dark:border-gray-600">
              <table className="min-w-full divide-y divide-gray-300 dark:divide-gray-600">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-gray-50 dark:bg-gray-800">{children}</thead>
          ),
          th: ({ children }) => (
            <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100 border-b border-gray-300 dark:border-gray-600">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-gray-700">
              {children}
            </td>
          ),

          // Enhanced blockquote rendering
          blockquote: ({ children }) => (
            <blockquote className="my-6 border-l-4 border-blue-500 pl-4 py-2 bg-blue-50 dark:bg-blue-900/20 rounded-r-lg">
              <div className="text-gray-700 dark:text-gray-300 italic">
                {children}
              </div>
            </blockquote>
          ),

          // Enhanced horizontal rule
          hr: () => (
            <hr className="my-8 border-0 h-px bg-gray-300 dark:bg-gray-600" />
          ),

          // Enhanced emphasis
          strong: ({ children }) => (
            <strong className="font-semibold text-gray-900 dark:text-gray-100">
              {children}
            </strong>
          ),
          em: ({ children }) => (
            <em className="italic text-gray-800 dark:text-gray-200">
              {children}
            </em>
          ),
        }}
      >
        {content}
      </ReactMarkdown>

      {/* Enhanced CSS for KaTeX math rendering */}
      <style jsx global>{`
        /* KaTeX Display Math - Ensure proper centering */
        .katex-display {
          margin: 1.5rem 0 !important;
          text-align: center !important;
          display: block !important;
        }
        
        .katex-display > .katex {
          display: inline-block !important;
          white-space: nowrap;
          text-align: center !important;
        }
        
        /* KaTeX Inline Math */
        .katex {
          font-size: 1.1em !important;
        }
        
        /* Ensure display math container is properly centered */
        .katex-display .katex > .katex-html {
          display: inline-block;
        }
        
        /* Fix for Tamil text with math */
        .prose p {
          line-height: 1.75 !important;
        }
        
        /* Better spacing for mixed Tamil/English content */
        .prose {
          font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Noto Sans Tamil', sans-serif;
        }
        
        /* Ensure math expressions don't break formatting */
        .prose p .katex-display {
          margin: 1rem 0 !important;
        }
        
        /* Better spacing around display math in lists */
        .prose li .katex-display {
          margin: 0.75rem 0 !important;
        }
        
        /* Prevent math expressions from being affected by prose styles */
        .prose .katex * {
          font-family: 'KaTeX_Main', 'Times New Roman', serif !important;
        }
        
        /* Smooth transitions for better streaming experience */
        .prose {
          transition: none;
        }
        
        /* Ensure consistent spacing */
        .prose > * + * {
          margin-top: 1rem;
        }
        
        .prose h3 + * {
          margin-top: 0.75rem;
        }
        
        /* Fix any potential overflow issues with math */
        .katex-display {
          overflow-x: auto;
          overflow-y: hidden;
        }
        
        /* Better mobile handling */
        @media (max-width: 640px) {
          .katex-display {
            font-size: 0.9em;
          }
        }
      `}</style>
    </div>
  );
};