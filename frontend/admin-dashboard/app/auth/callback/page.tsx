'use client'

import { useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { signIn } from 'next-auth/react'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export default function CallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const accessToken = searchParams.get('access_token')
  const refreshToken = searchParams.get('refresh_token')

  useEffect(() => {
    if (accessToken && refreshToken) {
      signIn('credentials', { 
        accessToken: accessToken,
        refreshToken: refreshToken, // <-- Pass the refresh token
        redirect: false 
      }).then((result) => {
    // --- END: MODIFICATION ---
        if (result?.ok) {
          router.push('/chat')
        } else {
          router.push('/?error=authentication_failed')
        }
      }).catch(() => {
        router.push('/?error=authentication_failed')
      })
    } else {
      router.push('/?error=no_token')
    }
  }, [accessToken, refreshToken, router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardContent className="p-6 space-y-4">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-2">Signing you in...</h2>
            <p className="text-gray-600 mb-4">Please wait while we complete your authentication.</p>
          </div>
          <div className="space-y-3">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}