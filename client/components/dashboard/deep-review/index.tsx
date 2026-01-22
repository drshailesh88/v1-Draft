'use client';

import { useState, useRef } from 'react';
import DashboardLayout from '@/components/layout';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { User } from '@supabase/supabase-js';
import { api, apiCall, uploadFile } from '@/lib/api';
import {
  HiOutlineDocumentMagnifyingGlass,
  HiOutlineCloudArrowUp,
  HiOutlineDocumentText,
  HiOutlineCheckCircle,
  HiOutlineExclamationCircle,
  HiOutlineArrowDownTray,
  HiOutlineBeaker,
  HiOutlinePencilSquare,
  HiOutlineChartBar,
  HiOutlineScale,
  HiOutlineLightBulb,
  HiOutlineArrowPath,
} from 'react-icons/hi2';

interface Props {
  user: User | null | undefined;
  userDetails: { [x: string]: any } | null;
}

interface ReviewPerspective {
  name: string;
  score: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
}

interface Suggestion {
  priority: 'high' | 'medium' | 'low';
  category: string;
  description: string;
  recommendation: string;
}

interface ReviewResult {
  id: string;
  overallScore: number;
  perspectives: {
    methodology: ReviewPerspective;
    domain: ReviewPerspective;
    writing: ReviewPerspective;
    statistical: ReviewPerspective;
    ethics: ReviewPerspective;
  };
  overallStrengths: string[];
  overallWeaknesses: string[];
  suggestions: Suggestion[];
}

const PERSPECTIVE_ICONS: Record<string, React.ReactNode> = {
  methodology: <HiOutlineBeaker className="h-5 w-5" />,
  domain: <HiOutlineLightBulb className="h-5 w-5" />,
  writing: <HiOutlinePencilSquare className="h-5 w-5" />,
  statistical: <HiOutlineChartBar className="h-5 w-5" />,
  ethics: <HiOutlineScale className="h-5 w-5" />,
};

const PERSPECTIVE_LABELS: Record<string, string> = {
  methodology: 'Methodology',
  domain: 'Domain Expertise',
  writing: 'Writing Quality',
  statistical: 'Statistical Analysis',
  ethics: 'Research Ethics',
};

