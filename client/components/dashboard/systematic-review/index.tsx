'use client';

import DashboardLayout from '@/components/layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { api, apiCall } from '@/lib/api';
import { User } from '@supabase/supabase-js';
import { useState, useEffect } from 'react';
import {
  HiOutlineClipboardDocumentList,
  HiOutlineMagnifyingGlass,
  HiOutlineDocumentPlus,
  HiOutlineTrash,
  HiOutlineCheck,
  HiOutlineXMark,
  HiOutlineArrowPath,
  HiOutlineFunnel,
  HiOutlineChartBar,
} from 'react-icons/hi2';

interface Props {
  user: User | null | undefined;
  userDetails: { [x: string]: any } | null;
}

interface Review {
  id: string;
  name: string;
  research_question: string;
  inclusion_criteria: string[];
  exclusion_criteria: string[];
  databases: string[];
  status: 'draft' | 'searching' | 'screening' | 'completed';
  created_at: string;
  updated_at: string;
}

interface Study {
  id: string;
  title: string;
  authors: string[];
  year: number;
  source: string;
  abstract: string;
  status: 'pending' | 'included' | 'excluded' | 'maybe';
  exclusion_reason?: string;
}

interface PrismaFlow {
  identification: {
    databases_searched: number;
    records_identified: number;
    duplicates_removed: number;
  };
  screening: {
    records_screened: number;
    records_excluded: number;
  };
  eligibility: {
    full_text_assessed: number;
    full_text_excluded: number;
    exclusion_reasons: { reason: string; count: number }[];
  };
  included: {
    studies_included: number;
  };
}

interface Statistics {
  total_studies: number;
  included: number;
  excluded: number;
  pending: number;
  maybe: number;
  by_year: { year: number; count: number }[];
  by_database: { database: string; count: number }[];
}

const DATABASES = [
  { value: 'pubmed', label: 'PubMed' },
  { value: 'scopus', label: 'Scopus' },
  { value: 'web_of_science', label: 'Web of Science' },
  { value: 'cochrane', label: 'Cochrane Library' },
  { value: 'embase', label: 'EMBASE' },
  { value: 'psycinfo', label: 'PsycINFO' },
  { value: 'ieee', label: 'IEEE Xplore' },
  { value: 'google_scholar', label: 'Google Scholar' },
];

