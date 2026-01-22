'use client';

import DashboardLayout from '@/components/layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { api, apiCall, uploadFile } from '@/lib/api';
import { User } from '@supabase/supabase-js';
import { useState } from 'react';
import { HiOutlineShieldCheck, HiOutlineDocumentText, HiOutlineSparkles, HiOutlineUser } from 'react-icons/hi2';

interface Props {
  user: User | null | undefined;
  userDetails: { [x: string]: any } | null;
}

interface SentenceAnalysis {
  text: string;
  ai_probability: number;
  classification: 'ai' | 'human' | 'mixed';
}

interface DetectionResult {
  overall_ai_probability: number;
  overall_human_probability: number;
  verdict: 'AI Generated' | 'Human Written' | 'Mixed Content';
  confidence: number;
  sentences: SentenceAnalysis[];
  word_count: number;
  analysis_timestamp: string;
}

export default function AIDetector(props: Props) {
  const [inputText, setInputText] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleAnalyzeText = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text to analyze.');
      return;
    }

    if (inputText.trim().split(/\s+/).length < 50) {
      setError('Please enter at least 50 words for accurate detection.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiCall<DetectionResult>(api.aiDetector.detectText, {
        method: 'POST',
        body: JSON.stringify({ text: inputText }),
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.match(/\.(txt|doc|docx|pdf)$/i)) {
      setError('Please upload a TXT, DOC, DOCX, or PDF file.');
      return;
    }

    setSelectedFile(file);
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await uploadFile(api.aiDetector.detectFile, file);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'File analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'AI Generated':
        return 'bg-red-500';
      case 'Human Written':
        return 'bg-green-500';
      case 'Mixed Content':
        return 'bg-yellow-500';
      default:
        return 'bg-zinc-500';
    }
  };

  const getSentenceHighlight = (classification: string) => {
    switch (classification) {
      case 'ai':
        return 'bg-red-100 dark:bg-red-900/30 border-l-4 border-red-500';
      case 'human':
        return 'bg-green-100 dark:bg-green-900/30 border-l-4 border-green-500';
      case 'mixed':
        return 'bg-yellow-100 dark:bg-yellow-900/30 border-l-4 border-yellow-500';
      default:
        return '';
    }
  };

  return (
    <DashboardLayout
      user={props.user}
      userDetails={props.userDetails}
      title="AI Detector"
      description="Detect AI-generated content in academic writing"
    >
      <div className="mx-auto max-w-6xl space-y-6">
        {/* Header */}
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-zinc-950 dark:bg-white">
            <HiOutlineShieldCheck className="h-6 w-6 text-white dark:text-zinc-950" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-zinc-950 dark:text-white">AI Content Detector</h1>
            <p className="text-sm text-zinc-500 dark:text-zinc-400">
              Analyze text to detect AI-generated content with sentence-level precision
            </p>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Input Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HiOutlineDocumentText className="h-5 w-5" />
                Input Text
              </CardTitle>
              <CardDescription>
                Paste your text below or upload a document for analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="Paste your academic text here for AI detection analysis... (minimum 50 words recommended for accurate results)"
                className="min-h-[300px] resize-none"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
              />

              <div className="flex items-center justify-between text-sm text-zinc-500">
                <span>{inputText.trim().split(/\s+/).filter(Boolean).length} words</span>
                <span>{inputText.length} characters</span>
              </div>

              <div className="flex flex-col gap-3 sm:flex-row">
                <Button
                  className="flex-1"
                  onClick={handleAnalyzeText}
                  disabled={loading || !inputText.trim()}
                >
                  {loading ? (
                    <>
                      <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <HiOutlineShieldCheck className="mr-2 h-4 w-4" />
                      Analyze Text
                    </>
                  )}
                </Button>

                <div className="relative flex-1">
                  <input
                    type="file"
                    accept=".txt,.doc,.docx,.pdf"
                    onChange={handleFileUpload}
                    className="absolute inset-0 cursor-pointer opacity-0"
                    disabled={loading}
                  />
                  <Button variant="outline" className="w-full" disabled={loading}>
                    <HiOutlineDocumentText className="mr-2 h-4 w-4" />
                    Upload Document
                  </Button>
                </div>
              </div>

              {selectedFile && (
                <p className="text-sm text-zinc-500">
                  Selected file: {selectedFile.name}
                </p>
              )}

              {error && (
                <div className="rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
                  {error}
                </div>
              )}
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
                Detection results with confidence scores
              </CardDescription>
            </CardHeader>
            <CardContent>
              {!result && !loading && (
                <div className="flex h-[300px] flex-col items-center justify-center text-center text-zinc-500">
                  <HiOutlineShieldCheck className="mb-4 h-16 w-16 opacity-20" />
                  <p>Enter text or upload a document to see analysis results</p>
                </div>
              )}

              {loading && (
                <div className="flex h-[300px] flex-col items-center justify-center text-center">
                  <div className="mb-4 h-16 w-16 animate-spin rounded-full border-4 border-zinc-200 border-t-zinc-950 dark:border-zinc-700 dark:border-t-white" />
                  <p className="text-zinc-500">Analyzing content...</p>
                </div>
              )}

              {result && (
                <div className="space-y-6">
                  {/* Verdict */}
                  <div className="text-center">
                    <Badge
                      className={`${getVerdictColor(result.verdict)} px-4 py-2 text-lg text-white`}
                    >
                      {result.verdict}
                    </Badge>
                    <p className="mt-2 text-sm text-zinc-500">
                      Confidence: {(result.confidence * 100).toFixed(1)}%
                    </p>
                  </div>

                  {/* Probability Bars */}
                  <div className="space-y-4">
                    <div>
                      <div className="mb-2 flex items-center justify-between text-sm">
                        <span className="flex items-center gap-2">
                          <HiOutlineSparkles className="h-4 w-4 text-red-500" />
                          AI Probability
                        </span>
                        <span className="font-semibold text-red-500">
                          {(result.overall_ai_probability * 100).toFixed(1)}%
                        </span>
                      </div>
                      <Progress
                        value={result.overall_ai_probability * 100}
                        className="h-3 [&>div]:bg-red-500"
                      />
                    </div>

                    <div>
                      <div className="mb-2 flex items-center justify-between text-sm">
                        <span className="flex items-center gap-2">
                          <HiOutlineUser className="h-4 w-4 text-green-500" />
                          Human Probability
                        </span>
                        <span className="font-semibold text-green-500">
                          {(result.overall_human_probability * 100).toFixed(1)}%
                        </span>
                      </div>
                      <Progress
                        value={result.overall_human_probability * 100}
                        className="h-3 [&>div]:bg-green-500"
                      />
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-4 rounded-lg bg-zinc-50 p-4 dark:bg-zinc-900">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-zinc-950 dark:text-white">
                        {result.word_count}
                      </p>
                      <p className="text-sm text-zinc-500">Words Analyzed</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-zinc-950 dark:text-white">
                        {result.sentences.length}
                      </p>
                      <p className="text-sm text-zinc-500">Sentences</p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Highlighted Sentences */}
        {result && result.sentences.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Sentence-Level Analysis</CardTitle>
              <CardDescription>
                Each sentence is highlighted based on its AI probability
              </CardDescription>
              <div className="mt-2 flex flex-wrap gap-2">
                <Badge variant="outline" className="border-red-500 text-red-500">
                  AI Generated
                </Badge>
                <Badge variant="outline" className="border-green-500 text-green-500">
                  Human Written
                </Badge>
                <Badge variant="outline" className="border-yellow-500 text-yellow-500">
                  Mixed/Uncertain
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="max-h-[400px] space-y-2 overflow-y-auto">
                {result.sentences.map((sentence, index) => (
                  <div
                    key={index}
                    className={`rounded-r-lg p-3 ${getSentenceHighlight(sentence.classification)}`}
                  >
                    <p className="text-sm text-zinc-700 dark:text-zinc-300">
                      {sentence.text}
                    </p>
                    <p className="mt-1 text-xs text-zinc-500">
                      AI Probability: {(sentence.ai_probability * 100).toFixed(1)}%
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
