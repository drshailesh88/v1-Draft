'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useRouter } from 'next/navigation'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

interface Paper {
  title: string
  authors: string[]
  year: string
  journal: string
  doi: string
  abstract: string
  source: string
  url: string
}

export default function LiteratureSearchPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [query, setQuery] = useState('')
  const [papers, setPapers] = useState<Paper[]>([])
  const [savedPapers, setSavedPapers] = useState<any[]>([])
  const [searching, setSearching] = useState(false)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

  useEffect(() => {
    if (!loading && !user) router.push('/login')
    else if (user) fetchSavedPapers()
  }, [user, loading, router])

  const fetchSavedPapers = async () => {
    const token = (await supabase.auth.getSession()).data.session?.access_token
    const res = await fetch(`${API_URL}/api/literature/saved-papers?token=${token}`)
    const data = await res.json()
    setSavedPapers(data.papers || [])
  }

  const handleSearch = async () => {
    if (!query.trim()) return
    setSearching(true)
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/literature/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, sources: ['pubmed', 'arxiv', 'semantic_scholar'], max_results: 20, token }),
      })
      if (!res.ok) throw new Error('Search failed')
      const data = await res.json()
      setPapers(data.papers)
    } catch (error: any) {
      alert(error.message)
    } finally {
      setSearching(false)
    }
  }

  const handleSavePaper = async (paper: Paper) => {
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/literature/save-paper?token=${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(paper),
      })
      if (!res.ok) throw new Error('Save failed')
      await fetchSavedPapers()
      alert('Paper saved!')
    } catch (error: any) {
      alert(error.message)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Literature Search</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search PubMed, arXiv, Semantic Scholar..."
                className="flex-1"
              />
              <Button onClick={handleSearch} disabled={searching}>
                {searching ? 'Searching...' : 'Search'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {papers.length > 0 && (
          <Card className="mt-6">
            <CardContent className="pt-6">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Title</TableHead>
                    <TableHead>Authors</TableHead>
                    <TableHead>Year</TableHead>
                    <TableHead>Source</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {papers.map((paper, idx) => (
                    <TableRow key={idx}>
                      <TableCell className="max-w-md">
                        <a href={paper.url} target="_blank" rel="noopener noreferrer" className="hover:underline text-blue-600">
                          {paper.title}
                        </a>
                      </TableCell>
                      <TableCell className="text-sm">{paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 ? '...' : ''}</TableCell>
                      <TableCell>{paper.year}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{paper.source}</Badge>
                      </TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleSavePaper(paper)}
                          disabled={savedPapers.some((p) => p.doi === paper.doi)}
                        >
                          {savedPapers.some((p) => p.doi === paper.doi) ? 'Saved' : 'Save'}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {savedPapers.length > 0 && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Saved Papers ({savedPapers.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {savedPapers.map((paper, idx) => (
                  <div key={idx} className="p-3 bg-gray-50 rounded">
                    <p className="font-medium">{paper.title}</p>
                    <p className="text-sm text-gray-500">{paper.authors?.join(', ')}</p>
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