// components/chat/chat-home.tsx
'use client'

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { createConversation } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { SendIcon, Compass, Code, BrainCircuit } from 'lucide-react';
import { useSWRConfig } from 'swr';

const sampleQueries = [
  {
    icon: <Compass className="size-5" />,
    title: 'Explain a concept',
    query: 'Explain Doppler effect with a real-world example.',
  },
  {
    icon: <Code className="size-5" />,
    title: 'Solve a problem',
    query: 'Solve the 2019 A/L Physics MCQ question number 5.',
  },
  {
    icon: <BrainCircuit className="size-5" />,
    title: 'Compare theories',
    query: 'Compare and contrast Bohr\'s model and the quantum mechanical model of the atom.',
  },
];

export function ChatHome() {
    const router = useRouter();
    const { data: session } = useSession();
    const [input, setInput] = useState('');
    const { mutate } = useSWRConfig();

    const startConversation = async (prompt: string) => {
        if (!prompt.trim() || !session) return;
        
        try {
            if (!session.accessToken) throw new Error("No access token found in session.");
            const newConversation = await createConversation(session.accessToken);
            
            // Manually update the local SWR cache to show the new chat immediately
            await mutate(['/conversations/', session.accessToken]);

            // Store the initial prompt in localStorage to be picked up by the conversation page
            localStorage.setItem(`initialPrompt_${newConversation.id}`, prompt);

            // Navigate to the new conversation page
            router.push(`/c/${newConversation.id}`);

        } catch (error) {
            console.error("Failed to start new conversation:", error);
        }
    };

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        startConversation(input);
    };

    return (
        <div className="flex flex-col h-full items-center justify-end p-4">
            <div className="max-w-3xl w-full mx-auto flex flex-col items-center flex-1 justify-center">
                <h1 className="text-4xl font-bold text-foreground mb-8">
                    Welcome to <span className="text-primary">12TH.ai</span>
                </h1>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mb-8">
                    {sampleQueries.map((item, index) => (
                        <Card key={index} className="hover:bg-accent transition-colors cursor-pointer" onClick={() => startConversation(item.query)}>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2 text-md">
                                    {item.icon}
                                    {item.title}
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-muted-foreground">{item.query}</p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>

            <div className="w-full max-w-3xl p-4 sticky bottom-0">
                <form onSubmit={handleSubmit} className="relative">
                    <Textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask me anything about A/L Physics, Chemistry, or Combined Maths..."
                        className="w-full pr-12 min-h-[52px] resize-none border rounded-lg shadow-sm"
                    />
                    <Button
                        type="submit"
                        variant="ghost"
                        size="icon"
                        className="absolute right-3 top-1/2 -translate-y-1/2"
                        disabled={!input.trim()}
                    >
                        <SendIcon className="w-5 h-5" />
                    </Button>
                </form>
            </div>
        </div>
    );
}