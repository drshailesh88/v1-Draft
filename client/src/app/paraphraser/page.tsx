'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { useRouter } from 'next/navigation'
import { Copy, RefreshCw, Sparkles } from 'lucide-react'

interface VocabularyEnhancement {
  original: string
  suggestion: string
  position: number[]
}

export default function ParaphraserPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [originalText, setOriginalText] = useState('')
  const [paraphrasedText, setParaphrasedText] = useState('')
  const [intensity, setIntensity] = useState('medium')
  const [vocabularyEnhancements, setVocabularyEnhancements] = useState<VocabularyEnhancement[]>([])
  const [paraphrasing, setParaphrasing] = useState(false)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

  useEffect(() => {
    if (!loading && !user) router.push('/login')
  }, [user, loading, router])

  const handleParaphrase = async () => {
    if (!originalText.trim()) return
    setParaphrasing(true)
    setParaphrasedText('')
    setVocabularyEnhancements([])
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/paraphraser/paraphrase`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ text: originalText, intensity }),
      })
      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.detail || 'Paraphrasing failed')
      }
      const data = await res.json()
      setParaphrasedText(data.paraphrased)
      setVocabularyEnhancements(data.vocabulary_enhancements || [])
    } catch (error: any) {
      alert(error.message)
    } finally {
      setParaphrasing(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  }

  const handleIntensityChange = (value: string) => {
    setIntensity(value)
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              Academic Paraphraser
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="intensity">Paraphrase Intensity</Label>
                <RadioGroup 
                  value={intensity} 
                  onValueChange={handleIntensityChange}
                  className="flex gap-6 mt-2"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="light" id="light" />
                    <Label htmlFor="light" className="font-normal cursor-pointer">
                      Light
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="medium" id="medium" />
                    <Label htmlFor="medium" className="font-normal cursor-pointer">
                      Medium
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="strong" id="strong" />
                    <Label htmlFor="strong" className="font-normal cursor-pointer">
                      Strong
                    </Label>
                  </div>
                </RadioGroup>
                <p className="text-sm text-muted-foreground mt-2">
                  {intensity === 'light' && 'Minimal surface changes to improve flow and readability.'}
                  {intensity === 'medium' && 'Moderate changes with improved clarity and style.'}
                  {intensity === 'strong' && 'Significant rephrasing with different wording and structure.'}
                </p>
              </div>

              <div>
                <Label htmlFor="original">Original Text</Label>
                <Textarea
                  id="original"
                  value={originalText}
                  onChange={(e) => setOriginalText(e.target.value)}
                  placeholder="Paste your academic text here..."
                  className="min-h-[200px] mt-2"
                />
              </div>

              <Button 
                onClick={handleParaphrase} 
                disabled={paraphrasing || !originalText.trim()}
                className="w-full"
              >
                {paraphrasing ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Paraphrasing...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Paraphrase
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {paraphrasedText && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Original Text</CardTitle>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => copyToClipboard(originalText)}
                  >
                    <Copy className="h-4 w-4 mr-1" />
                    Copy
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  {originalText}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Paraphrased Text</CardTitle>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => copyToClipboard(paraphrasedText)}
                  >
                    <Copy className="h-4 w-4 mr-1" />
                    Copy
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  {paraphrasedText}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {vocabularyEnhancements.length > 0 && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                Vocabulary Enhancements
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {vocabularyEnhancements.map((enhancement, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                    <Badge variant="secondary" className="mt-0.5">
                      {idx + 1}
                    </Badge>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-red-600 line-through">
                          {enhancement.original}
                        </span>
                        <span className="text-muted-foreground">→</span>
                        <span className="font-medium text-green-600">
                          {enhancement.suggestion}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Consider using "{enhancement.suggestion}" for more precise academic expression
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
