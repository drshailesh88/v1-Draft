'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { useRouter } from 'next/navigation'

interface Rating {
  score: number
  explanation: string
  strengths: string[]
  weaknesses: string[]
}

interface SimilarityResult {
  paper_title: string
  similarity_score: number
  common_themes: string[]
  methodological_differences: string[]
}

interface AnalyzeResponse {
  review_id: string
  overall_rating: Rating
  methods_critique: any
  results_critique: any
  discussion_critique: any
  suggestions: string[]
  similarity_analysis: SimilarityResult[]
  agent_tasks: Record<string, any>
}

interface Review {
  id: string
  paper_title: string
  overall_rating: Rating
  created_at: string
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

export default function DeepReviewPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [reviews, setReviews] = useState<Review[]>([])
  const [selectedReview, setSelectedReview] = useState<AnalyzeResponse | null>(null)
  const [savedPapers, setSavedPapers] = useState<Paper[]>([])
  const [showAnalyzeDialog, setShowAnalyzeDialog] = useState(false)
  const [showComparisonDialog, setShowComparisonDialog] = useState(false)
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [exportContent, setExportContent] = useState('')
  const [exportFormat, setExportFormat] = useState('markdown')
  const [analyzing, setAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)
  const [currentAgent, setCurrentAgent] = useState('')
  const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

  const [paperForm, setPaperForm] = useState({
    title: '',
    content: '',
    comparison_papers: [] as Paper[]
  })

  useEffect(() => {
    if (!loading && !user) router.push('/login')
    else if (user) {
      fetchReviews()
      fetchSavedPapers()
    }
  }, [user, loading, router])

