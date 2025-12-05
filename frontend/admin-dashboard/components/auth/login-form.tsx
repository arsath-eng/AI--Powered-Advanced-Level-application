'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { GoogleSignInButton } from '@/components/ui/google-sign-in-button'

export function LoginForm() {
  const [loading, setLoading] = useState(false)

  const handleGoogleSignIn = () => {
    setLoading(true)
    // Redirect to FastAPI backend for Google OAuth
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/auth/google`
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <CardTitle className="text-3xl font-bold">Welcome to 12TH.ai</CardTitle>
          <CardDescription className="text-gray-600">
            Sign in to start your AI conversation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <GoogleSignInButton 
            onClick={handleGoogleSignIn}
            loading={loading}
          />
          <div className="text-center text-sm text-gray-500">
            By continuing, you agree to our Terms of Service and Privacy Policy.
          </div>
        </CardContent>
      </Card>
    </div>
  )
}