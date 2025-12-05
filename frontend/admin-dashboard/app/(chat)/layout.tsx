// app/(chat)/layout.tsx
'use client';
import React, { useState } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { Sidebar } from '@/components/chat/sidebar';
import { SidebarToggle } from '@/components/chat/sidebar-toggle';
import { cn } from '@/lib/utils';

const ChatLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { status } = useSession();
  const router = useRouter();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  React.useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/');
    }
  }, [status, router]);

  if (status === 'loading') {
    return <div className="flex h-screen items-center justify-center">Loading session...</div>;
  }

  if (status === 'unauthenticated') {
    return null;
  }

  return (
    <div className="h-screen bg-background overflow-hidden">
      {/* 1. Backdrop for mobile overlay (hidden on large screens) */}
      <div
        onClick={() => setIsSidebarOpen(false)}
        className={cn(
          'fixed inset-0 z-20 bg-black/50 transition-opacity lg:hidden',
          isSidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        )}
      />

      {/* 2. Sidebar container with responsive slide-in/out */}
      <div
        className={cn(
          'fixed top-0 left-0 h-full z-30 w-64 transition-transform duration-300 ease-in-out',
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <Sidebar />
      </div>

      {/* 3. Sidebar toggle button fixed in top-left corner */}
      <div className="fixed top-2 left-2 z-40">
        <SidebarToggle isOpen={isSidebarOpen} setIsOpen={setIsSidebarOpen} />
      </div>

      {/* 4. Main content with responsive margin */}
      <main
        className={cn(
          'h-full w-full flex-1 flex flex-col overflow-hidden relative transition-all duration-300 ease-in-out',
          isSidebarOpen ? 'lg:ml-[85px]' : 'ml-0' // Shift by ~1/3 of sidebar width (256px / 3 ≈ 85px)
        )}
      >
        {children}
      </main>
    </div>
  );
};

export default ChatLayout;