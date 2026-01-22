'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { api, apiCall } from '@/lib/api';
import { User } from '@supabase/supabase-js';
import { useToast } from '@/hooks/use-toast';
import {
  HiOutlineMagnifyingGlass,
  HiOutlineBookOpen,
  HiOutlineBookmarkSquare,
  HiOutlineArrowDownTray,
  HiOutlineCalendar,
  HiOutlineAcademicCap,
  HiOutlineLink,
  HiOutlineCheckCircle,
} from 'react-icons/hi2';

interface Props {
  user: User | null | undefined;
  userDetails: { [x: string]: any } | null;
}

interface Paper {
  id: string;
  title: string;
  authors: string[];
  year: number;
  abstract: string;
  source: string;
  doi?: string;
  url?: string;
  citations?: number;
  saved?: boolean;
}

interface SearchFilters {
  sources: string[];
  yearFrom: string;
  yearTo: string;
  sortBy: string;
}

const SOURCES = [
  { id: 'pubmed', name: 'PubMed', icon: '🔬' },
  { id: 'arxiv', name: 'arXiv', icon: '📄' },
  { id: 'semantic_scholar', name: 'Semantic Scholar', icon: '📚' },
];

const SORT_OPTIONS = [
  { value: 'relevance', label: 'Relevance' },
  { value: 'date_desc', label: 'Newest First' },
  { value: 'date_asc', label: 'Oldest First' },
  { value: 'citations', label: 'Most Cited' },
];

