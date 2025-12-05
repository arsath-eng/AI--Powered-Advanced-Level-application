import type { NextAuthConfig } from 'next-auth';
import { JWT } from 'next-auth/jwt'; // <-- Import the JWT type
import Credentials from 'next-auth/providers/credentials';
import { jwtDecode } from 'jwt-decode';

/**
 * Takes a token, and returns a new token with updated
 * `accessToken` and `accessTokenExpires`. If an error occurs,
 * returns the old token and an error property
 */
async function refreshAccessToken(token: JWT): Promise<JWT> { // <-- FIX 1: Use the JWT type instead of 'any'
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/token/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({ refresh_token: token.refreshToken }),
    });

    const refreshedTokens = await response.json();

    if (!response.ok) {
      throw refreshedTokens;
    }

    const newAccessToken = refreshedTokens.access_token;
    const decoded = jwtDecode<{ exp: number }>(newAccessToken);

    return {
      ...token, // Keep the old refresh token
      accessToken: newAccessToken,
      accessTokenExpires: decoded.exp * 1000,
      error: undefined,
    };
  } catch (error) {
    console.error("Error refreshing access token:", error);
    return {
      ...token,
      error: "RefreshAccessTokenError",
    };
  }
}

export const authOptions: NextAuthConfig = {
  providers: [
    Credentials({
      name: 'credentials',
      credentials: {
        accessToken: { label: 'Access Token', type: 'text' },
        refreshToken: { label: 'Refresh Token', type: 'text' },
      },
      async authorize(credentials) {
        if (!credentials?.accessToken || !credentials.refreshToken) {
          return null;
        }
        
        try {
          // --- FIX 2: Explicitly cast credentials to strings ---
          const accessToken = credentials.accessToken as string;
          const refreshToken = credentials.refreshToken as string;

          const decoded = jwtDecode<{ sub: string, exp: number }>(accessToken);
          
          return {
            id: decoded.sub,
            accessToken: accessToken,
            refreshToken: refreshToken,
            expiresIn: decoded.exp * 1000,
          };
        } catch (error) {
          console.error('Auth error during authorize step:', error);
          return null;
        }
      },
    }),
  ],
  session: {
    strategy: 'jwt',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = user.accessToken;
        token.refreshToken = user.refreshToken;
        token.accessTokenExpires = user.expiresIn;
        return token;
      }

      if (Date.now() < token.accessTokenExpires) {
        return token;
      }

      console.log("Access token has expired, attempting to refresh...");
      return refreshAccessToken(token);
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken;
      session.error = token.error;
      return session;
    },
  },
  pages: {
    signIn: '/',
  },
  debug: process.env.NODE_ENV === 'development',
};