'use client'

import { useState, useRef } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useRouter } from 'next/navigation'

interface DetectionResult {
  ai_probability: number
  human_probability: number
  verdict: string
  confidence: number
  highlighted_sections: any[]
}

export default function AIDetectorPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [text, setText] = useState('')
  const [result, setResult] = useState<DetectionResult | null>(null)
  const [detecting, setDetecting] = useState(false)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

  if (loading && !user) {
    router.push('/login')
    return null
  }

  const handleDetectText = async () => {
    if (!text.trim()) return
    setDetecting(true)
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/ai-detector/detect-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, token }),
      })
      if (!res.ok) throw new Error('Detection failed')
      const data = await res.json()
      setResult(data.result)
    } catch (error: any) {
      alert(error.message)
    } finally {
      setDetecting(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setDetecting(true)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('token', (await supabase.auth.getSession()).data.session?.access_token || '')

    try {
      const res = await fetch(`${API_URL}/api/ai-detector/detect-file`, {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) throw new Error('Detection failed')
      const data = await res.json()
      setResult(data.result)
      const fileText = await file.text()
      setText(fileText)
    } catch (error: any) {
      alert(error.message)
    } finally {
      setDetecting(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const getVerdictColor = (verdict: string) => {
    if (verdict.includes('Likely AI-generated')) return 'bg-red-500'
    if (verdict.includes('Possibly AI-generated')) return 'bg-orange-500'
    if (verdict.includes('Possibly human-written')) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>AI Content Detector</CardTitle>
          </CardHeader>
          <CardContent>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".txt,.md"
              className="hidden"
            />
            <div className="space-y-4">
              <div>
                <Button onClick={() => fileInputRef.current?.click()} variant="outline" className="mb-2">
                  Upload File
                </Button>
              </div>
              <div>
                <label className="block mb-2">Or paste text</label>
                <Textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Paste your text here to check for AI-generated content..."
                  className="min-h-[200px]"
                />
              </div>
              <Button onClick={handleDetectText} disabled={detecting || !text.trim()}>
                {detecting ? 'Analyzing...' : 'Detect AI Content'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {result && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Detection Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex justify-center">
                  <Badge className={`text-white px-6 py-3 text-lg ${getVerdictColor(result.verdict)}`}>
                    {result.verdict}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardContent className="pt-6">
                      <p className="text-sm text-gray-500 mb-2">AI Probability</p>
                      <p className="text-3xl font-bold text-red-600">{result.ai_probability}%</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="pt-6">
                      <p className="text-sm text-gray-500 mb-2">Human Probability</p>
                      <p className="text-3xl font-bold text-green-600">{result.human_probability}%</p>
                    </CardContent>
                  </Card>
                </div>

                <div>
                  <p className="text-sm text-gray-500">Confidence: {result.confidence}%</p>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${result.confidence}%` }}
                    />
                  </div>
                </div>

                {result.highlighted_sections.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-2">Highlighted Sections</h3>
                    <div className="space-y-2">
                      {result.highlighted_sections.map((section, idx) => (
                        <div
                          key={idx}
                          className={`p-3 rounded ${
                            section.type === 'high_ai_probability' ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'
                          }`}
                        >
                          <p className="text-sm">{text.substring(section.start, section.end)}</p>
                          <p className="text-xs mt-1">Score: {section.score}%</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}