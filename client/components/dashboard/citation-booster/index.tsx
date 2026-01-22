'use client';

import DashboardLayout from '@/components/layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { api, apiCall } from '@/lib/api';
import { User } from '@supabase/supabase-js';
import { useState } from 'react';
import {
  HiOutlineSparkles,
  HiOutlineMagnifyingGlass,
  HiOutlineDocumentText,
  HiOutlinePlusCircle,
  HiOutlineClipboardDocument,
  HiOutlineExclamationTriangle,
  HiOutlineCheckCircle,
  HiOutlineLightBulb,
} from 'react-icons/hi2';

interface Props {
  user: User | null | undefined;
  userDetails: { [x: string]: any } | null;
}

interface SuggestedCitation {
  id: string;
  title: string;
  authors: string[];
  year: number;
  journal: string;
  doi?: string;
  relevance_score: number;
  relevance_reason: string;
  citation_context: string;
  formatted_citation: {
    apa: string;
    mla: string;
    chicago: string;
    harvard: string;
  };
}

interface CitationGap {
  id: string;
  section: string;
  sentence: string;
  gap_type: 'missing_citation' | 'weak_support' | 'outdated_citation';
  severity: 'high' | 'medium' | 'low';
  suggestion: string;
  suggested_citations: SuggestedCitation[];
}

interface AnalysisResult {
  total_citations_found: number;
  citations_suggested: number;
  gaps_identified: number;
  coverage_score: number;
  suggested_citations: SuggestedCitation[];
  gaps: CitationGap[];
  sections_analyzed: {
    name: string;
    citation_count: number;
    coverage: number;
  }[];
}

const CITATION_STYLES = [
  { value: 'apa', label: 'APA 7th' },
  { value: 'mla', label: 'MLA 9th' },
  { value: 'chicago', label: 'Chicago' },
  { value: 'harvard', label: 'Harvard' },
];

