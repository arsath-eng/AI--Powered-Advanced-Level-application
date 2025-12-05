'use client';

import { useState, useEffect, useRef, FormEvent } from 'react';
import { useParams } from 'next/navigation';
import { useSession } from 'next-auth/react';
import useSWR from 'swr';
import 'katex/dist/katex.min.css';
import { fetcher } from '@/lib/api';
import { Skeleton } from '@/components/ui/skeleton';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { SendIcon } from 'lucide-react';
import { MarkdownRenderer } from '@/components/MarkdownRenderer';
import Image from 'next/image'; // Import the Next.js Image component

// --- FIX: Update the Message interface ---
interface Message {
  role: 'user' | 'model';
  content: string;
  question_image_url?: string | null;
  answer_image_url?: string | null;
  youtube_link?: string | null;
}

interface ConversationData {
  id: string;
  title: string;
  messages: Message[];
}

const getYouTubeVideoId = (url: string): string | null => {
  try {
    const parsed = new URL(url);
    if (parsed.hostname === 'youtu.be' || parsed.hostname === 'www.youtu.be') {
      return parsed.pathname.slice(1).split('?')[0];
    } else if (parsed.hostname === 'www.youtube.com' || parsed.hostname === 'youtube.com' || parsed.hostname === 'm.youtube.com') {
      if (parsed.pathname === '/watch') {
        return parsed.searchParams.get('v');
      } else if (parsed.pathname.startsWith('/embed/')) {
        return parsed.pathname.split('/embed/')[1];
      } else if (parsed.pathname.startsWith('/v/')) {
        return parsed.pathname.split('/v/')[1];
      }
    }
    return null;
  } catch {
    return null;
  }
};

