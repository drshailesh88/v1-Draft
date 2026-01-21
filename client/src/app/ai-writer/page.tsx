'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { useRouter } from 'next/navigation'

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

interface Project {
  id: string
  title: string
  topic: string
  research_questions: string
  sections: Section[]
  created_at: string
  updated_at: string
}

interface Section {
  id: string
  project_id: string
  section_type: string
  content: string
  word_count: number
  citations_used: string[]
  created_at: string
  updated_at: string
}

const SECTION_TYPES = [
  { id: 'abstract', label: 'Abstract' },
  { id: 'introduction', label: 'Introduction' },
  { id: 'methods', label: 'Methods' },
  { id: 'results', label: 'Results' },
  { id: 'discussion', label: 'Discussion' },
  { id: 'conclusion', label: 'Conclusion' },
]

export default function AIWriterPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [currentProject, setCurrentProject] = useState<Project | null>(null)
  const [showNewProject, setShowNewProject] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [papers, setPapers] = useState<Paper[]>([])
  const [selectedPapers, setSelectedPapers] = useState<Paper[]>([])
  const [generating, setGenerating] = useState(false)
  const [activeSection, setActiveSection] = useState('abstract')
  const [sectionContent, setSectionContent] = useState('')
  const [keyPoints, setKeyPoints] = useState('')
  const [wordCount, setWordCount] = useState(0)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

  useEffect(() => {
    if (!loading && !user) router.push('/login')
    else if (user) fetchProjects()
  }, [user, loading, router])

  useEffect(() => {
    setWordCount(sectionContent.split(/\s+/).filter(w => w.length > 0).length)
  }, [sectionContent])

  const fetchProjects = async () => {
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/ai-writer/projects?token=${token}`)
      const data = await res.json()
      setProjects(data.projects || [])
    } catch (error) {
      console.error('Error fetching projects:', error)
    }
  }

  const fetchProject = async (projectId: string) => {
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/ai-writer/project/${projectId}?token=${token}`)
      const data = await res.json()
      setCurrentProject(data)
      setShowNewProject(false)
    } catch (error) {
      console.error('Error fetching project:', error)
    }
  }

  const createProject = async (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.target as HTMLFormElement)
    const title = formData.get('title') as string
    const topic = formData.get('topic') as string
    const researchQuestions = formData.get('research_questions') as string

    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/ai-writer/create-project`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title,
          topic,
          research_questions: researchQuestions,
          token,
        }),
      })

      if (!res.ok) throw new Error('Failed to create project')

      const data = await res.json()
      await fetchProject(data.project_id)
      await fetchProjects()
    } catch (error) {
      alert('Failed to create project')
    }
  }

  const searchPapers = async () => {
    if (!searchQuery.trim()) return
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/literature/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          sources: ['pubmed', 'arxiv', 'semantic_scholar'],
          max_results: 10,
          token,
        }),
      })

      if (!res.ok) throw new Error('Search failed')

      const data = await res.json()
      setPapers(data.papers || [])
    } catch (error) {
      alert('Failed to search papers')
    }
  }

  const generateSection = async () => {
    if (!currentProject || !keyPoints.trim()) {
      alert('Please enter key points for this section')
      return
    }

    setGenerating(true)
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/ai-writer/generate-section`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: currentProject.id,
          section_type: activeSection,
          paper_topic: currentProject.topic,
          key_points: keyPoints,
          selected_papers: selectedPapers,
          token,
        }),
      })

      if (!res.ok) throw new Error('Generation failed')

      const data = await res.json()
      setSectionContent(data.generated_text)
      setWordCount(data.word_count)
    } catch (error) {
      alert('Failed to generate section')
    } finally {
      setGenerating(false)
    }
  }

  const saveSection = async () => {
    if (!currentProject || !sectionContent.trim()) {
      alert('Please generate content first')
      return
    }

    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/ai-writer/save-section`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: currentProject.id,
          section_type: activeSection,
          content: sectionContent,
          word_count: wordCount,
          citations_used: selectedPapers.map(p => p.title),
          token,
        }),
      })

      if (!res.ok) throw new Error('Save failed')

      alert('Section saved!')
      await fetchProject(currentProject.id)
    } catch (error) {
      alert('Failed to save section')
    }
  }

  const deleteProject = async (projectId: string) => {
    if (!confirm('Are you sure you want to delete this project?')) return

    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      await fetch(`${API_URL}/api/ai-writer/project/${projectId}?token=${token}`, {
        method: 'DELETE',
      })

      await fetchProjects()
      if (currentProject?.id === projectId) {
        setCurrentProject(null)
        setShowNewProject(true)
      }
    } catch (error) {
      alert('Failed to delete project')
    }
  }

  const loadSection = (section: Section) => {
    setActiveSection(section.section_type)
    setSectionContent(section.content)
    setWordCount(section.word_count || 0)
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">AI Writer</h1>
          <p className="text-gray-600">Draft academic papers section by section with AI assistance</p>
        </div>

        {!showNewProject && !currentProject && (
          <div className="grid md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Your Projects ({projects.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {projects.map((project) => (
                    <div key={project.id} className="p-3 bg-gray-50 rounded hover:bg-gray-100 cursor-pointer" onClick={() => fetchProject(project.id)}>
                      <p className="font-medium">{project.title}</p>
                      <p className="text-sm text-gray-500 truncate">{project.topic}</p>
                      <div className="mt-2 flex justify-between items-center">
                        <Badge variant="outline">{project.sections?.length || 0} sections</Badge>
                        <Button size="sm" variant="ghost" onClick={(e) => { e.stopPropagation(); deleteProject(project.id) }}>Delete</Button>
                      </div>
                    </div>
                  ))}
                  {projects.length === 0 && <p className="text-gray-500 text-sm">No projects yet</p>}
                </div>
                <Button onClick={() => setShowNewProject(true)} className="w-full mt-4">Create New Project</Button>
              </CardContent>
            </Card>
          </div>
        )}

        {showNewProject && (
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>Create New Writing Project</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={createProject} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Project Title</label>
                  <Input name="title" placeholder="e.g., AI in Drug Discovery" required />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Research Topic</label>
                  <Input name="topic" placeholder="e.g., Machine learning approaches for drug discovery" required />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Research Questions</label>
                  <Textarea name="research_questions" placeholder="What are the main research questions you want to address?" rows={3} />
                </div>
                <Button type="submit" className="w-full">Create Project</Button>
                <Button type="button" variant="outline" className="w-full" onClick={() => setShowNewProject(false)}>Cancel</Button>
              </form>
            </CardContent>
          </Card>
        )}

        {currentProject && (
          <div className="space-y-6">
            <Card>
              <CardContent className="pt-6">
                <div className="flex justify-between items-center">
                  <div>
                    <h2 className="text-2xl font-bold">{currentProject.title}</h2>
                    <p className="text-gray-600">{currentProject.topic}</p>
                  </div>
                  <Button variant="outline" onClick={() => { setCurrentProject(null); setShowNewProject(false) }}>Back to Projects</Button>
                </div>
              </CardContent>
            </Card>

            <div className="grid md:grid-cols-3 gap-6">
              <div className="md:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Generate Section</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Tabs value={activeSection} onValueChange={setActiveSection}>
                      <TabsList className="grid grid-cols-3 w-full">
                        {SECTION_TYPES.slice(0, 3).map((section) => (
                          <TabsTrigger key={section.id} value={section.id}>{section.label}</TabsTrigger>
                        ))}
                      </TabsList>
                      <TabsList className="grid grid-cols-3 w-full mt-2">
                        {SECTION_TYPES.slice(3).map((section) => (
                          <TabsTrigger key={section.id} value={section.id}>{section.label}</TabsTrigger>
                        ))}
                      </TabsList>

                      {SECTION_TYPES.map((section) => (
                        <TabsContent key={section.id} value={section.id} className="mt-4">
                          <div className="space-y-4">
                            <div>
                              <label className="block text-sm font-medium mb-1">Key Points for {section.label}</label>
                              <Textarea
                                value={keyPoints}
                                onChange={(e) => setKeyPoints(e.target.value)}
                                placeholder={`What should this ${section.label.toLowerCase()} cover?`}
                                rows={4}
                              />
                            </div>
                            <div className="flex gap-2">
                              <Button onClick={generateSection} disabled={generating || !keyPoints.trim()}>
                                {generating ? 'Generating...' : 'Generate'}
                              </Button>
                              <Button onClick={saveSection} disabled={!sectionContent.trim()} variant="outline">Save</Button>
                            </div>
                            <div>
                              <label className="block text-sm font-medium mb-1">Generated Content</label>
                              <Textarea
                                value={sectionContent}
                                onChange={(e) => setSectionContent(e.target.value)}
                                rows={15}
                                className="font-mono text-sm"
                              />
                              <p className="text-sm text-gray-500 mt-1">Word count: {wordCount}</p>
                            </div>
                          </div>
                        </TabsContent>
                      ))}
                    </Tabs>
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Saved Sections</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {currentProject.sections?.length > 0 ? (
                        currentProject.sections.map((section) => (
                          <div
                            key={section.id}
                            className="p-2 bg-gray-50 rounded hover:bg-gray-100 cursor-pointer"
                            onClick={() => loadSection(section)}
                          >
                            <div className="flex justify-between">
                              <span className="font-medium capitalize">{section.section_type}</span>
                              <span className="text-sm text-gray-500">{section.word_count} words</span>
                            </div>
                          </div>
                        ))
                      ) : (
                        <p className="text-sm text-gray-500">No saved sections</p>
                      )}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Find Papers</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex gap-2">
                        <Input
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && searchPapers()}
                          placeholder="Search for papers..."
                        />
                        <Button size="sm" onClick={searchPapers}>Search</Button>
                      </div>

                      {papers.length > 0 && (
                        <div className="space-y-2 max-h-60 overflow-y-auto">
                          {papers.map((paper, idx) => (
                            <div key={idx} className="p-2 bg-gray-50 rounded">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <input
                                    type="checkbox"
                                    checked={selectedPapers.some(p => p.doi === paper.doi)}
                                    onChange={(e) => {
                                      if (e.target.checked) {
                                        setSelectedPapers([...selectedPapers, paper])
                                      } else {
                                        setSelectedPapers(selectedPapers.filter(p => p.doi !== paper.doi))
                                      }
                                    }}
                                    className="mr-2"
                                  />
                                  <span className="text-sm font-medium">{paper.title}</span>
                                  <p className="text-xs text-gray-500">{paper.authors.slice(0, 2).join(', ')} ({paper.year})</p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {selectedPapers.length > 0 && (
                        <div className="border-t pt-2">
                          <p className="text-sm font-medium mb-2">Selected Papers ({selectedPapers.length})</p>
                          <div className="space-y-1">
                            {selectedPapers.map((paper, idx) => (
                              <div key={idx} className="flex justify-between items-center text-xs">
                                <span className="truncate flex-1">{paper.title}</span>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="h-6 px-2"
                                  onClick={() => setSelectedPapers(selectedPapers.filter(p => p.doi !== paper.doi))}
                                >
                                  ×
                                </Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