export default function LiteratureSearch({ user, userDetails }: Props) {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({
    sources: ['pubmed', 'arxiv', 'semantic_scholar'],
    yearFrom: '',
    yearTo: new Date().getFullYear().toString(),
    sortBy: 'relevance',
  });
  const [results, setResults] = useState<Paper[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedPapers, setSelectedPapers] = useState<Set<string>>(new Set());
  const [savingPapers, setSavingPapers] = useState<Set<string>>(new Set());

  const handleSourceToggle = (sourceId: string) => {
    setFilters((prev) => ({
      ...prev,
      sources: prev.sources.includes(sourceId)
        ? prev.sources.filter((s) => s !== sourceId)
        : [...prev.sources, sourceId],
    }));
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast({
        title: 'Search query required',
        description: 'Please enter a search term.',
        variant: 'destructive',
      });
      return;
    }

    if (filters.sources.length === 0) {
      toast({
        title: 'Select at least one source',
        description: 'Please select at least one database to search.',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsSearching(true);
      setHasSearched(true);

      const response = await apiCall<{ papers: Paper[] }>(api.literature.search, {
        method: 'POST',
        body: JSON.stringify({
          query: searchQuery,
          sources: filters.sources,
          year_from: filters.yearFrom ? parseInt(filters.yearFrom) : null,
          year_to: filters.yearTo ? parseInt(filters.yearTo) : null,
          sort_by: filters.sortBy,
        }),
      });

      setResults(response.papers);
      setSelectedPapers(new Set());
    } catch (error: any) {
      toast({
        title: 'Search failed',
        description: error.message || 'Failed to search literature.',
        variant: 'destructive',
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handleSavePaper = async (paper: Paper) => {
    try {
      setSavingPapers((prev) => new Set(prev).add(paper.id));

      await apiCall(api.literature.savePaper, {
        method: 'POST',
        body: JSON.stringify({
          paper_id: paper.id,
          title: paper.title,
          authors: paper.authors,
          year: paper.year,
          abstract: paper.abstract,
          source: paper.source,
          doi: paper.doi,
          url: paper.url,
        }),
      });

      setResults((prev) =>
        prev.map((p) => (p.id === paper.id ? { ...p, saved: true } : p))
      );

      toast({
        title: 'Paper saved',
        description: 'The paper has been added to your library.',
      });
    } catch (error: any) {
      toast({
        title: 'Save failed',
        description: error.message || 'Failed to save paper.',
        variant: 'destructive',
      });
    } finally {
      setSavingPapers((prev) => {
        const newSet = new Set(prev);
        newSet.delete(paper.id);
        return newSet;
      });
    }
  };

  const handleExportCitations = async () => {
    const papersToExport = results.filter((p) => selectedPapers.has(p.id));

    if (papersToExport.length === 0) {
      toast({
        title: 'No papers selected',
        description: 'Please select papers to export.',
        variant: 'destructive',
      });
      return;
    }

    try {
      const response = await apiCall<{ citations: string; format: string }>(
        api.literature.export,
        {
          method: 'POST',
          body: JSON.stringify({
            paper_ids: Array.from(selectedPapers),
            format: 'bibtex',
          }),
        }
      );

      // Download the citations file
      const blob = new Blob([response.citations], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'citations.bib';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: 'Citations exported',
        description: `Exported ${papersToExport.length} citations.`,
      });
    } catch (error: any) {
      toast({
        title: 'Export failed',
        description: error.message || 'Failed to export citations.',
        variant: 'destructive',
      });
    }
  };

  const togglePaperSelection = (paperId: string) => {
    setSelectedPapers((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(paperId)) {
        newSet.delete(paperId);
      } else {
        newSet.add(paperId);
      }
      return newSet;
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <DashboardLayout
      user={user}
      userDetails={userDetails}
      title="Literature Search"
      description="Search academic literature"
    >
      <div className="space-y-6">
        {/* Search Header */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <HiOutlineMagnifyingGlass className="h-5 w-5" />
              Search Academic Literature
            </CardTitle>
            <CardDescription>
              Search across multiple academic databases simultaneously
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Search Input */}
            <div className="flex gap-2">
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter your search query (e.g., machine learning healthcare)"
                className="flex-1"
              />
              <Button onClick={handleSearch} disabled={isSearching}>
                {isSearching ? 'Searching...' : 'Search'}
              </Button>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-6">
              {/* Source Selection */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">Sources</Label>
                <div className="flex gap-3">
                  {SOURCES.map((source) => (
                    <div
                      key={source.id}
                      className="flex items-center space-x-2"
                    >
                      <Checkbox
                        id={source.id}
                        checked={filters.sources.includes(source.id)}
                        onCheckedChange={() => handleSourceToggle(source.id)}
                      />
                      <label
                        htmlFor={source.id}
                        className="text-sm cursor-pointer"
                      >
                        {source.icon} {source.name}
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Year Range */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">Year Range</Label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    placeholder="From"
                    value={filters.yearFrom}
                    onChange={(e) =>
                      setFilters((prev) => ({ ...prev, yearFrom: e.target.value }))
                    }
                    className="w-24"
                  />
                  <span className="text-zinc-500">to</span>
                  <Input
                    type="number"
                    placeholder="To"
                    value={filters.yearTo}
                    onChange={(e) =>
                      setFilters((prev) => ({ ...prev, yearTo: e.target.value }))
                    }
                    className="w-24"
                  />
                </div>
              </div>

              {/* Sort By */}
              <div className="space-y-2">
                <Label className="text-sm font-medium">Sort By</Label>
                <Select
                  value={filters.sortBy}
                  onValueChange={(value) =>
                    setFilters((prev) => ({ ...prev, sortBy: value }))
                  }
                >
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {SORT_OPTIONS.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        {hasSearched && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <HiOutlineBookOpen className="h-5 w-5" />
                  Search Results
                </CardTitle>
                <CardDescription>
                  {isSearching
                    ? 'Searching...'
                    : `Found ${results.length} papers`}
                </CardDescription>
              </div>
              {selectedPapers.size > 0 && (
                <Button onClick={handleExportCitations} variant="outline">
                  <HiOutlineArrowDownTray className="mr-2 h-4 w-4" />
                  Export {selectedPapers.size} Citations
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {isSearching ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="space-y-3">
                      <Skeleton className="h-6 w-3/4" />
                      <Skeleton className="h-4 w-1/2" />
                      <Skeleton className="h-20 w-full" />
                    </div>
                  ))}
                </div>
              ) : results.length === 0 ? (
                <div className="text-center py-12 text-zinc-500">
                  <HiOutlineBookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No papers found. Try adjusting your search query or filters.</p>
                </div>
              ) : (
                <ScrollArea className="h-[600px]">
                  <div className="space-y-4 pr-4">
                    {results.map((paper) => (
                      <Card
                        key={paper.id}
                        className={`transition-colors ${
                          selectedPapers.has(paper.id)
                            ? 'border-zinc-900 dark:border-zinc-50'
                            : ''
                        }`}
                      >
                        <CardHeader className="pb-2">
                          <div className="flex items-start gap-3">
                            <Checkbox
                              checked={selectedPapers.has(paper.id)}
                              onCheckedChange={() => togglePaperSelection(paper.id)}
                              className="mt-1"
                            />
                            <div className="flex-1">
                              <CardTitle className="text-base font-semibold leading-tight">
                                {paper.title}
                              </CardTitle>
                              <div className="flex flex-wrap items-center gap-2 mt-2">
                                <Badge variant="secondary">
                                  {paper.source}
                                </Badge>
                                <span className="text-sm text-zinc-500 flex items-center gap-1">
                                  <HiOutlineCalendar className="h-3 w-3" />
                                  {paper.year}
                                </span>
                                {paper.citations !== undefined && (
                                  <span className="text-sm text-zinc-500 flex items-center gap-1">
                                    <HiOutlineAcademicCap className="h-3 w-3" />
                                    {paper.citations} citations
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent className="pb-2">
                          <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-2">
                            {paper.authors.join(', ')}
                          </p>
                          <p className="text-sm text-zinc-600 dark:text-zinc-400 line-clamp-3">
                            {paper.abstract}
                          </p>
                        </CardContent>
                        <CardFooter className="pt-2 flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleSavePaper(paper)}
                            disabled={paper.saved || savingPapers.has(paper.id)}
                          >
                            {paper.saved ? (
                              <>
                                <HiOutlineCheckCircle className="mr-2 h-4 w-4 text-green-500" />
                                Saved
                              </>
                            ) : savingPapers.has(paper.id) ? (
                              'Saving...'
                            ) : (
                              <>
                                <HiOutlineBookmarkSquare className="mr-2 h-4 w-4" />
                                Save
                              </>
                            )}
                          </Button>
                          {paper.url && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => window.open(paper.url, '_blank')}
                            >
                              <HiOutlineLink className="mr-2 h-4 w-4" />
                              View Source
                            </Button>
                          )}
                        </CardFooter>
                      </Card>
                    ))}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
