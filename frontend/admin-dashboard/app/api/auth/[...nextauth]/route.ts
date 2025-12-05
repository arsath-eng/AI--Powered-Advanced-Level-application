import NextAuth from 'next-auth'
import { authOptions } from '@/lib/auth'

// Destructure the handlers from the NextAuth result
const { handlers: { GET, POST } } = NextAuth(authOptions)

// Export the GET and POST handler functions
export { GET, POST }