  const fetchReviews = async () => {
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/deep-review/reviews?token=${token}`)
      const data = await res.json()
      setReviews(data.reviews || [])
    } catch (error: any) {
      console.error('Fetch reviews error:', error)
    }
  }

  const fetchReviewDetail = async (reviewId: string) => {
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/deep-review/review/${reviewId}?token=${token}`)
      const data = await res.json()
      const review = data.review
      setSelectedReview({
        review_id: review.id,
        overall_rating: review.overall_rating,
        methods_critique: typeof review.methods_critique === 'string' ? JSON.parse(review.methods_critique) : review.methods_critique,
        results_critique: typeof review.results_critique === 'string' ? JSON.parse(review.results_critique) : review.results_critique,
        discussion_critique: typeof review.discussion_critique === 'string' ? JSON.parse(review.discussion_critique) : review.discussion_critique,
        suggestions: typeof review.suggestions === 'string' ? JSON.parse(review.suggestions) : review.suggestions,
        similarity_analysis: review.similarity_analysis || [],
        agent_tasks: review.agent_tasks || {}
      })
      setPaperForm({
        title: review.paper_title,
        content: review.paper_content || '',
        comparison_papers: review.comparison_papers || []
      })
    } catch (error: any) {
      console.error('Fetch review detail error:', error)
      alert('Failed to load review details')
    }
  }

  const fetchSavedPapers = async () => {
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/literature/saved-papers?token=${token}`)
      const data = await res.json()
      setSavedPapers(data.papers || [])
    } catch (error: any) {
      console.error('Fetch saved papers error:', error)
    }
  }

  const handleAnalyze = async () => {
    if (!paperForm.title.trim() || !paperForm.content.trim()) {
      alert('Please provide both title and content')
      return
    }

    setAnalyzing(true)
    setAnalysisProgress(0)
    setCurrentAgent('Initializing agents...')

    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token

      const res = await fetch(`${API_URL}/api/deep-review/analyze?token=${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          paper_content: paperForm.content,
          paper_title: paperForm.title,
          comparison_papers: paperForm.comparison_papers.length > 0 ? paperForm.comparison_papers : undefined
        }),
      })

      if (!res.ok) throw new Error('Analysis failed')

      const data: AnalyzeResponse = await res.json()
      setSelectedReview(data)
      setShowAnalyzeDialog(false)
      setPaperForm({ title: '', content: '', comparison_papers: [] })
      await fetchReviews()
    } catch (error: any) {
      alert(error.message)
    } finally {
      setAnalyzing(false)
      setAnalysisProgress(0)
      setCurrentAgent('')
    }
  }

  const handleSaveReview = async () => {
    if (!selectedReview) return

    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token

      const res = await fetch(`${API_URL}/api/deep-review/save-review?token=${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          review_id: selectedReview.review_id,
          paper_title: paperForm.title,
          paper_content: paperForm.content,
          comparison_papers: paperForm.comparison_papers,
          overall_rating: selectedReview.overall_rating,
          methods_critique: JSON.stringify(selectedReview.methods_critique),
          results_critique: JSON.stringify(selectedReview.results_critique),
          discussion_critique: JSON.stringify(selectedReview.discussion_critique),
          suggestions: JSON.stringify(selectedReview.suggestions),
          similarity_analysis: selectedReview.similarity_analysis,
          agent_tasks: selectedReview.agent_tasks
        }),
      })

      if (!res.ok) throw new Error('Save failed')

      alert('Review saved successfully!')
      await fetchReviews()
    } catch (error: any) {
      alert(error.message)
    }
  }

  const toggleComparisonPaper = (paper: Paper) => {
    const isSelected = paperForm.comparison_papers.some(p => p.doi === paper.doi)
    if (isSelected) {
      setPaperForm({
        ...paperForm,
        comparison_papers: paperForm.comparison_papers.filter(p => p.doi !== paper.doi)
      })
    } else {
      setPaperForm({
        ...paperForm,
        comparison_papers: [...paperForm.comparison_papers, paper].slice(0, 5)
      })
    }
  }

  const exportReview = (format: string) => {
    if (!selectedReview) return

    let content = ''

    if (format === 'markdown') {
      content = `# Deep Review: ${paperForm.title}

## Overall Rating
**Score:** ${selectedReview.overall_rating.score}/10
**Verdict:** ${selectedReview.overall_rating.explanation}

**Strengths:**
${selectedReview.overall_rating.strengths.map(s => `- ${s}`).join('\n')}

**Weaknesses:**
${selectedReview.overall_rating.weaknesses.map(w => `- ${w}`).join('\n')}

## Methods Critique
\`\`\`json
${JSON.stringify(selectedReview.methods_critique, null, 2)}
\`\`\`

## Results Critique
\`\`\`json
${JSON.stringify(selectedReview.results_critique, null, 2)}
\`\`\`

## Discussion Critique
\`\`\`json
${JSON.stringify(selectedReview.discussion_critique, null, 2)}
\`\`\`

## Suggestions for Improvement
${selectedReview.suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n')}

## Similarity Analysis
${selectedReview.similarity_analysis.map(sim => `
### ${sim.paper_title}
- **Similarity Score:** ${sim.similarity_score}%
- **Common Themes:** ${sim.common_themes.join(', ')}
- **Methodological Differences:** ${sim.methodological_differences.join(', ')}
`).join('\n')}
`
    }

    setExportContent(content)
    setExportFormat(format)
    setShowExportDialog(true)
  }

  const downloadExport = () => {
    const blob = new Blob([exportContent], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `deep_review_${paperForm.title.replace(/\s+/g, '_')}.${exportFormat === 'markdown' ? 'md' : 'txt'}`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Deep Review</h1>
          <Button onClick={() => setShowAnalyzeDialog(true)}>New Review</Button>
        </div>

        {!selectedReview ? (
          <div className="grid gap-4">
            <div className="grid gap-4">
              {reviews.map((review) => (
                <Card
                  key={review.id}
                  className="cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => fetchReviewDetail(review.id)}
                >
                  <CardHeader>
                    <CardTitle>{review.paper_title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-600">Overall Score:</span>
                        <Badge variant={review.overall_rating.score >= 7 ? 'default' : review.overall_rating.score >= 5 ? 'secondary' : 'destructive'}>
                          {review.overall_rating.score}/10
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-500">Created: {new Date(review.created_at).toLocaleDateString()}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
              {reviews.length === 0 && (
                <Card>
                  <CardContent className="pt-6 text-center">
                    <p className="text-gray-500">No deep reviews yet. Click "New Review" to analyze your first paper!</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex gap-4 items-start">
              <Button variant="outline" onClick={() => setSelectedReview(null)}>
                ← Back to Reviews
              </Button>
              <div className="flex-1">
                <Card>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <CardTitle>{paperForm.title}</CardTitle>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={handleSaveReview}>
                          Save Review
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => exportReview('markdown')}>
                          Export
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              </div>
            </div>

            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-6">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="methods">Methods</TabsTrigger>
                <TabsTrigger value="results">Results</TabsTrigger>
                <TabsTrigger value="discussion">Discussion</TabsTrigger>
                <TabsTrigger value="suggestions">Suggestions</TabsTrigger>
                <TabsTrigger value="similarity">Similarity</TabsTrigger>
              </TabsList>

              <TabsContent value="overview">
                <Card>
                  <CardHeader>
                    <CardTitle>Overall Rating</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center gap-4">
                      <div className="text-4xl font-bold">
                        {selectedReview.overall_rating.score}/10
                      </div>
                      <Badge variant={selectedReview.overall_rating.score >= 7 ? 'default' : selectedReview.overall_rating.score >= 5 ? 'secondary' : 'destructive'}>
                        {selectedReview.overall_rating.score >= 7 ? 'Accept' : selectedReview.overall_rating.score >= 5 ? 'Minor Revision' : 'Major Revision'}
                      </Badge>
                    </div>

                    <div>
                      <Label className="font-semibold">Explanation</Label>
                      <p className="text-sm text-gray-700 mt-1">{selectedReview.overall_rating.explanation}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="font-semibold">Strengths</Label>
                        <ul className="list-disc list-inside mt-2 space-y-1">
                          {selectedReview.overall_rating.strengths.map((s, i) => (
                            <li key={i} className="text-sm text-green-700">{s}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <Label className="font-semibold">Weaknesses</Label>
                        <ul className="list-disc list-inside mt-2 space-y-1">
                          {selectedReview.overall_rating.weaknesses.map((w, i) => (
                            <li key={i} className="text-sm text-red-700">{w}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    <div>
                      <Label className="font-semibold">Agent Tasks Status</Label>
                      <div className="mt-2 space-y-2">
                        {Object.entries(selectedReview.agent_tasks).map(([agent, status]: [string, any]) => (
                          <div key={agent} className="flex items-center justify-between text-sm">
                            <span className="capitalize">{agent.replace('_', ' ')}</span>
                            <Badge variant={status.status === 'completed' ? 'default' : status.status === 'error' ? 'destructive' : 'secondary'}>
                              {status.status}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="methods">
                <Card>
                  <CardHeader>
                    <CardTitle>Methods Critique</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {Object.entries(selectedReview.methods_critique).map(([key, value]: [string, any]) => (
                      typeof value === 'object' && 'score' in value ? (
                        <div key={key}>
                          <Label className="font-semibold capitalize">{key.replace('_', ' ')}</Label>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge>{value.score}/10</Badge>
                            <span className="text-sm text-gray-600">{value.explanation}</span>
                          </div>
                        </div>
                      ) : Array.isArray(value) && key === 'strengths' ? (
                        <div key={key}>
                          <Label className="font-semibold capitalize">{key}</Label>
                          <ul className="list-disc list-inside mt-2">
                            {value.map((item: string, i: number) => (
                              <li key={i} className="text-sm">{item}</li>
                            ))}
                          </ul>
                        </div>
                      ) : Array.isArray(value) && key === 'weaknesses' ? (
                        <div key={key}>
                          <Label className="font-semibold capitalize">{key}</Label>
                          <ul className="list-disc list-inside mt-2">
                            {value.map((item: string, i: number) => (
                              <li key={i} className="text-sm">{item}</li>
                            ))}
                          </ul>
                        </div>
                      ) : null
                    ))}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="results">
                <Card>
                  <CardHeader>
                    <CardTitle>Results Critique</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {Object.entries(selectedReview.results_critique).map(([key, value]: [string, any]) => (
                      typeof value === 'object' && 'score' in value ? (
                        <div key={key}>
                          <Label className="font-semibold capitalize">{key.replace('_', ' ')}</Label>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge>{value.score}/10</Badge>
                            <span className="text-sm text-gray-600">{value.explanation}</span>
                          </div>
                        </div>
                      ) : Array.isArray(value) && key === 'strengths' ? (
                        <div key={key}>
                          <Label className="font-semibold capitalize">{key}</Label>
                          <ul className="list-disc list-inside mt-2">
                            {value.map((item: string, i: number) => (
                              <li key={i} className="text-sm">{item}</li>
                            ))}
                          </ul>
                        </div>
                      ) : Array.isArray(value) && key === 'weaknesses' ? (
                        <div key={key}>
                          <Label className="font-semibold capitalize">{key}</Label>
                          <ul className="list-disc list-inside mt-2">
                            {value.map((item: string, i: number) => (
                              <li key={i} className="text-sm">{item}</li>
                            ))}
                          </ul>
                        </div>
                      ) : null
                    ))}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="discussion">
                <Card>
                  <CardHeader>
                    <CardTitle>Discussion Critique</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {Object.entries(selectedReview.discussion_critique).map(([key, value]: [string, any]) => (
                      typeof value === 'object' && 'score' in value ? (
                        <div key={key}>
                          <Label className="font-semibold capitalize">{key.replace('_', ' ')}</Label>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge>{value.score}/10</Badge>
                            <span className="text-sm text-gray-600">{value.explanation}</span>
                          </div>
                        </div>
                      ) : Array.isArray(value) && key === 'strengths' ? (
                        <div key={key}>
                          <Label className="font-semibold capitalize">{key}</Label>
                          <ul className="list-disc list-inside mt-2">
                            {value.map((item: string, i: number) => (
                              <li key={i} className="text-sm">{item}</li>
                            ))}
                          </ul>
                        </div>
                      ) : Array.isArray(value) && key === 'weaknesses' ? (
                        <div key={key}>
                          <Label className="font-semibold capitalize">{key}</Label>
                          <ul className="list-disc list-inside mt-2">
                            {value.map((item: string, i: number) => (
                              <li key={i} className="text-sm">{item}</li>
                            ))}
                          </ul>
                        </div>
                      ) : null
                    ))}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="suggestions">
                <Card>
                  <CardHeader>
                    <CardTitle>Suggestions for Improvement</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ol className="list-decimal list-inside space-y-3">
                      {selectedReview.suggestions.map((suggestion, i) => (
                        <li key={i} className="text-sm">
                          <p className="font-medium">{suggestion}</p>
                        </li>
                      ))}
                    </ol>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="similarity">
                <Card>
                  <CardHeader>
                    <CardTitle>Similarity Analysis</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {selectedReview.similarity_analysis.length > 0 ? (
                      <div className="space-y-4">
                        {selectedReview.similarity_analysis.map((sim, i) => (
                          <div key={i} className="p-4 bg-gray-50 rounded">
                            <div className="flex justify-between items-start mb-2">
                              <h4 className="font-semibold">{sim.paper_title}</h4>
                              <Badge>{sim.similarity_score}% similarity</Badge>
                            </div>
                            <div className="space-y-2">
                              <div>
                                <Label className="text-xs">Common Themes</Label>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {sim.common_themes.map((theme, j) => (
                                    <Badge key={j} variant="outline" className="text-xs">{theme}</Badge>
                                  ))}
                                </div>
                              </div>
                              <div>
                                <Label className="text-xs">Methodological Differences</Label>
                                <ul className="list-disc list-inside mt-1 text-sm text-gray-600">
                                  {sim.methodological_differences.map((diff, j) => (
                                    <li key={j}>{diff}</li>
                                  ))}
                                </ul>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-center">No comparison papers selected</p>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        )}
      </div>

      <Dialog open={showAnalyzeDialog} onOpenChange={setShowAnalyzeDialog}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>New Deep Review</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="paper_title">Paper Title *</Label>
              <Input
                id="paper_title"
                value={paperForm.title}
                onChange={(e) => setPaperForm({ ...paperForm, title: e.target.value })}
                placeholder="Enter the paper title..."
              />
            </div>

            <div>
              <Label htmlFor="paper_content">Paper Content *</Label>
              <Textarea
                id="paper_content"
                value={paperForm.content}
                onChange={(e) => setPaperForm({ ...paperForm, content: e.target.value })}
                placeholder="Paste the full paper content here..."
                rows={15}
              />
            </div>

            <div>
              <div className="flex justify-between items-center">
                <Label>Comparison Papers</Label>
                <Button variant="outline" size="sm" onClick={() => setShowComparisonDialog(true)}>
                  Select Papers ({paperForm.comparison_papers.length}/5)
                </Button>
              </div>
              {paperForm.comparison_papers.length > 0 && (
                <div className="mt-2 space-y-2">
                  {paperForm.comparison_papers.map((paper, i) => (
                    <div key={i} className="p-2 bg-gray-50 rounded flex justify-between items-center">
                      <div>
                        <p className="text-sm font-medium">{paper.title}</p>
                        <p className="text-xs text-gray-500">{paper.authors.slice(0, 2).join(', ')}</p>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => toggleComparisonPaper(paper)}>
                        Remove
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <Button onClick={handleAnalyze} className="w-full" disabled={analyzing}>
              {analyzing ? 'Analyzing...' : 'Start Deep Review'}
            </Button>

            {analyzing && (
              <div className="space-y-2">
                <p className="text-sm text-gray-600">{currentAgent}</p>
                <Progress value={analysisProgress} />
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showComparisonDialog} onOpenChange={setShowComparisonDialog}>
        <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Select Comparison Papers</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {savedPapers.length > 0 ? (
              <div className="space-y-2">
                {savedPapers.map((paper, i) => (
                  <div
                    key={i}
                    className="p-3 border rounded cursor-pointer hover:bg-gray-50"
                    onClick={() => toggleComparisonPaper(paper)}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{paper.title}</p>
                        <p className="text-sm text-gray-500">{paper.authors.slice(0, 3).join(', ')}</p>
                        <p className="text-xs text-gray-400">{paper.journal} ({paper.year})</p>
                      </div>
                      {paperForm.comparison_papers.some(p => p.doi === paper.doi) && (
                        <Badge>Selected</Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center">No saved papers available. Save papers from the Literature Search first.</p>
            )}
            <Button onClick={() => setShowComparisonDialog(false)} className="w-full">
              Done
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={showExportDialog} onOpenChange={setShowExportDialog}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Export Review</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="max-h-[400px] overflow-y-auto bg-gray-50 p-4 rounded">
              <pre className="text-xs whitespace-pre-wrap">{exportContent}</pre>
            </div>
            <Button onClick={downloadExport} className="w-full">
              Download {exportFormat.toUpperCase()}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
