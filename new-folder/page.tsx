"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2 } from "lucide-react"

export default function HomePage() {
  const [youtubeUrl, setYoutubeUrl] = useState("")
  const [transcript, setTranscript] = useState("")
  const [error, setError] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleTranscribe = async () => {
    setError("")
    setTranscript("")
    setIsLoading(true)

    // IMPORTANT: Replace 'YOUR_BACKEND_API_URL' with your actual deployed Python API URL
    const apiUrl = "YOUR_BACKEND_API_URL/api/yt-to-text"

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: youtubeUrl }),
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.error || "An unknown error occurred.")
        setTranscript("")
      } else {
        setTranscript(data.text)
        setError("")
      }
    } catch (err) {
      console.error("Fetch error:", err)
      setError("Could not connect to the API. Please check the URL and your network connection.")
      setTranscript("")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4 dark:bg-gray-950">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="text-center text-2xl">YouTube Video Transcriber</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="youtube-url" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              YouTube Video URL
            </label>
            <Input
              id="youtube-url"
              type="url"
              placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              className="w-full"
            />
          </div>
          <Button onClick={handleTranscribe} disabled={isLoading || !youtubeUrl} className="w-full">
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Transcribing...
              </>
            ) : (
              "Get Transcript"
            )}
          </Button>

          {error && (
            <div className="mt-4 text-red-500 text-center">
              <p>Error: {error}</p>
            </div>
          )}

          {transcript && (
            <div className="space-y-2">
              <h3 className="text-lg font-medium">Transcription:</h3>
              <Textarea
                readOnly
                value={transcript}
                rows={10}
                className="w-full resize-y"
                aria-label="Video Transcription"
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