export default function SystematicReview(props: Props) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [selectedReview, setSelectedReview] = useState<Review | null>(null);
  const [studies, setStudies] = useState<Study[]>([]);
  const [prismaFlow, setPrismaFlow] = useState<PrismaFlow | null>(null);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [searching, setSearching] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [showNewReview, setShowNewReview] = useState<boolean>(false);
  const [newReviewName, setNewReviewName] = useState<string>('');
  const [newResearchQuestion, setNewResearchQuestion] = useState<string>('');
  const [selectedDatabases, setSelectedDatabases] = useState<string[]>(['pubmed']);
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Screening state
  const [currentStudyIndex, setCurrentStudyIndex] = useState<number>(0);

  useEffect(() => {
    loadReviews();
  }, []);

  useEffect(() => {
    if (selectedReview) {
      loadStudies(selectedReview.id);
      loadPrismaFlow(selectedReview.id);
    }
  }, [selectedReview]);

  const loadReviews = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiCall<{ reviews: Review[] }>(api.systematicReview.reviews, {
        method: 'GET',
      });
      setReviews(response.reviews || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load reviews');
    } finally {
      setLoading(false);
    }
  };

  const createReview = async () => {
    if (!newReviewName.trim() || !newResearchQuestion.trim()) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await apiCall<Review>(api.systematicReview.reviews, {
        method: 'POST',
        body: JSON.stringify({
          name: newReviewName,
          research_question: newResearchQuestion,
          databases: selectedDatabases,
        }),
      });
      setReviews([response, ...reviews]);
      setSelectedReview(response);
      setNewReviewName('');
      setNewResearchQuestion('');
      setShowNewReview(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create review');
    } finally {
      setLoading(false);
    }
  };

  const deleteReview = async (reviewId: string) => {
    if (!confirm('Are you sure you want to delete this review?')) return;

    setLoading(true);
    try {
      await apiCall(api.systematicReview.review(reviewId), {
        method: 'DELETE',
      });
      setReviews(reviews.filter((r) => r.id !== reviewId));
      if (selectedReview?.id === reviewId) {
        setSelectedReview(null);
        setStudies([]);
        setPrismaFlow(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete review');
    } finally {
      setLoading(false);
    }
  };

  const loadStudies = async (reviewId: string) => {
    try {
      const response = await apiCall<{ studies: Study[]; statistics: Statistics }>(
        api.systematicReview.studies(reviewId),
        { method: 'GET' }
      );
      setStudies(response.studies || []);
      setStatistics(response.statistics || null);
    } catch (err) {
      console.error('Failed to load studies:', err);
    }
  };

  const loadPrismaFlow = async (reviewId: string) => {
    try {
      const response = await apiCall<PrismaFlow>(
        api.systematicReview.prismaFlow(reviewId),
        { method: 'GET' }
      );
      setPrismaFlow(response);
    } catch (err) {
      console.error('Failed to load PRISMA flow:', err);
    }
  };

  const performSearch = async () => {
    if (!selectedReview || !searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }

    setSearching(true);
    setError(null);
    try {
      const response = await apiCall<{ studies_found: number; message: string }>(
        api.systematicReview.search(selectedReview.id),
        {
          method: 'POST',
          body: JSON.stringify({
            query: searchQuery,
            databases: selectedReview.databases,
          }),
        }
      );
      await loadStudies(selectedReview.id);
      await loadPrismaFlow(selectedReview.id);
      alert(`Found ${response.studies_found} studies`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setSearching(false);
    }
  };

  const updateStudyStatus = async (studyId: string, status: Study['status'], reason?: string) => {
    if (!selectedReview) return;

    try {
      await apiCall(api.systematicReview.studies(selectedReview.id), {
        method: 'PATCH',
        body: JSON.stringify({
          study_id: studyId,
          status,
          exclusion_reason: reason,
        }),
      });
      setStudies(
        studies.map((s) =>
          s.id === studyId ? { ...s, status, exclusion_reason: reason } : s
        )
      );
      await loadPrismaFlow(selectedReview.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update study');
    }
  };

  const pendingStudies = studies.filter((s) => s.status === 'pending');
  const currentStudy = pendingStudies[currentStudyIndex];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'included':
        return 'bg-green-500';
      case 'excluded':
        return 'bg-red-500';
      case 'maybe':
        return 'bg-yellow-500';
      default:
        return 'bg-zinc-500';
    }
  };

  return (
    <DashboardLayout
      user={props.user}
      userDetails={props.userDetails}
      title="Systematic Review"
      description="Manage systematic literature reviews"
    >
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-zinc-950 dark:bg-white">
              <HiOutlineClipboardDocumentList className="h-6 w-6 text-white dark:text-zinc-950" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-zinc-950 dark:text-white">
                Systematic Review
              </h1>
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Conduct PRISMA-compliant systematic literature reviews
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
            {error}
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-4">
          {/* Reviews Panel */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Reviews</CardTitle>
                <Button
                  size="sm"
                  variant={showNewReview ? 'outline' : 'default'}
                  onClick={() => setShowNewReview(!showNewReview)}
                >
                  {showNewReview ? (
                    <HiOutlineXMark className="h-4 w-4" />
                  ) : (
                    <HiOutlineDocumentPlus className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {showNewReview && (
                <div className="space-y-3 rounded-lg border border-zinc-200 p-3 dark:border-zinc-800">
                  <Input
                    placeholder="Review name"
                    value={newReviewName}
                    onChange={(e) => setNewReviewName(e.target.value)}
                  />
                  <Textarea
                    placeholder="Research question"
                    value={newResearchQuestion}
                    onChange={(e) => setNewResearchQuestion(e.target.value)}
                    className="min-h-[60px]"
                  />
                  <div className="space-y-2">
                    <Label className="text-xs">Databases</Label>
                    <div className="flex flex-wrap gap-1">
                      {DATABASES.slice(0, 4).map((db) => (
                        <Badge
                          key={db.value}
                          variant={selectedDatabases.includes(db.value) ? 'default' : 'outline'}
                          className="cursor-pointer text-xs"
                          onClick={() =>
                            setSelectedDatabases(
                              selectedDatabases.includes(db.value)
                                ? selectedDatabases.filter((d) => d !== db.value)
                                : [...selectedDatabases, db.value]
                            )
                          }
                        >
                          {db.label}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <Button className="w-full" onClick={createReview} disabled={loading}>
                    Create Review
                  </Button>
                </div>
              )}

              <div className="max-h-[400px] space-y-2 overflow-y-auto">
                {reviews.length === 0 ? (
                  <div className="py-8 text-center text-sm text-zinc-500">
                    No reviews yet
                  </div>
                ) : (
                  reviews.map((review) => (
                    <div
                      key={review.id}
                      className={`cursor-pointer rounded-lg border p-3 transition-colors ${
                        selectedReview?.id === review.id
                          ? 'border-zinc-950 bg-zinc-50 dark:border-white dark:bg-zinc-900'
                          : 'border-zinc-200 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:bg-zinc-900'
                      }`}
                      onClick={() => setSelectedReview(review)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="text-sm font-medium text-zinc-950 dark:text-white">
                            {review.name}
                          </h3>
                          <Badge variant="outline" className="mt-1 text-xs">
                            {review.status}
                          </Badge>
                        </div>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteReview(review.id);
                          }}
                        >
                          <HiOutlineTrash className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* Main Content */}
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle>
                {selectedReview ? selectedReview.name : 'Select a Review'}
              </CardTitle>
              {selectedReview && (
                <CardDescription className="line-clamp-2">
                  {selectedReview.research_question}
                </CardDescription>
              )}
            </CardHeader>
            <CardContent>
              {!selectedReview ? (
                <div className="flex h-[400px] flex-col items-center justify-center text-center text-zinc-500">
                  <HiOutlineClipboardDocumentList className="mb-4 h-16 w-16 opacity-20" />
                  <p>Select a review to get started</p>
                </div>
              ) : (
                <Tabs defaultValue="search" className="w-full">
                  <TabsList className="w-full">
                    <TabsTrigger value="search" className="flex-1">
                      <HiOutlineMagnifyingGlass className="mr-2 h-4 w-4" />
                      Search
                    </TabsTrigger>
                    <TabsTrigger value="screening" className="flex-1">
                      <HiOutlineFunnel className="mr-2 h-4 w-4" />
                      Screening
                    </TabsTrigger>
                    <TabsTrigger value="prisma" className="flex-1">
                      <HiOutlineArrowPath className="mr-2 h-4 w-4" />
                      PRISMA
                    </TabsTrigger>
                    <TabsTrigger value="statistics" className="flex-1">
                      <HiOutlineChartBar className="mr-2 h-4 w-4" />
                      Statistics
                    </TabsTrigger>
                  </TabsList>

                  {/* Search Tab */}
                  <TabsContent value="search" className="space-y-4">
                    <div className="space-y-4">
                      <div className="flex gap-2">
                        <Input
                          placeholder="Enter search query (e.g., machine learning AND healthcare)"
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          className="flex-1"
                        />
                        <Button onClick={performSearch} disabled={searching}>
                          {searching ? (
                            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                          ) : (
                            <HiOutlineMagnifyingGlass className="h-4 w-4" />
                          )}
                        </Button>
                      </div>

                      <div className="flex flex-wrap gap-2">
                        <span className="text-sm text-zinc-500">Databases:</span>
                        {selectedReview.databases.map((db) => (
                          <Badge key={db} variant="secondary" className="text-xs">
                            {DATABASES.find((d) => d.value === db)?.label || db}
                          </Badge>
                        ))}
                      </div>

                      <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
                        <h4 className="mb-2 font-medium">Search Results</h4>
                        <p className="text-sm text-zinc-500">
                          {studies.length} studies found
                        </p>
                        <div className="mt-4 max-h-[300px] space-y-2 overflow-y-auto">
                          {studies.slice(0, 10).map((study) => (
                            <div
                              key={study.id}
                              className="rounded border border-zinc-200 p-3 dark:border-zinc-800"
                            >
                              <div className="flex items-start justify-between gap-2">
                                <div>
                                  <h5 className="text-sm font-medium">{study.title}</h5>
                                  <p className="text-xs text-zinc-500">
                                    {study.authors.slice(0, 3).join(', ')}
                                    {study.authors.length > 3 && ' et al.'} ({study.year})
                                  </p>
                                </div>
                                <Badge className={getStatusColor(study.status)}>
                                  {study.status}
                                </Badge>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </TabsContent>

                  {/* Screening Tab */}
                  <TabsContent value="screening" className="space-y-4">
                    <div className="mb-4 flex items-center justify-between">
                      <div>
                        <p className="text-sm text-zinc-500">
                          {pendingStudies.length} studies to screen
                        </p>
                        <Progress
                          value={
                            ((studies.length - pendingStudies.length) / Math.max(studies.length, 1)) * 100
                          }
                          className="mt-2 h-2 w-48"
                        />
                      </div>
                      <div className="flex gap-2">
                        <Badge variant="outline" className="border-green-500 text-green-500">
                          Included: {studies.filter((s) => s.status === 'included').length}
                        </Badge>
                        <Badge variant="outline" className="border-red-500 text-red-500">
                          Excluded: {studies.filter((s) => s.status === 'excluded').length}
                        </Badge>
                      </div>
                    </div>

                    {currentStudy ? (
                      <div className="rounded-lg border border-zinc-200 p-6 dark:border-zinc-800">
                        <div className="mb-4">
                          <Badge variant="secondary" className="mb-2">
                            {currentStudyIndex + 1} of {pendingStudies.length}
                          </Badge>
                          <h3 className="text-lg font-semibold">{currentStudy.title}</h3>
                          <p className="mt-1 text-sm text-zinc-500">
                            {currentStudy.authors.join(', ')} ({currentStudy.year})
                          </p>
                          <p className="mt-1 text-xs text-zinc-400">
                            Source: {currentStudy.source}
                          </p>
                        </div>

                        <div className="mb-6">
                          <h4 className="mb-2 text-sm font-medium">Abstract</h4>
                          <p className="text-sm text-zinc-600 dark:text-zinc-400">
                            {currentStudy.abstract || 'No abstract available'}
                          </p>
                        </div>

                        <div className="flex gap-3">
                          <Button
                            variant="outline"
                            className="flex-1 border-green-500 text-green-500 hover:bg-green-50"
                            onClick={() => {
                              updateStudyStatus(currentStudy.id, 'included');
                              setCurrentStudyIndex(Math.min(currentStudyIndex, pendingStudies.length - 2));
                            }}
                          >
                            <HiOutlineCheck className="mr-2 h-4 w-4" />
                            Include
                          </Button>
                          <Button
                            variant="outline"
                            className="flex-1 border-yellow-500 text-yellow-500 hover:bg-yellow-50"
                            onClick={() => {
                              updateStudyStatus(currentStudy.id, 'maybe');
                              setCurrentStudyIndex(Math.min(currentStudyIndex, pendingStudies.length - 2));
                            }}
                          >
                            Maybe
                          </Button>
                          <Button
                            variant="outline"
                            className="flex-1 border-red-500 text-red-500 hover:bg-red-50"
                            onClick={() => {
                              const reason = prompt('Exclusion reason (optional):');
                              updateStudyStatus(currentStudy.id, 'excluded', reason || undefined);
                              setCurrentStudyIndex(Math.min(currentStudyIndex, pendingStudies.length - 2));
                            }}
                          >
                            <HiOutlineXMark className="mr-2 h-4 w-4" />
                            Exclude
                          </Button>
                        </div>

                        <div className="mt-4 flex justify-between">
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={currentStudyIndex === 0}
                            onClick={() => setCurrentStudyIndex(currentStudyIndex - 1)}
                          >
                            Previous
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={currentStudyIndex >= pendingStudies.length - 1}
                            onClick={() => setCurrentStudyIndex(currentStudyIndex + 1)}
                          >
                            Skip
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex h-[300px] flex-col items-center justify-center text-center text-zinc-500">
                        <HiOutlineCheck className="mb-4 h-16 w-16 text-green-500 opacity-50" />
                        <p>All studies have been screened!</p>
                      </div>
                    )}
                  </TabsContent>

                  {/* PRISMA Flow Tab */}
                  <TabsContent value="prisma" className="space-y-4">
                    {prismaFlow ? (
                      <div className="space-y-4">
                        {/* PRISMA Flow Diagram */}
                        <div className="flex flex-col items-center space-y-4">
                          {/* Identification */}
                          <div className="w-full max-w-md rounded-lg border-2 border-blue-500 bg-blue-50 p-4 text-center dark:bg-blue-900/20">
                            <h4 className="font-semibold text-blue-700 dark:text-blue-400">
                              Identification
                            </h4>
                            <p className="mt-2 text-sm">
                              Records identified: {prismaFlow.identification.records_identified}
                            </p>
                            <p className="text-sm">
                              Databases searched: {prismaFlow.identification.databases_searched}
                            </p>
                            <p className="text-sm text-zinc-500">
                              Duplicates removed: {prismaFlow.identification.duplicates_removed}
                            </p>
                          </div>

                          <div className="h-8 w-0.5 bg-zinc-300 dark:bg-zinc-700" />

                          {/* Screening */}
                          <div className="w-full max-w-md rounded-lg border-2 border-yellow-500 bg-yellow-50 p-4 text-center dark:bg-yellow-900/20">
                            <h4 className="font-semibold text-yellow-700 dark:text-yellow-400">
                              Screening
                            </h4>
                            <p className="mt-2 text-sm">
                              Records screened: {prismaFlow.screening.records_screened}
                            </p>
                            <p className="text-sm text-zinc-500">
                              Records excluded: {prismaFlow.screening.records_excluded}
                            </p>
                          </div>

                          <div className="h-8 w-0.5 bg-zinc-300 dark:bg-zinc-700" />

                          {/* Eligibility */}
                          <div className="w-full max-w-md rounded-lg border-2 border-orange-500 bg-orange-50 p-4 text-center dark:bg-orange-900/20">
                            <h4 className="font-semibold text-orange-700 dark:text-orange-400">
                              Eligibility
                            </h4>
                            <p className="mt-2 text-sm">
                              Full-text assessed: {prismaFlow.eligibility.full_text_assessed}
                            </p>
                            <p className="text-sm text-zinc-500">
                              Full-text excluded: {prismaFlow.eligibility.full_text_excluded}
                            </p>
                          </div>

                          <div className="h-8 w-0.5 bg-zinc-300 dark:bg-zinc-700" />

                          {/* Included */}
                          <div className="w-full max-w-md rounded-lg border-2 border-green-500 bg-green-50 p-4 text-center dark:bg-green-900/20">
                            <h4 className="font-semibold text-green-700 dark:text-green-400">
                              Included
                            </h4>
                            <p className="mt-2 text-2xl font-bold text-green-600">
                              {prismaFlow.included.studies_included}
                            </p>
                            <p className="text-sm">studies included</p>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex h-[300px] flex-col items-center justify-center text-center text-zinc-500">
                        <HiOutlineArrowPath className="mb-4 h-16 w-16 opacity-20" />
                        <p>Run a search to generate PRISMA flow diagram</p>
                      </div>
                    )}
                  </TabsContent>

                  {/* Statistics Tab */}
                  <TabsContent value="statistics" className="space-y-4">
                    {statistics ? (
                      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        <Card>
                          <CardContent className="pt-6">
                            <div className="text-center">
                              <p className="text-3xl font-bold">{statistics.total_studies}</p>
                              <p className="text-sm text-zinc-500">Total Studies</p>
                            </div>
                          </CardContent>
                        </Card>
                        <Card>
                          <CardContent className="pt-6">
                            <div className="text-center">
                              <p className="text-3xl font-bold text-green-500">
                                {statistics.included}
                              </p>
                              <p className="text-sm text-zinc-500">Included</p>
                            </div>
                          </CardContent>
                        </Card>
                        <Card>
                          <CardContent className="pt-6">
                            <div className="text-center">
                              <p className="text-3xl font-bold text-red-500">
                                {statistics.excluded}
                              </p>
                              <p className="text-sm text-zinc-500">Excluded</p>
                            </div>
                          </CardContent>
                        </Card>
                        <Card>
                          <CardContent className="pt-6">
                            <div className="text-center">
                              <p className="text-3xl font-bold text-yellow-500">
                                {statistics.pending}
                              </p>
                              <p className="text-sm text-zinc-500">Pending</p>
                            </div>
                          </CardContent>
                        </Card>

                        {/* By Year Chart */}
                        <Card className="sm:col-span-2">
                          <CardHeader>
                            <CardTitle className="text-sm">Studies by Year</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="flex items-end gap-1 h-32">
                              {statistics.by_year.map((item) => (
                                <div
                                  key={item.year}
                                  className="flex-1 bg-zinc-950 dark:bg-white rounded-t"
                                  style={{
                                    height: `${(item.count / Math.max(...statistics.by_year.map(y => y.count))) * 100}%`,
                                    minHeight: '8px'
                                  }}
                                  title={`${item.year}: ${item.count} studies`}
                                />
                              ))}
                            </div>
                            <div className="flex justify-between mt-2 text-xs text-zinc-500">
                              <span>{statistics.by_year[0]?.year}</span>
                              <span>{statistics.by_year[statistics.by_year.length - 1]?.year}</span>
                            </div>
                          </CardContent>
                        </Card>

                        {/* By Database */}
                        <Card className="sm:col-span-2">
                          <CardHeader>
                            <CardTitle className="text-sm">Studies by Database</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-2">
                              {statistics.by_database.map((item) => (
                                <div key={item.database} className="flex items-center gap-2">
                                  <span className="w-24 text-xs truncate">{item.database}</span>
                                  <Progress
                                    value={(item.count / statistics.total_studies) * 100}
                                    className="flex-1 h-2"
                                  />
                                  <span className="w-8 text-xs text-right">{item.count}</span>
                                </div>
                              ))}
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    ) : (
                      <div className="flex h-[300px] flex-col items-center justify-center text-center text-zinc-500">
                        <HiOutlineChartBar className="mb-4 h-16 w-16 opacity-20" />
                        <p>No statistics available yet</p>
                      </div>
                    )}
                  </TabsContent>
                </Tabs>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
