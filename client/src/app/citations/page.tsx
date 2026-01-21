'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useRouter } from 'next/navigation'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

interface Citation {
  formatted: string
  bibtex: string
}

export default function CitationGeneratorPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [doi, setDoi] = useState('')
  const [style, setStyle] = useState('APA')
  const [citations, setCitations] = useState<Citation[]>([])
  const [generating, setGenerating] = useState(false)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

  useEffect(() => {
    if (!loading && !user) router.push('/login')
  }, [user, loading, router])

  const handleGenerate = async () => {
    if (!doi.trim()) return
    setGenerating(true)
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/citations/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ metadata: { doi }, style, token }),
      })
      if (!res.ok) throw new Error('Generation failed')
      const data = await res.json()
      setCitations([data, ...citations])
      setDoi('')
    } catch (error: any) {
      alert(error.message)
    } finally {
      setGenerating(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Citation Generator</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Input
                value={doi}
                onChange={(e) => setDoi(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
                placeholder="Enter DOI (e.g., 10.1000/182)"
                className="flex-1"
              />
              <Select value={style} onValueChange={setStyle}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="APA">APA</SelectItem>
                  <SelectItem value="MLA">MLA</SelectItem>
                  <SelectItem value="Chicago">Chicago</SelectItem>
                  <SelectItem value="IEEE">IEEE</SelectItem>
                  <SelectItem value="Harvard">Harvard</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={handleGenerate} disabled={generating}>
                {generating ? 'Generating...' : 'Generate'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {citations.length > 0 && (
          <Card className="mt-6">
            <CardContent className="pt-6">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Formatted Citation</TableHead>
                    <TableHead>BibTeX</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {citations.map((citation, idx) => (
                    <TableRow key={idx}>
                      <TableCell className="max-w-md">{citation.formatted}</TableCell>
                      <TableCell className="max-w-md font-mono text-sm">{citation.bibtex}</TableCell>
                      <TableCell>
                        <Button size="sm" variant="outline" onClick={() => copyToClipboard(citation.formatted)}>
                          Copy
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}