export default function CitationBooster(props: Props) {
  const [manuscriptText, setManuscriptText] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [selectedStyle, setSelectedStyle] = useState<string>('apa');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const analyzeManuscript = async () => {
    if (!manuscriptText.trim()) {
      setError('Please enter your manuscript text');
      return;
    }

    if (manuscriptText.trim().split(/\s+/).length < 100) {
      setError('Please enter at least 100 words for meaningful analysis');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiCall<AnalysisResult>(api.citationBooster.analyze, {
        method: 'POST',
        body: JSON.stringify({
          text: manuscriptText,
          citation_style: selectedStyle,
        }),
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const insertCitation = (citation: SuggestedCitation) => {
    const formattedCitation = citation.formatted_citation[selectedStyle as keyof typeof citation.formatted_citation];
    const insertText = `\n\n[CITATION: ${formattedCitation}]\n\n`;
    setManuscriptText(manuscriptText + insertText);
  };

  const getGapSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-blue-500';
      default:
        return 'bg-zinc-500';
    }
  };

  const getGapTypeIcon = (type: string) => {
    switch (type) {
      case 'missing_citation':
        return <HiOutlineExclamationTriangle className="h-4 w-4" />;
      case 'weak_support':
        return <HiOutlineLightBulb className="h-4 w-4" />;
      case 'outdated_citation':
        return <HiOutlineDocumentText className="h-4 w-4" />;
      default:
        return <HiOutlineExclamationTriangle className="h-4 w-4" />;
    }
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-500';
    if (score >= 0.6) return 'text-yellow-500';
    return 'text-zinc-500';
  };

  return (
    <DashboardLayout
      user={props.user}
      userDetails={props.userDetails}
      title="Citation Booster"
      description="Enhance your manuscript with relevant citations"
    >
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-zinc-950 dark:bg-white">
              <HiOutlineSparkles className="h-6 w-6 text-white dark:text-zinc-950" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-zinc-950 dark:text-white">Citation Booster</h1>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Find relevant citations and identify gaps in your manuscript
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
            {error}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Input Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HiOutlineDocumentText className="h-5 w-5" />
                Manuscript Input
              </CardTitle>
              <CardDescription>
                Paste your manuscript text for citation analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="Paste your manuscript text here. The AI will analyze it to suggest relevant citations and identify areas that need better citation support...

Example: Machine learning has revolutionized healthcare diagnostics. Deep learning models have shown remarkable accuracy in medical image analysis. However, challenges remain in ensuring model interpretability..."
                className="min-h-[350px] resize-none font-mono text-sm"
                value={manuscriptText}
                onChange={(e) => setManuscriptText(e.target.value)}
              />

              <div className="flex items-center justify-between text-sm text-zinc-500">
                <span>{manuscriptText.trim().split(/\s+/).filter(Boolean).length} words</span>
                <div className="flex gap-2">
                  {CITATION_STYLES.map((style) => (
                    <Badge
                      key={style.value}
                      variant={selectedStyle === style.value ? 'default' : 'outline'}
                      className="cursor-pointer"
                      onClick={() => setSelectedStyle(style.value)}
                    >
                      {style.label}
                    </Badge>
                  ))}
                </div>
              </div>

              <Button
                className="w-full"
                onClick={analyzeManuscript}
                disabled={loading || !manuscriptText.trim()}
              >
                {loading ? (
                  <>
                    <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <HiOutlineMagnifyingGlass className="mr-2 h-4 w-4" />
                    Analyze & Find Citations
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Results Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HiOutlineSparkles className="h-5 w-5" />
                Analysis Results
              </CardTitle>
              <CardDescription>
                Suggested citations and gap analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!result && !loading && (
                <div className="flex h-[350px] flex-col items-center justify-center text-center text-zinc-500">
                  <HiOutlineSparkles className="mb-4 h-16 w-16 opacity-20" />
                  <p>Enter your manuscript text and click analyze</p>
                  <p className="mt-2 text-xs">
                    We will suggest relevant citations and identify gaps
                  </p>
                </div>
              )}

              {loading && (
                <div className="flex h-[350px] flex-col items-center justify-center text-center">
                  <div className="mb-4 h-16 w-16 animate-spin rounded-full border-4 border-zinc-200 border-t-zinc-950 dark:border-zinc-700 dark:border-t-white" />
                  <p className="text-zinc-500">Analyzing your manuscript...</p>
                  <p className="mt-2 text-xs text-zinc-400">
                    Searching academic databases for relevant citations
                  </p>
                </div>
              )}

              {result && (
                <div className="space-y-4">
                  {/* Summary Stats */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="rounded-lg bg-zinc-50 p-3 text-center dark:bg-zinc-900">
                      <p className="text-2xl font-bold text-zinc-950 dark:text-white">
                        {result.citations_suggested}
                      </p>
                      <p className="text-xs text-zinc-500">Citations Suggested</p>
                    </div>
                    <div className="rounded-lg bg-zinc-50 p-3 text-center dark:bg-zinc-900">
                      <p className="text-2xl font-bold text-yellow-500">
                        {result.gaps_identified}
                      </p>
                      <p className="text-xs text-zinc-500">Gaps Found</p>
                    </div>
                    <div className="rounded-lg bg-zinc-50 p-3 text-center dark:bg-zinc-900">
                      <p className="text-2xl font-bold text-green-500">
                        {(result.coverage_score * 100).toFixed(0)}%
                      </p>
                      <p className="text-xs text-zinc-500">Coverage</p>
                    </div>
                  </div>

                  {/* Coverage by Section */}
                  {result.sections_analyzed.length > 0 && (
                    <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
                      <h4 className="mb-3 text-sm font-medium">Coverage by Section</h4>
                      <div className="space-y-2">
                        {result.sections_analyzed.map((section, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <span className="w-24 truncate text-xs">{section.name}</span>
                            <Progress value={section.coverage * 100} className="flex-1 h-2" />
                            <span className="w-12 text-right text-xs">
                              {section.citation_count} refs
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Detailed Results */}
        {result && (
          <Card>
            <CardContent className="pt-6">
              <Tabs defaultValue="suggestions" className="w-full">
                <TabsList className="w-full">
                  <TabsTrigger value="suggestions" className="flex-1">
                    <HiOutlinePlusCircle className="mr-2 h-4 w-4" />
                    Suggested Citations ({result.suggested_citations.length})
                  </TabsTrigger>
                  <TabsTrigger value="gaps" className="flex-1">
                    <HiOutlineExclamationTriangle className="mr-2 h-4 w-4" />
                    Citation Gaps ({result.gaps.length})
                  </TabsTrigger>
                </TabsList>

                {/* Suggested Citations Tab */}
                <TabsContent value="suggestions" className="space-y-4">
                  {result.suggested_citations.length === 0 ? (
                    <div className="py-8 text-center text-zinc-500">
                      <HiOutlineCheckCircle className="mx-auto mb-2 h-12 w-12 text-green-500 opacity-50" />
                      <p>Your manuscript is well-cited!</p>
                    </div>
                  ) : (
                    <div className="max-h-[500px] space-y-4 overflow-y-auto">
                      {result.suggested_citations.map((citation) => (
                        <div
                          key={citation.id}
                          className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800"
                        >
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <h4 className="font-medium text-zinc-950 dark:text-white">
                                {citation.title}
                              </h4>
                              <p className="mt-1 text-sm text-zinc-500">
                                {citation.authors.slice(0, 3).join(', ')}
                                {citation.authors.length > 3 && ' et al.'} ({citation.year})
                              </p>
                              <p className="text-xs text-zinc-400">{citation.journal}</p>

                              <div className="mt-2 flex items-center gap-2">
                                <span className={`text-sm font-semibold ${getRelevanceColor(citation.relevance_score)}`}>
                                  {(citation.relevance_score * 100).toFixed(0)}% relevant
                                </span>
                                {citation.doi && (
                                  <a
                                    href={`https://doi.org/${citation.doi}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs text-blue-500 hover:underline"
                                  >
                                    DOI
                                  </a>
                                )}
                              </div>

                              <p className="mt-2 text-xs text-zinc-600 dark:text-zinc-400">
                                <strong>Why relevant:</strong> {citation.relevance_reason}
                              </p>

                              {/* Formatted Citation */}
                              <div className="mt-3 rounded bg-zinc-50 p-2 dark:bg-zinc-900">
                                <p className="font-mono text-xs text-zinc-700 dark:text-zinc-300">
                                  {citation.formatted_citation[selectedStyle as keyof typeof citation.formatted_citation]}
                                </p>
                              </div>
                            </div>

                            <div className="flex flex-col gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() =>
                                  copyToClipboard(
                                    citation.formatted_citation[selectedStyle as keyof typeof citation.formatted_citation],
                                    citation.id
                                  )
                                }
                              >
                                {copiedId === citation.id ? (
                                  <>
                                    <HiOutlineCheckCircle className="mr-1 h-4 w-4 text-green-500" />
                                    Copied
                                  </>
                                ) : (
                                  <>
                                    <HiOutlineClipboardDocument className="mr-1 h-4 w-4" />
                                    Copy
                                  </>
                                )}
                              </Button>
                              <Button
                                size="sm"
                                onClick={() => insertCitation(citation)}
                              >
                                <HiOutlinePlusCircle className="mr-1 h-4 w-4" />
                                Insert
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </TabsContent>

                {/* Citation Gaps Tab */}
                <TabsContent value="gaps" className="space-y-4">
                  {result.gaps.length === 0 ? (
                    <div className="py-8 text-center text-zinc-500">
                      <HiOutlineCheckCircle className="mx-auto mb-2 h-12 w-12 text-green-500 opacity-50" />
                      <p>No citation gaps detected!</p>
                    </div>
                  ) : (
                    <div className="max-h-[500px] space-y-4 overflow-y-auto">
                      {result.gaps.map((gap) => (
                        <div
                          key={gap.id}
                          className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800"
                        >
                          <div className="flex items-start gap-3">
                            <div className={`mt-1 rounded-full p-1 text-white ${getGapSeverityColor(gap.severity)}`}>
                              {getGapTypeIcon(gap.gap_type)}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <Badge variant="outline" className="text-xs">
                                  {gap.section}
                                </Badge>
                                <Badge
                                  className={`${getGapSeverityColor(gap.severity)} text-xs text-white`}
                                >
                                  {gap.severity} priority
                                </Badge>
                              </div>

                              <div className="mt-2 rounded bg-yellow-50 p-2 dark:bg-yellow-900/20">
                                <p className="text-sm italic text-zinc-700 dark:text-zinc-300">
                                  {gap.sentence}
                                </p>
                              </div>

                              <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
                                <strong>Issue:</strong>{' '}
                                {gap.gap_type.replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase())}
                              </p>

                              <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                                <strong>Suggestion:</strong> {gap.suggestion}
                              </p>

                              {/* Suggested citations for this gap */}
                              {gap.suggested_citations.length > 0 && (
                                <div className="mt-3 space-y-2">
                                  <p className="text-xs font-medium text-zinc-500">
                                    Recommended citations:
                                  </p>
                                  {gap.suggested_citations.slice(0, 2).map((citation) => (
                                    <div
                                      key={citation.id}
                                      className="flex items-center justify-between rounded bg-zinc-50 p-2 dark:bg-zinc-900"
                                    >
                                      <div className="flex-1">
                                        <p className="text-xs font-medium line-clamp-1">
                                          {citation.title}
                                        </p>
                                        <p className="text-xs text-zinc-500">
                                          {citation.authors[0]} ({citation.year})
                                        </p>
                                      </div>
                                      <Button
                                        size="sm"
                                        variant="ghost"
                                        onClick={() => insertCitation(citation)}
                                      >
                                        <HiOutlinePlusCircle className="h-4 w-4" />
                                      </Button>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
