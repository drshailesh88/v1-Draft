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
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

interface SystematicReview {
  id: string
  research_question: string
  databases: string[]
  search_terms: string
  inclusion_criteria: string
  exclusion_criteria: string
  screening_counts: any
  created_at: string
}

interface ScreeningRecord {
  id: string
  paper_id: string
  title: string
  authors: string[]
  year: string
  doi: string
  status: string
  reason: string
  stage: string
}

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

export default function SystematicReviewPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [reviews, setReviews] = useState<SystematicReview[]>([])
  const [selectedReview, setSelectedReview] = useState<SystematicReview | null>(null)
  const [papers, setPapers] = useState<Paper[]>([])
  const [screeningRecords, setScreeningRecords] = useState<ScreeningRecord[]>([])
  const [prismaSvg, setPrismaSvg] = useState<string>('')
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showSearchDialog, setShowSearchDialog] = useState(false)
  const [showScreeningDialog, setShowScreeningDialog] = useState(false)
  const [showPrismaDialog, setShowPrismaDialog] = useState(false)
  const [showExportDialog, setShowExportDialog] = useState(false)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

  const [reviewForm, setReviewForm] = useState({
    research_question: '',
    databases: ['pubmed', 'arxiv', 'semantic_scholar'],
    search_terms: '',
    inclusion_criteria: '',
    exclusion_criteria: ''
  })

  const [searchQuery, setSearchQuery] = useState('')
  const [screeningDecision, setScreeningDecision] = useState({
    paper_id: '',
    title: '',
    authors: [] as string[],
    year: '',
    doi: '',
    status: 'included',
    reason: '',
    stage: 'screening'
  })

  const [exportContent, setExportContent] = useState('')
  const [exportFormat, setExportFormat] = useState('csv')

  useEffect(() => {
    if (!loading && !user) router.push('/login')
    else if (user) fetchReviews()
  }, [user, loading, router])

  const fetchReviews = async () => {
    const token = (await supabase.auth.getSession()).data.session?.access_token
    const res = await fetch(`${API_URL}/api/systematic-review/user-reviews?token=${token}`)
    const data = await res.json()
    setReviews(data.reviews || [])
  }

  const fetchReviewDetails = async (reviewId: string) => {
    const token = (await supabase.auth.getSession()).data.session?.access_token
    const res = await fetch(`${API_URL}/api/systematic-review/review/${reviewId}?token=${token}`)
    const data = await res.json()
    setSelectedReview(data.review)
    setScreeningRecords(data.screening_records || [])
  }

  const handleCreateReview = async () => {
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/systematic-review/create-review?token=${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reviewForm),
      })
      if (!res.ok) throw new Error('Failed to create review')
      await fetchReviews()
      setShowCreateDialog(false)
      setReviewForm({
        research_question: '',
        databases: ['pubmed', 'arxiv', 'semantic_scholar'],
        search_terms: '',
        inclusion_criteria: '',
        exclusion_criteria: ''
      })
      alert('Review created successfully!')
    } catch (error: any) {
      alert(error.message)
    }
  }

  const handleSearchPapers = async () => {
    if (!selectedReview || !searchQuery.trim()) return
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const sources = selectedReview.databases.join(',')
      const res = await fetch(`${API_URL}/api/systematic-review/search-literature?query=${encodeURIComponent(searchQuery)}&sources=${sources}&max_results=50&token=${token}`)
      if (!res.ok) throw new Error('Search failed')
      const data = await res.json()
      setPapers(data.papers)
      setShowSearchDialog(true)
    } catch (error: any) {
      alert(error.message)
    }
  }

  const handleScreening = async () => {
    if (!selectedReview) return
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/systematic-review/record-screening?token=${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          review_id: selectedReview.id,
          ...screeningDecision
        }),
      })
      if (!res.ok) throw new Error('Screening failed')
      await fetchReviewDetails(selectedReview.id)
      setShowScreeningDialog(false)
      alert('Screening recorded successfully!')
    } catch (error: any) {
      alert(error.message)
    }
  }

  const handleGeneratePrisma = async () => {
    if (!selectedReview) return
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/systematic-review/generate-prisma-diagram?review_id=${selectedReview.id}&token=${token}`, {
        method: 'POST',
      })
      if (!res.ok) throw new Error('Failed to generate PRISMA diagram')
      const data = await res.json()
      setPrismaSvg(data.svg)
      setShowPrismaDialog(true)
    } catch (error: any) {
      alert(error.message)
    }
  }

  const handleExport = async (format: string) => {
    if (!selectedReview) return
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/systematic-review/export/${selectedReview.id}?format=${format}&token=${token}`)
      if (!res.ok) throw new Error('Export failed')
      const data = await res.json()
      setExportContent(data.content)
      setExportFormat(format)
      setShowExportDialog(true)
    } catch (error: any) {
      alert(error.message)
    }
  }

  const downloadExport = () => {
    const blob = new Blob([exportContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `systematic_review_${selectedReview?.id}.${exportFormat === 'csv' ? 'csv' : exportFormat === 'bibtex' ? 'bib' : 'svg'}`
    a.click()
    URL.revokeObjectURL(url)
  }

  const initiateScreening = (paper: Paper, stage: string = 'screening') => {
    setScreeningDecision({
      paper_id: paper.doi || paper.title,
      title: paper.title,
      authors: paper.authors,
      year: paper.year,
      doi: paper.doi || '',
      status: 'included',
      reason: '',
      stage
    })
    setShowScreeningDialog(true)
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Systematic Literature Review</h1>
          <Button onClick={() => setShowCreateDialog(true)}>Create New Review</Button>
        </div>

        {!selectedReview ? (
          <div className="grid gap-4">
            {reviews.map((review) => (
              <Card key={review.id} className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => fetchReviewDetails(review.id)}>
                <CardHeader>
                  <CardTitle>{review.research_question}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <p><strong>Databases:</strong> {review.databases.join(', ')}</p>
                    <p><strong>Created:</strong> {new Date(review.created_at).toLocaleDateString()}</p>
                    <div className="flex gap-2 flex-wrap">
                      <Badge>Identified: {review.screening_counts?.identification || 0}</Badge>
                      <Badge>Screened: {review.screening_counts?.screening || 0}</Badge>
                      <Badge>Included: {review.screening_counts?.included || 0}</Badge>
                      <Badge variant="destructive">Excluded: {review.screening_counts?.excluded || 0}</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            {reviews.length === 0 && (
              <Card>
                <CardContent className="pt-6 text-center">
                  <p className="text-gray-500">No systematic reviews yet. Create your first review to get started!</p>
                </CardContent>
              </Card>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex gap-4 items-start">
              <Button variant="outline" onClick={() => { setSelectedReview(null); setPapers([]); setScreeningRecords([]) }}>
                ← Back to Reviews
              </Button>
              <div className="flex-1">
                <Card>
                  <CardHeader>
                    <CardTitle>{selectedReview.research_question}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="font-semibold">Search Terms</Label>
                        <p className="text-sm text-gray-600 mt-1">{selectedReview.search_terms}</p>
                      </div>
                      <div>
                        <Label className="font-semibold">Databases</Label>
                        <div className="flex gap-2 mt-1 flex-wrap">
                          {selectedReview.databases.map((db) => (
                            <Badge key={db} variant="outline">{db}</Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <Label className="font-semibold">Inclusion Criteria</Label>
                        <p className="text-sm text-gray-600 mt-1">{selectedReview.inclusion_criteria}</p>
                      </div>
                      <div>
                        <Label className="font-semibold">Exclusion Criteria</Label>
                        <p className="text-sm text-gray-600 mt-1">{selectedReview.exclusion_criteria}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>

            <div className="flex gap-2">
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearchPapers()}
                placeholder="Search literature for this review..."
                className="flex-1"
              />
              <Button onClick={handleSearchPapers}>Search</Button>
              <Button onClick={handleGeneratePrisma} variant="outline">PRISMA Diagram</Button>
              <Button onClick={() => setShowExportDialog(true)} variant="outline">Export</Button>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Screening Progress</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-4 bg-blue-50 rounded">
                      <p className="text-3xl font-bold text-blue-600">{selectedReview.screening_counts?.identification || 0}</p>
                      <p className="text-sm text-gray-600">Identified</p>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded">
                      <p className="text-3xl font-bold text-green-600">{selectedReview.screening_counts?.screening || 0}</p>
                      <p className="text-sm text-gray-600">Screened</p>
                    </div>
                    <div className="text-center p-4 bg-purple-50 rounded">
                      <p className="text-3xl font-bold text-purple-600">{selectedReview.screening_counts?.included || 0}</p>
                      <p className="text-sm text-gray-600">Included</p>
                    </div>
                    <div className="text-center p-4 bg-red-50 rounded">
                      <p className="text-3xl font-bold text-red-600">{selectedReview.screening_counts?.excluded || 0}</p>
                      <p className="text-sm text-gray-600">Excluded</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <p className="text-sm text-gray-600">
                      1. Search for papers using the search bar above
                    </p>
                    <p className="text-sm text-gray-600">
                      2. Review each paper and decide to include or exclude
                    </p>
                    <p className="text-sm text-gray-600">
                      3. Track progress with screening counts
                    </p>
                    <p className="text-sm text-gray-600">
                      4. Generate PRISMA diagram when complete
                    </p>
                    <p className="text-sm text-gray-600">
                      5. Export data for your manuscript
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {screeningRecords.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Screening Records ({screeningRecords.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Title</TableHead>
                        <TableHead>Stage</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Reason</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {screeningRecords.map((record) => (
                        <TableRow key={record.id}>
                          <TableCell className="max-w-md">
                            <p className="font-medium">{record.title}</p>
                            <p className="text-xs text-gray-500">{record.authors?.slice(0, 2).join(', ')} ({record.year})</p>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{record.stage}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={record.status === 'included' ? 'default' : 'destructive'}>
                              {record.status}
                            </Badge>
                          </TableCell>
                          <TableCell className="max-w-xs truncate">{record.reason || '-'}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>

      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Systematic Review</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="research_question">Research Question *</Label>
              <Input
                id="research_question"
                value={reviewForm.research_question}
                onChange={(e) => setReviewForm({ ...reviewForm, research_question: e.target.value })}
                placeholder="e.g., What is the effectiveness of mindfulness-based interventions for anxiety?"
              />
            </div>
            <div>
              <Label htmlFor="search_terms">Search Terms *</Label>
              <Textarea
                id="search_terms"
                value={reviewForm.search_terms}
                onChange={(e) => setReviewForm({ ...reviewForm, search_terms: e.target.value })}
                placeholder="Enter keywords and search strings..."
              />
            </div>
            <div>
              <Label htmlFor="inclusion_criteria">Inclusion Criteria *</Label>
              <Textarea
                id="inclusion_criteria"
                value={reviewForm.inclusion_criteria}
                onChange={(e) => setReviewForm({ ...reviewForm, inclusion_criteria: e.target.value })}
                placeholder="Define what makes a study eligible for inclusion..."
              />
            </div>
            <div>
              <Label htmlFor="exclusion_criteria">Exclusion Criteria *</Label>
              <Textarea
                id="exclusion_criteria"
                value={reviewForm.exclusion_criteria}
                onChange={(e) => setReviewForm({ ...reviewForm, exclusion_criteria: e.target.value })}
                placeholder="Define what makes a study ineligible..."
              />
            </div>
            <Button onClick={handleCreateReview} className="w-full">Create Review</Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showSearchDialog} onOpenChange={setShowSearchDialog}>
        <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Search Results ({papers.length})</DialogTitle>
          </DialogHeader>
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
                    <Button size="sm" onClick={() => initiateScreening(paper, 'identification')}>
                      Screen
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </DialogContent>
      </Dialog>

      <Dialog open={showScreeningDialog} onOpenChange={setShowScreeningDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Screen Paper</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">{screeningDecision.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">{screeningDecision.authors.join(', ')} ({screeningDecision.year})</p>
                <p className="text-sm text-gray-600 mt-1">DOI: {screeningDecision.doi || 'N/A'}</p>
              </CardContent>
            </Card>
            <div>
              <Label>Stage</Label>
              <select
                value={screeningDecision.stage}
                onChange={(e) => setScreeningDecision({ ...screeningDecision, stage: e.target.value })}
                className="w-full p-2 border rounded"
              >
                <option value="identification">Identification</option>
                <option value="screening">Screening</option>
                <option value="eligibility">Eligibility</option>
              </select>
            </div>
            <div>
              <Label>Decision *</Label>
              <div className="flex gap-4 mt-2">
                <Button
                  type="button"
                  variant={screeningDecision.status === 'included' ? 'default' : 'outline'}
                  onClick={() => setScreeningDecision({ ...screeningDecision, status: 'included' })}
                  className="flex-1"
                >
                  Include
                </Button>
                <Button
                  type="button"
                  variant={screeningDecision.status === 'excluded' ? 'destructive' : 'outline'}
                  onClick={() => setScreeningDecision({ ...screeningDecision, status: 'excluded' })}
                  className="flex-1"
                >
                  Exclude
                </Button>
              </div>
            </div>
            <div>
              <Label htmlFor="reason">Reason (for exclusion)</Label>
              <Textarea
                id="reason"
                value={screeningDecision.reason}
                onChange={(e) => setScreeningDecision({ ...screeningDecision, reason: e.target.value })}
                placeholder="Why exclude this paper?"
              />
            </div>
            <Button onClick={handleScreening} className="w-full">Record Decision</Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showPrismaDialog} onOpenChange={setShowPrismaDialog}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>PRISMA Flow Diagram</DialogTitle>
          </DialogHeader>
          <div className="flex justify-center">
            <div dangerouslySetInnerHTML={{ __html: prismaSvg }} />
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showExportDialog} onOpenChange={setShowExportDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Export Review</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Select Export Format</Label>
              <div className="flex gap-4 mt-2">
                <Button variant="outline" onClick={() => handleExport('csv')}>CSV</Button>
                <Button variant="outline" onClick={() => handleExport('bibtex')}>BibTeX</Button>
                <Button variant="outline" onClick={() => handleExport('prisma')}>PRISMA SVG</Button>
              </div>
            </div>
            {exportContent && (
              <>
                <div className="max-h-[300px] overflow-y-auto bg-gray-50 p-4 rounded">
                  <pre className="text-xs">{exportContent}</pre>
                </div>
                <Button onClick={downloadExport} className="w-full">Download</Button>
              </>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