export default function DeepReview(props: Props) {
  const [inputMethod, setInputMethod] = useState<'text' | 'file'>('text');
  const [inputText, setInputText] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [reviewResult, setReviewResult] = useState<ReviewResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (inputMethod === 'text' && !inputText.trim()) {
      setError('Please enter text to analyze.');
      return;
    }
    if (inputMethod === 'file' && !selectedFile) {
      setError('Please select a file to analyze.');
      return;
    }

    setLoading(true);
    setError(null);
    setReviewResult(null);

    try {
      let response: ReviewResult;

      if (inputMethod === 'file' && selectedFile) {
        response = await uploadFile(api.deepReview.analyzeFile, selectedFile);
      } else {
        response = await apiCall<ReviewResult>(api.deepReview.analyze, {
          method: 'POST',
          body: JSON.stringify({ text: inputText }),
        });
      }

      setReviewResult(response);
      setActiveTab('overview');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleExportReport = async () => {
    if (!reviewResult) return;

    try {
      const response = await fetch(api.deepReview.export, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewId: reviewResult.id }),
      });

      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `deep-review-report-${reviewResult.id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Failed to export report. Please try again.');
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 dark:text-green-400';
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const getProgressColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'destructive';
      case 'medium':
        return 'warning';
      case 'low':
        return 'secondary';
      default:
        return 'secondary';
    }
  };

  return (
    <DashboardLayout
      user={props.user}
      userDetails={props.userDetails}
      title="Deep Review"
      description="AI-powered academic paper review"
    >
      <div className="mx-auto max-w-6xl px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-zinc-950 dark:text-white">
            Deep Review
          </h1>
          <p className="mt-2 text-zinc-500 dark:text-zinc-400">
            Get comprehensive multi-perspective feedback on your research paper.
          </p>
        </div>

        {!reviewResult ? (
          <Card className="dark:border-zinc-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HiOutlineDocumentMagnifyingGlass className="h-5 w-5" />
                Submit for Review
              </CardTitle>
              <CardDescription>
                Upload a document or paste your text for analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Input Method Toggle */}
              <div className="flex gap-2">
                <Button
                  variant={inputMethod === 'text' ? 'default' : 'outline'}
                  onClick={() => setInputMethod('text')}
                  className="flex-1"
                >
                  <HiOutlineDocumentText className="mr-2 h-4 w-4" />
                  Paste Text
                </Button>
                <Button
                  variant={inputMethod === 'file' ? 'default' : 'outline'}
                  onClick={() => setInputMethod('file')}
                  className="flex-1"
                >
                  <HiOutlineCloudArrowUp className="mr-2 h-4 w-4" />
                  Upload File
                </Button>
              </div>

              {/* Text Input */}
              {inputMethod === 'text' && (
                <div className="space-y-2">
                  <Label htmlFor="paper-text">Paper Content</Label>
                  <Textarea
                    id="paper-text"
                    placeholder="Paste your research paper text here..."
                    className="min-h-[300px] resize-none"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                  />
                  <p className="text-xs text-zinc-500">
                    {inputText.length} characters
                  </p>
                </div>
              )}

              {/* File Upload */}
              {inputMethod === 'file' && (
                <div className="space-y-4">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="flex min-h-[200px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-zinc-300 bg-zinc-50 transition-colors hover:border-zinc-400 hover:bg-zinc-100 dark:border-zinc-700 dark:bg-zinc-900 dark:hover:border-zinc-600 dark:hover:bg-zinc-800"
                  >
                    <HiOutlineCloudArrowUp className="mb-4 h-12 w-12 text-zinc-400" />
                    <p className="mb-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
                      Click to upload or drag and drop
                    </p>
                    <p className="text-xs text-zinc-500">
                      PDF, DOC, DOCX, or TXT (max 10MB)
                    </p>
                  </div>
                  {selectedFile && (
                    <div className="flex items-center gap-2 rounded-lg bg-zinc-100 p-3 dark:bg-zinc-800">
                      <HiOutlineDocumentText className="h-5 w-5 text-zinc-500" />
                      <span className="flex-1 text-sm">{selectedFile.name}</span>
                      <Badge variant="secondary">
                        {(selectedFile.size / 1024).toFixed(1)} KB
                      </Badge>
                    </div>
                  )}
                </div>
              )}

              {error && (
                <div className="rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
                  {error}
                </div>
              )}

              <Button
                className="w-full"
                onClick={handleAnalyze}
                disabled={loading || (inputMethod === 'text' ? !inputText.trim() : !selectedFile)}
              >
                {loading ? (
                  <>
                    <HiOutlineArrowPath className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <HiOutlineDocumentMagnifyingGlass className="mr-2 h-4 w-4" />
                    Analyze Paper
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {/* Overall Score Card */}
            <Card className="dark:border-zinc-800">
              <CardContent className="py-6">
                <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
                  <div className="flex items-center gap-6">
                    <div className="relative flex h-32 w-32 items-center justify-center rounded-full border-8 border-zinc-200 dark:border-zinc-700">
                      <span className={`text-4xl font-bold ${getScoreColor(reviewResult.overallScore)}`}>
                        {reviewResult.overallScore}
                      </span>
                      <span className="absolute bottom-2 text-sm text-zinc-500">/100</span>
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-zinc-950 dark:text-white">
                        Quality Score
                      </h2>
                      <p className="text-zinc-500 dark:text-zinc-400">
                        Based on multi-perspective analysis
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={() => setReviewResult(null)}>
                      New Review
                    </Button>
                    <Button onClick={handleExportReport}>
                      <HiOutlineArrowDownTray className="mr-2 h-4 w-4" />
                      Export Report
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Detailed Review Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-3 lg:grid-cols-7">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="methodology">Methodology</TabsTrigger>
                <TabsTrigger value="domain">Domain</TabsTrigger>
                <TabsTrigger value="writing">Writing</TabsTrigger>
                <TabsTrigger value="statistical">Statistical</TabsTrigger>
                <TabsTrigger value="ethics">Ethics</TabsTrigger>
                <TabsTrigger value="suggestions">Suggestions</TabsTrigger>
              </TabsList>

              {/* Overview Tab */}
              <TabsContent value="overview" className="space-y-6">
                {/* Perspective Scores */}
                <Card className="dark:border-zinc-800">
                  <CardHeader>
                    <CardTitle>Review Perspectives</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {Object.entries(reviewResult.perspectives).map(([key, perspective]) => (
                      <div key={key} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {PERSPECTIVE_ICONS[key]}
                            <span className="font-medium">{PERSPECTIVE_LABELS[key]}</span>
                          </div>
                          <span className={`font-bold ${getScoreColor(perspective.score)}`}>
                            {perspective.score}/100
                          </span>
                        </div>
                        <div className="relative h-2 w-full overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-700">
                          <div
                            className={`h-full transition-all ${getProgressColor(perspective.score)}`}
                            style={{ width: `${perspective.score}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Strengths & Weaknesses */}
                <div className="grid gap-6 md:grid-cols-2">
                  <Card className="dark:border-zinc-800">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-green-600 dark:text-green-400">
                        <HiOutlineCheckCircle className="h-5 w-5" />
                        Key Strengths
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {reviewResult.overallStrengths.map((strength, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm">
                            <HiOutlineCheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-green-500" />
                            <span>{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>

                  <Card className="dark:border-zinc-800">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-orange-600 dark:text-orange-400">
                        <HiOutlineExclamationCircle className="h-5 w-5" />
                        Areas for Improvement
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {reviewResult.overallWeaknesses.map((weakness, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm">
                            <HiOutlineExclamationCircle className="mt-0.5 h-4 w-4 shrink-0 text-orange-500" />
                            <span>{weakness}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              {/* Individual Perspective Tabs */}
              {Object.entries(reviewResult.perspectives).map(([key, perspective]) => (
                <TabsContent key={key} value={key} className="space-y-6">
                  <Card className="dark:border-zinc-800">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="flex items-center gap-2">
                          {PERSPECTIVE_ICONS[key]}
                          {PERSPECTIVE_LABELS[key]}
                        </CardTitle>
                        <Badge className={getScoreColor(perspective.score)}>
                          Score: {perspective.score}/100
                        </Badge>
                      </div>
                      <CardDescription>{perspective.summary}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="grid gap-6 md:grid-cols-2">
                        <div>
                          <h4 className="mb-3 flex items-center gap-2 font-medium text-green-600 dark:text-green-400">
                            <HiOutlineCheckCircle className="h-4 w-4" />
                            Strengths
                          </h4>
                          <ul className="space-y-2">
                            {perspective.strengths.map((item, index) => (
                              <li key={index} className="text-sm text-zinc-600 dark:text-zinc-300">
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="mb-3 flex items-center gap-2 font-medium text-orange-600 dark:text-orange-400">
                            <HiOutlineExclamationCircle className="h-4 w-4" />
                            Weaknesses
                          </h4>
                          <ul className="space-y-2">
                            {perspective.weaknesses.map((item, index) => (
                              <li key={index} className="text-sm text-zinc-600 dark:text-zinc-300">
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      <div>
                        <h4 className="mb-3 flex items-center gap-2 font-medium text-blue-600 dark:text-blue-400">
                          <HiOutlineLightBulb className="h-4 w-4" />
                          Recommendations
                        </h4>
                        <ul className="space-y-2">
                          {perspective.suggestions.map((item, index) => (
                            <li
                              key={index}
                              className="rounded-lg bg-blue-50 p-3 text-sm text-blue-800 dark:bg-blue-900/20 dark:text-blue-200"
                            >
                              {item}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              ))}

              {/* Suggestions Tab */}
              <TabsContent value="suggestions">
                <Card className="dark:border-zinc-800">
                  <CardHeader>
                    <CardTitle>Improvement Suggestions</CardTitle>
                    <CardDescription>
                      Prioritized recommendations to improve your paper
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {reviewResult.suggestions
                        .sort((a, b) => {
                          const order = { high: 0, medium: 1, low: 2 };
                          return order[a.priority] - order[b.priority];
                        })
                        .map((suggestion, index) => (
                          <div
                            key={index}
                            className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-700"
                          >
                            <div className="mb-2 flex items-center gap-2">
                              <Badge variant={getPriorityColor(suggestion.priority) as any}>
                                {suggestion.priority.toUpperCase()}
                              </Badge>
                              <Badge variant="outline">{suggestion.category}</Badge>
                            </div>
                            <p className="mb-2 font-medium text-zinc-900 dark:text-white">
                              {suggestion.description}
                            </p>
                            <p className="text-sm text-zinc-600 dark:text-zinc-400">
                              <strong>Recommendation:</strong> {suggestion.recommendation}
                            </p>
                          </div>
                        ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
