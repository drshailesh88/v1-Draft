'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useRouter } from 'next/navigation'

interface Topic {
  name: string
  relevance: number
  description: string
  gap_analysis: string
  trending_score: number
}

interface SavedTopic {
  id: string
  research_field: string
  topic_name: string
  relevance_score: number
  gap_analysis: string
  trending_score: number
  description: string
  created_at: string
}

export default function TopicsPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [researchField, setResearchField] = useState('')
  const [numTopics, setNumTopics] = useState('10')
  const [topics, setTopics] = useState<Topic[]>([])
  const [savedTopics, setSavedTopics] = useState<SavedTopic[]>([])
  const [discovering, setDiscovering] = useState(false)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

  useEffect(() => {
    if (!loading && !user) router.push('/login')
    else if (user) fetchSavedTopics()
  }, [user, loading, router])

  const fetchSavedTopics = async () => {
    const token = (await supabase.auth.getSession()).data.session?.access_token
    const res = await fetch(`${API_URL}/api/topics/history?token=${token}`)
    const data = await res.json()
    setSavedTopics(data.topics || [])
  }

  const handleDiscover = async () => {
    if (!researchField.trim()) return
    setDiscovering(true)
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/topics/discover`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ research_field: researchField, num_topics: parseInt(numTopics), token }),
      })
      if (!res.ok) throw new Error('Discovery failed')
      const data = await res.json()
      setTopics(data.topics)
      await fetchSavedTopics()
    } catch (error: any) {
      alert(error.message)
    } finally {
      setDiscovering(false)
    }
  }

  const getTrendingBadge = (score: number) => {
    if (score >= 0.8) return <Badge variant="default" className="bg-red-500">🔥 Hot</Badge>
    if (score >= 0.6) return <Badge variant="default" className="bg-orange-500">Trending</Badge>
    if (score >= 0.4) return <Badge variant="secondary">Rising</Badge>
    return <Badge variant="outline">Stable</Badge>
  }

  const getRelevanceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.6) return 'text-blue-600'
    if (score >= 0.4) return 'text-yellow-600'
    return 'text-gray-600'
  }

  const handleClearHistory = async () => {
    if (!confirm('Are you sure you want to clear all topic history?')) return
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      await fetch(`${API_URL}/api/topics/history`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      })
      setSavedTopics([])
      setTopics([])
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
            <CardTitle>Discover Research Topics</CardTitle>
            <CardDescription>Find trending topics and research gaps in your field</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 flex-wrap">
              <Input
                value={researchField}
                onChange={(e) => setResearchField(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleDiscover()}
                placeholder="Enter research field (e.g., 'machine learning', 'climate change')"
                className="flex-1 min-w-[300px]"
              />
              <Select value={numTopics} onValueChange={setNumTopics}>
                <SelectTrigger className="w-[120px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="5">5 topics</SelectItem>
                  <SelectItem value="10">10 topics</SelectItem>
                  <SelectItem value="15">15 topics</SelectItem>
                  <SelectItem value="20">20 topics</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={handleDiscover} disabled={discovering}>
                {discovering ? 'Discovering...' : 'Discover Topics'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {topics.length > 0 && (
          <div className="mt-6">
            <h2 className="text-xl font-semibold mb-4">Discovered Topics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {topics.map((topic, idx) => (
                <Card key={idx} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <CardTitle className="text-lg">{topic.name}</CardTitle>
                      {getTrendingBadge(topic.trending_score)}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600 mb-3">{topic.description}</p>
                    
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">Relevance:</span>
                        <span className={`text-sm font-semibold ${getRelevanceColor(topic.relevance)}`}>
                          {(topic.relevance * 100).toFixed(0)}%
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">Trending:</span>
                        <span className="text-sm font-semibold">
                          {(topic.trending_score * 100).toFixed(0)}%
                        </span>
                      </div>
                      
                      <div className="mt-3">
                        <span className="text-sm font-medium block mb-1">Research Gaps:</span>
                        <p className="text-xs text-gray-700 bg-blue-50 p-2 rounded">
                          {topic.gap_analysis}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {savedTopics.length > 0 && (
          <Card className="mt-6">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Discovery History ({savedTopics.length})</CardTitle>
                <Button variant="outline" size="sm" onClick={handleClearHistory}>
                  Clear History
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {savedTopics.slice(0, 10).map((topic) => (
                  <div key={topic.id} className="p-3 bg-gray-50 rounded border">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="font-medium text-sm">{topic.topic_name}</p>
                        <p className="text-xs text-gray-500">{topic.research_field}</p>
                      </div>
                      {getTrendingBadge(topic.trending_score)}
                    </div>
                    <div className="flex gap-4 text-xs text-gray-600">
                      <span>Relevance: {(topic.relevance_score * 100).toFixed(0)}%</span>
                      <span>Trending: {(topic.trending_score * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
                {savedTopics.length > 10 && (
                  <p className="text-sm text-gray-500 text-center">... and {savedTopics.length - 10} more</p>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
