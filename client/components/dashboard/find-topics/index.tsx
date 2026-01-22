'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/layout';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { User } from '@supabase/supabase-js';
import { api, apiCall } from '@/lib/api';
import {
  HiOutlineLightBulb,
  HiOutlineMagnifyingGlass,
  HiOutlineArrowTrendingUp,
  HiOutlineBookmark,
  HiOutlineCheck,
  HiOutlineRectangleGroup,
  HiOutlineExclamationTriangle,
  HiOutlineArrowPath,
  HiOutlineSparkles,
  HiOutlineXMark,
} from 'react-icons/hi2';

interface Props {
  user: User | null | undefined;
  userDetails: { [x: string]: any } | null;
}

interface TrendingTopic {
  id: string;
  title: string;
  description: string;
  trendScore: number;
  publicationCount: number;
  growthRate: string;
  relatedKeywords: string[];
}

interface ResearchGap {
  id: string;
  title: string;
  description: string;
  potentialImpact: 'high' | 'medium' | 'low';
  feasibility: 'high' | 'medium' | 'low';
  existingWork: string;
}

interface TopicCluster {
  id: string;
  name: string;
  topics: string[];
  paperCount: number;
  connections: string[];
}

interface DiscoverResult {
  trendingTopics: TrendingTopic[];
  researchGaps: ResearchGap[];
  topicClusters: TopicCluster[];
}

interface SavedTopic {
  id: string;
  type: 'trending' | 'gap';
  title: string;
  savedAt: string;
}

