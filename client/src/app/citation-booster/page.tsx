'use client'

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useRouter } from 'next/navigation'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

interface CitationGap {
  section: string
  position: number
  gap_type: string
  description: string
  suggested_topics: string[]
}

interface SuggestedPaper {
  title: string
  authors: string[]
  year: string
  journal: string
  doi: string
  abstract: string
  source: string
  url: string
  relevance_score: number
  reason: string
}

export default function CitationBoosterPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [text, setText] = useState('')
  const [updatedText, setUpdatedText] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [missingCitations, setMissingCitations] = useState<CitationGap[]>([])
  const [suggestedPapers, setSuggestedPapers] = useState<SuggestedPaper[]>([])
  const [gapAnalysis, setGapAnalysis] = useState('')
  const [selectedGap, setSelectedGap] = useState<CitationGap | null>(null)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

  if (!loading && !user) router.push('/login')
  if (loading) return <div>Loading...</div>

  const handleAnalyze = async () => {
    if (!text.trim()) {
      alert('Please enter text to analyze')
      return
    }
    setAnalyzing(true)
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/citation-booster/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, token }),
      })
      if (!res.ok) throw new Error('Analysis failed')
      const data = await res.json()
      setMissingCitations(data.missing_citations)
      setSuggestedPapers(data.suggested_papers)
      setGapAnalysis(data.gap_analysis)
      setUpdatedText(data.original_text)
    } catch (error: any) {
      alert(error.message)
    } finally {
      setAnalyzing(false)
    }
  }

  const handleAddCitation = async (paper: SuggestedPaper, position?: number) => {
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/citation-booster/add-citation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: updatedText,
          paper,
          position: position ?? 0,
          token,
        }),
      })
      if (!res.ok) throw new Error('Failed to add citation')
      const data = await res.json()
      setUpdatedText(data.updated_text)
      alert(`Citation added: ${data.citation_added}`)
    } catch (error: any) {
      alert(error.message)
    }
  }

  const handleExport = () => {
    const blob = new Blob([updatedText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'boosted-paper.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  const getRelevanceColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-100 text-green-800'
    if (score >= 0.6) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Citation Booster</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste your academic paper text here to analyze citation gaps..."
                className="min-h-[300px]"
              />
              <div className="flex gap-2">
                <Button onClick={handleAnalyze} disabled={analyzing}>
                  {analyzing ? 'Analyzing...' : 'Analyze Citations'}
                </Button>
                {updatedText && (
                  <Button onClick={handleExport} variant="outline">
                    Export Boosted Paper
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {gapAnalysis && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Gap Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700 mb-4">{gapAnalysis}</p>
              <h3 className="font-semibold mb-2">Identified Gaps</h3>
              <div className="space-y-2">
                {missingCitations.map((gap, idx) => (
                  <div
                    key={idx}
                    className="p-4 border rounded hover:bg-gray-50 cursor-pointer"
                    onClick={() => setSelectedGap(gap)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <Badge variant="outline">{gap.section}</Badge>
                      <Badge variant="secondary">{gap.gap_type}</Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{gap.description}</p>
                    <div className="flex gap-1 flex-wrap">
                      {gap.suggested_topics.map((topic, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          {topic}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {suggestedPapers.length > 0 && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Suggested Papers ({suggestedPapers.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Score</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Authors</TableHead>
                    <TableHead>Year</TableHead>
                    <TableHead>Source</TableHead>
                    <TableHead>Reason</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {suggestedPapers.map((paper, idx) => (
                    <TableRow key={idx}>
                      <TableCell>
                        <Badge className={getRelevanceColor(paper.relevance_score)}>
                          {(paper.relevance_score * 100).toFixed(0)}%
                        </Badge>
                      </TableCell>
                      <TableCell className="max-w-md">
                        <a
                          href={paper.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:underline text-blue-600"
                        >
                          {paper.title}
                        </a>
                      </TableCell>
                      <TableCell className="text-sm">
                        {paper.authors.slice(0, 2).join(', ')}
                        {paper.authors.length > 2 ? '...' : ''}
                      </TableCell>
                      <TableCell>{paper.year}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{paper.source}</Badge>
                      </TableCell>
                      <TableCell className="max-w-xs text-sm text-gray-600">
                        {paper.reason}
                      </TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          onClick={() => handleAddCitation(paper, selectedGap?.position)}
                        >
                          Add Citation
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {updatedText && updatedText !== text && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Boosted Paper with Added Citations</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                value={updatedText}
                onChange={(e) => setUpdatedText(e.target.value)}
                className="min-h-[400px]"
              />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
