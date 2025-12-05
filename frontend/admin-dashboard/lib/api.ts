// frontend/lib/api.ts

// --- START: NEW TYPE-SAFE ERROR DEFINITIONS ---

// Define a specific type for the error information we expect from the backend.
// This replaces the use of `any`.
interface ErrorInfo {
  detail: string;
  [key: string]: unknown; // Allows for other potential properties in a type-safe way
}

// Create a custom error class that extends the built-in Error
export class FetchError extends Error {
  info: ErrorInfo; // Use our new, specific type here instead of `any`
  status: number;

  constructor(message: string, status: number, info: ErrorInfo) {
    // Pass the message to the parent Error class
    super(message);
    
    this.name = 'FetchError';
    this.status = status;
    this.info = info;
  }
}
// --- END: NEW TYPE-SAFE ERROR DEFINITIONS ---

const API_BASE_URL = 'http://localhost:8000';

// A generic fetcher function for use with SWR
export const fetcher = async ([url, token]: [string, string]) => {
  const res = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    let errorInfo: ErrorInfo; // Use our specific type for the variable as well
    try {
      // Try to parse the error response as JSON
      errorInfo = await res.json();
    } catch (e) {
      // If parsing fails, use the status text and conform to the ErrorInfo type
      errorInfo = { detail: res.statusText };
    }
    // Throw our new custom error
    throw new FetchError('An error occurred while fetching the data.', res.status, errorInfo);
  }

  return res.json();
};

// Function to create a new conversation
export const createConversation = async (token: string) => {
    const res = await fetch(`${API_BASE_URL}/conversations/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
        },
    });
    if (!res.ok) throw new Error('Failed to create conversation');
    return res.json();
};

// Function to delete a conversation
export const deleteConversation = async (conversationId: string, token: string) => {
    // FIX: Corrected the typo from API_GPI_BASE_URL to API_BASE_URL
    console.log("Token being sent for deletion:", token);
    const res = await fetch(`${API_BASE_URL}/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
    if (res.status !== 204) throw new Error('Failed to delete conversation');
};