export default function FindTopics(props: Props) {
  const [researchField, setResearchField] = useState('');
  const [keywords, setKeywords] = useState('');
  const [results, setResults] = useState<DiscoverResult | null>(null);
  const [savedTopics, setSavedTopics] = useState<SavedTopic[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('trending');

  const handleDiscover = async () => {
    if (!researchField.trim()) {
      setError('Please enter a research field.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await apiCall<DiscoverResult>(api.findTopics.discover, {
        method: 'POST',
        body: JSON.stringify({
          field: researchField,
          keywords: keywords.split(',').map((k) => k.trim()).filter((k) => k),
        }),
      });

      setResults(response);
      setActiveTab('trending');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to discover topics. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveTopic = async (topic: TrendingTopic | ResearchGap, type: 'trending' | 'gap') => {
    const existing = savedTopics.find((t) => t.id === topic.id);
    if (existing) {
      setSavedTopics(savedTopics.filter((t) => t.id !== topic.id));
      return;
    }

    try {
      await apiCall(api.findTopics.saved, {
        method: 'POST',
        body: JSON.stringify({
          topicId: topic.id,
          type,
          title: topic.title,
        }),
      });

      setSavedTopics([
        ...savedTopics,
        {
          id: topic.id,
          type,
          title: topic.title,
          savedAt: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      console.error('Failed to save topic:', err);
    }
  };

  const isTopicSaved = (id: string) => savedTopics.some((t) => t.id === id);

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'low':
        return 'bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-400';
      default:
        return 'bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-400';
    }
  };

  return (
    <DashboardLayout
      user={props.user}
      userDetails={props.userDetails}
      title="Find Topics"
      description="Discover research topics and gaps"
    >
      <div className="mx-auto max-w-6xl px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-zinc-950 dark:text-white">
            Find Topics
          </h1>
          <p className="mt-2 text-zinc-500 dark:text-zinc-400">
            Discover trending research topics, gaps, and opportunities in your field.
          </p>
        </div>

        {/* Search Section */}
        <Card className="mb-6 dark:border-zinc-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <HiOutlineMagnifyingGlass className="h-5 w-5" />
              Discover Topics
            </CardTitle>
            <CardDescription>
              Enter your research field and optional keywords to find relevant topics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="research-field">Research Field</Label>
                <Input
                  id="research-field"
                  placeholder="e.g., Machine Learning, Neuroscience, Climate Science"
                  value={researchField}
                  onChange={(e) => setResearchField(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="keywords">Keywords (optional)</Label>
                <Input
                  id="keywords"
                  placeholder="e.g., transformer, attention, NLP (comma separated)"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                />
              </div>
            </div>

            {error && (
              <div className="mt-4 rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
                {error}
              </div>
            )}

            <Button
              className="mt-4 w-full md:w-auto"
              onClick={handleDiscover}
              disabled={loading || !researchField.trim()}
            >
              {loading ? (
                <>
                  <HiOutlineArrowPath className="mr-2 h-4 w-4 animate-spin" />
                  Discovering...
                </>
              ) : (
                <>
                  <HiOutlineSparkles className="mr-2 h-4 w-4" />
                  Discover Topics
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Results Section */}
        {results && (
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="trending" className="flex items-center gap-2">
                <HiOutlineArrowTrendingUp className="h-4 w-4" />
                Trending
              </TabsTrigger>
              <TabsTrigger value="gaps" className="flex items-center gap-2">
                <HiOutlineExclamationTriangle className="h-4 w-4" />
                Research Gaps
              </TabsTrigger>
              <TabsTrigger value="clusters" className="flex items-center gap-2">
                <HiOutlineRectangleGroup className="h-4 w-4" />
                Clusters
              </TabsTrigger>
              <TabsTrigger value="saved" className="flex items-center gap-2">
                <HiOutlineBookmark className="h-4 w-4" />
                Saved ({savedTopics.length})
              </TabsTrigger>
            </TabsList>

            {/* Trending Topics Tab */}
            <TabsContent value="trending" className="mt-6">
              <div className="grid gap-4 md:grid-cols-2">
                {results.trendingTopics.map((topic) => (
                  <Card key={topic.id} className="dark:border-zinc-800">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <CardTitle className="text-lg">{topic.title}</CardTitle>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleSaveTopic(topic, 'trending')}
                        >
                          {isTopicSaved(topic.id) ? (
                            <HiOutlineCheck className="h-5 w-5 text-green-500" />
                          ) : (
                            <HiOutlineBookmark className="h-5 w-5" />
                          )}
                        </Button>
                      </div>
                      <CardDescription className="line-clamp-2">
                        {topic.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="mb-3 flex flex-wrap gap-2">
                        <Badge variant="secondary">
                          <HiOutlineArrowTrendingUp className="mr-1 h-3 w-3" />
                          Trend Score: {topic.trendScore}
                        </Badge>
                        <Badge variant="outline">
                          {topic.publicationCount} papers
                        </Badge>
                        <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                          {topic.growthRate} growth
                        </Badge>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {topic.relatedKeywords.map((keyword, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* Research Gaps Tab */}
            <TabsContent value="gaps" className="mt-6">
              <div className="space-y-4">
                {results.researchGaps.map((gap) => (
                  <Card key={gap.id} className="dark:border-zinc-800">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-lg">{gap.title}</CardTitle>
                          <CardDescription className="mt-1">
                            {gap.description}
                          </CardDescription>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleSaveTopic(gap, 'gap')}
                        >
                          {isTopicSaved(gap.id) ? (
                            <HiOutlineCheck className="h-5 w-5 text-green-500" />
                          ) : (
                            <HiOutlineBookmark className="h-5 w-5" />
                          )}
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="mb-3 flex flex-wrap gap-2">
                        <Badge className={getImpactColor(gap.potentialImpact)}>
                          Impact: {gap.potentialImpact}
                        </Badge>
                        <Badge className={getImpactColor(gap.feasibility)}>
                          Feasibility: {gap.feasibility}
                        </Badge>
                      </div>
                      <div className="rounded-lg bg-zinc-50 p-3 dark:bg-zinc-900">
                        <p className="text-sm text-zinc-600 dark:text-zinc-400">
                          <strong>Existing Work:</strong> {gap.existingWork}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* Topic Clusters Tab */}
            <TabsContent value="clusters" className="mt-6">
              <div className="space-y-4">
                {results.topicClusters.map((cluster) => (
                  <Card key={cluster.id} className="dark:border-zinc-800">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2 text-lg">
                          <HiOutlineRectangleGroup className="h-5 w-5 text-blue-500" />
                          {cluster.name}
                        </CardTitle>
                        <Badge variant="secondary">
                          {cluster.paperCount} papers
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="mb-4">
                        <h4 className="mb-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
                          Topics in this cluster:
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {cluster.topics.map((topic, index) => (
                            <Badge key={index} variant="outline">
                              {topic}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      {cluster.connections.length > 0 && (
                        <div>
                          <h4 className="mb-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
                            Connected to:
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {cluster.connections.map((connection, index) => (
                              <Badge
                                key={index}
                                variant="secondary"
                                className="bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400"
                              >
                                {connection}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* Saved Topics Tab */}
            <TabsContent value="saved" className="mt-6">
              {savedTopics.length === 0 ? (
                <Card className="dark:border-zinc-800">
                  <CardContent className="flex min-h-[200px] flex-col items-center justify-center py-8">
                    <HiOutlineBookmark className="mb-4 h-12 w-12 text-zinc-300 dark:text-zinc-600" />
                    <p className="text-zinc-500 dark:text-zinc-400">
                      No saved topics yet. Click the bookmark icon to save topics.
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-3">
                  {savedTopics.map((topic) => (
                    <Card key={topic.id} className="dark:border-zinc-800">
                      <CardContent className="flex items-center justify-between py-4">
                        <div className="flex items-center gap-3">
                          {topic.type === 'trending' ? (
                            <HiOutlineArrowTrendingUp className="h-5 w-5 text-green-500" />
                          ) : (
                            <HiOutlineExclamationTriangle className="h-5 w-5 text-yellow-500" />
                          )}
                          <div>
                            <p className="font-medium text-zinc-900 dark:text-white">
                              {topic.title}
                            </p>
                            <p className="text-xs text-zinc-500">
                              Saved {new Date(topic.savedAt).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="capitalize">
                            {topic.type}
                          </Badge>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              setSavedTopics(savedTopics.filter((t) => t.id !== topic.id))
                            }
                          >
                            <HiOutlineXMark className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        )}

        {/* Empty State */}
        {!results && !loading && (
          <Card className="dark:border-zinc-800">
            <CardContent className="flex min-h-[300px] flex-col items-center justify-center py-8">
              <HiOutlineLightBulb className="mb-4 h-16 w-16 text-zinc-300 dark:text-zinc-600" />
              <h3 className="mb-2 text-xl font-medium text-zinc-900 dark:text-white">
                Ready to Discover
              </h3>
              <p className="max-w-md text-center text-zinc-500 dark:text-zinc-400">
                Enter your research field above to discover trending topics, identify research gaps,
                and explore topic clusters in your area of interest.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
