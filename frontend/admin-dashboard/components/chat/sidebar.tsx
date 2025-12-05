'use client';

import { useSession, signOut } from 'next-auth/react';
import useSWR, { useSWRConfig } from 'swr';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { fetcher, createConversation, deleteConversation } from '@/lib/api';
import { PlusIcon, TrashIcon, LogOutIcon, MessageSquare, SettingsIcon } from 'lucide-react';
import { useState, useEffect } from 'react';

interface Conversation {
  id: string;
  title: string;
}

export function Sidebar() {
  const { data: session } = useSession();
  const router = useRouter();
  const pathname = usePathname();
  const { mutate } = useSWRConfig();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');

  const { data: conversations, error } = useSWR<Conversation[]>(
    session ? ['/conversations/', session.accessToken] : null,
    fetcher
  );

  const handleNewChat = async () => {
    if (!session?.accessToken) return;
    try {
      const newConversation = await createConversation(session.accessToken);
      await mutate(['/conversations/', session.accessToken]);
      router.push(`/c/${newConversation.id}`);
    } catch (err) {
      console.error('Error creating new chat:', err);
    }
  };

  const handleDelete = async (e: React.MouseEvent, conversationId: string) => {
    e.stopPropagation();
    if (!session?.accessToken || !window.confirm("Are you sure you want to delete this chat?")) return;
    try {
      await deleteConversation(conversationId, session.accessToken);
      await mutate(['/conversations/', session.accessToken]);
      if (pathname.includes(conversationId)) {
        router.push('/chat');
      }
    } catch (err) {
      console.error('Error deleting chat:', err);
    }
  };

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme);
    if (newTheme === 'system') {
      const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.classList.toggle('dark', isDarkMode);
    } else {
      document.documentElement.classList.toggle('dark', newTheme === 'dark');
    }
    setIsSettingsOpen(false);
  };

  // Sync theme with system preference on mount
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      if (theme === 'system') {
        document.documentElement.classList.toggle('dark', mediaQuery.matches);
      }
    };
    handleChange(); // Initial check
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  return (
    <div className="flex flex-col h-full w-64 bg-sidebar text-card-foreground p-2">
      <div className="flex items-center ml-12">
        <button
          onClick={handleNewChat}
          className="flex items-center justify-center mb-4  w-full bg-secondary hover:bg-secondary/80 text-secondary-foreground font-semibold py-2 px-4 rounded-md transition-colors"
        >
          <PlusIcon className="w-4 h-4 mr-2" />
          New Chat
        </button>
      </div>
      <nav className=" flex-1 overflow-y-auto space-y-1 conversation-scroll" style={{ scrollbarWidth: 'thin' }}>
        {error && <div className="text-destructive p-2">Failed to load</div>}
        {!conversations && !error && <div className="text-muted-foreground p-2">Loading...</div>}
        {conversations?.map((conv) => (
          <div key={conv.id} className="group relative">
            <Link
              href={`/c/${conv.id}`}
              className={`flex items-center space-x-2 w-full text-left p-2 rounded-md transition-colors ${pathname.includes(conv.id) ? 'bg-secondary' : 'hover:bg-secondary/50'}`}
            >
              <MessageSquare className="h-4 w-4 flex-shrink-0" />
              <span className="truncate flex-1">{conv.title}</span>
            </Link>
            <button
              onClick={(e) => handleDelete(e, conv.id)}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-muted-foreground hover:text-foreground opacity-0 group-hover:opacity-100 focus:opacity-100 transition-opacity"
            >
              <TrashIcon className="w-4 h-4" />
            </button>
          </div>
        ))}
      </nav>
      <div className="mt-auto pt-2 border-t border-border">
        <button
          onClick={() => setIsSettingsOpen(!isSettingsOpen)}
          className="flex items-center w-full text-left p-2 rounded-md hover:bg-secondary/50 transition-colors mb-2"
        >
          <SettingsIcon className="w-4 h-4 mr-2" />
          Settings
        </button>
        {isSettingsOpen && (
          <div className="bg-card p-2 rounded-md">
            <button
              onClick={() => handleThemeChange('light')}
              className="w-full text-left p-1 hover:bg-secondary/50 rounded-md text-foreground"
            >
              Light
            </button>
            <button
              onClick={() => handleThemeChange('dark')}
              className="w-full text-left p-1 hover:bg-secondary/50 rounded-md text-foreground"
            >
              Dark
            </button>
            <button
              onClick={() => handleThemeChange('system')}
              className="w-full text-left p-1 hover:bg-secondary/50 rounded-md text-foreground"
            >
              System
            </button>
          </div>
        )}
        <button
          onClick={() => signOut({ callbackUrl: '/' })}
          className="flex items-center w-full text-left p-2 rounded-md hover:bg-secondary/50 transition-colors"
        >
          <LogOutIcon className="w-4 h-4 mr-2" />
          Sign Out
        </button>
      </div>
    </div>
  );
}