export default function ConversationPage() {
  const params = useParams();
  const conversationId = params.conversationId as string;
  const { data: session } = useSession();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { data: initialData, error } = useSWR<ConversationData>(
    session && conversationId ? [`/conversations/${conversationId}`, session.accessToken] : null,
    fetcher
  );

  useEffect(() => {
    if (initialData && messages.length === 0) {
      setMessages(initialData.messages);
    }
  }, [initialData, messages]);

  useEffect(() => {
    if (!conversationId || !session?.accessToken) return;

    wsRef.current?.close();
    const ws = new WebSocket(`ws://localhost:8000/ws/${conversationId}?token=${session.accessToken}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      const initialPrompt = localStorage.getItem(`initialPrompt_${conversationId}`);
      if (initialPrompt) {
        setMessages(prev => [...prev, { role: 'user', content: initialPrompt }]);
        setIsStreaming(true);
        ws.send(initialPrompt);
        localStorage.removeItem(`initialPrompt_${conversationId}`);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsStreaming(false);
    };

    // --- FIX: Correctly handle both text and metadata messages ---
    ws.onmessage = (event) => {
      const messageChunk = event.data;
      
      if (messageChunk === "[END_OF_STREAM]") {
        setIsStreaming(false);
        return;
      }

      try {
        const parsed = JSON.parse(messageChunk);
        if (parsed.type === "metadata") {
          setMessages(prev => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage?.role === 'model') {
              const updatedLastMessage = { ...lastMessage, ...parsed.data };
              return [...prev.slice(0, -1), updatedLastMessage];
            }
            return prev;
          });
          return;
        }
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      } catch (_e) {
        // Not a JSON message, so it's a text chunk. Continue below.
      }

      setMessages(prev => {
        const lastMessage = prev[prev.length - 1];
        if (lastMessage?.role === 'model') {
          return [
            ...prev.slice(0, -1),
            { ...lastMessage, content: lastMessage.content + messageChunk }
          ];
        } else {
          return [...prev, { role: 'model', content: messageChunk }];
        }
      });
    };

    return () => {
      ws.close();
    };
  }, [conversationId, session]);

  useEffect(() => {
    if (chatContainerRef.current) {
        chatContainerRef.current.scrollTo({
          top: chatContainerRef.current.scrollHeight,
          behavior: 'smooth'
        });
    }
  }, [messages]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN || isStreaming) return;
    
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setIsStreaming(true);
    wsRef.current.send(input);
    setInput('');
    
    if (textareaRef.current) {
      textareaRef.current.style.height = '96px';
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 400)}px`;
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !isStreaming) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  };

  if (error) return (
    <div className="p-4 text-center">
      <div className="text-red-600 dark:text-red-400">
        Failed to load chat. It may have been deleted or you don&apos;t have access.
      </div>
    </div>
  );
  
  if (!initialData) return (
    <div className="p-4 space-y-4">
      <Skeleton className="h-16 w-1/2" />
      <Skeleton className="h-20 w-3/4 self-end" />
      <Skeleton className="h-16 w-1/2" />
    </div>
  );

  return (
    <div className="flex flex-col h-screen bg-background pt-6">
      <div 
        ref={chatContainerRef} 
        className="flex-1 overflow-y-auto conversation-scroll p-6 overflow-x-hidden" 
        style={{ scrollbarWidth: 'thin' }}
      >
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.map((msg, index) => (
            // --- FIX: Wrap message in a flex-col container for proper layout ---
            <div key={index} className={`flex flex-col gap-2 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              
              {/* Message Bubble */}
              <div className={`px-6 py-4 rounded-xl ${msg.role === 'user' ? 'bg-accent text-accent-foreground' : 'bg-transparent text-card-foreground'}`}>
                  <div className="prose prose-slate dark:prose-invert max-w-none">
                    <MarkdownRenderer content={msg.content} />
                  </div>
              </div>

              {/* --- FIX: Add the media rendering logic here --- */}
              {msg.role === 'model' && (
                <div className="space-y-4 mt-2 max-w-2xl w-full">
                  {msg.question_image_url && (
                    <div>
                      <p className="font-semibold text-sm mb-2">Question Image:</p>
                      <Image src={msg.question_image_url} alt="Question visual" className="rounded-lg border w-full h-auto" width={700} height={400} />
                    </div>
                  )}
                  {msg.answer_image_url && (
                    <div>
                      <p className="font-semibold text-sm mb-2">Answer Image:</p>
                      <Image src={msg.answer_image_url} alt="Answer visual" className="rounded-lg border w-full h-auto" width={700} height={400} />
                    </div>
                  )}
                  {msg.youtube_link && (
                    <div>
                      <p className="font-semibold text-sm mb-2">Related Video:</p>
                      <div className="aspect-video relative">
                        {(() => {
                          const videoId = getYouTubeVideoId(msg.youtube_link);
                          if (videoId) {
                            return (
                              <iframe
                                src={`https://www.youtube.com/embed/${videoId}`}
                                title="YouTube video player"
                                frameBorder="0"
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                                className="w-full h-full rounded-lg absolute top-0 left-0"
                              ></iframe>
                            );
                          } else {
                            return <p className="text-red-500">Invalid YouTube URL</p>;
                          }
                        })()}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
          
          {isStreaming && (
            <div className="flex items-start gap-4 justify-start">
              <div className="bg-gray-100 dark:bg-gray-800 px-2 py-3 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <div className="p-4 backdrop-blur-sm sticky bottom-0">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative">
          <div className="relative">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder={`Ask me anything about A/L Physics, Chemistry, or Combined Maths...`}
              className="w-full pr-12 min-h-[96px] max-h-[400px] overflow-y-auto conversation-scroll resize-none border-2 border-gray-500 rounded-lg shadow-sm focus:ring-2 focus:ring-accent focus:border-accent transition bg-input text-foreground"
              disabled={isStreaming}
            />
            <Button
              type="submit"
              variant="ghost"
              size="icon"
              className="absolute right-3 bottom-3 text-accent-foreground hover:text-accent disabled:opacity-50"
              disabled={!input.trim() || isStreaming}
            >
              <SendIcon className="w-5 h-5" />
              <span className="sr-only">Send message</span>
            </Button>
          </div>
          
          {isStreaming && (
            <div className="mt-2 text-sm text-gray-500 text-center">
              12TH.ai Assistant is generating response...
            </div>
          )}
        </form>
      </div>
    </div>
  );
}