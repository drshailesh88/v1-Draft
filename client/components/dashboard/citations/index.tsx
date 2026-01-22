'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
  HiOutlineBookOpen,
  HiOutlineMagnifyingGlass,
  HiOutlineClipboardDocument,
  HiOutlineArrowDownTray,
  HiOutlineSparkles,
  HiOutlineTrash,
  HiOutlinePlusCircle,
} from 'react-icons/hi2';

interface Props {
  user: User | null | undefined;
  userDetails: { [x: string]: any } | null;
}

interface CitationMetadata {
  title: string;
  authors: string;
  year: string;
  journal?: string;
  volume?: string;
  issue?: string;
  pages?: string;
  doi?: string;
  url?: string;
  publisher?: string;
  type: 'article' | 'book' | 'website' | 'conference';
}

interface GeneratedCitation {
  id: string;
  metadata: CitationMetadata;
  citations: { [style: string]: string };
  created_at: string;
}

const CITATION_STYLES = [
  { value: 'apa', label: 'APA 7th Edition' },
  { value: 'mla', label: 'MLA 9th Edition' },
  { value: 'chicago', label: 'Chicago 17th Edition' },
  { value: 'ieee', label: 'IEEE' },
  { value: 'harvard', label: 'Harvard' },
  { value: 'vancouver', label: 'Vancouver' },
  { value: 'ama', label: 'AMA 11th Edition' },
  { value: 'acs', label: 'ACS' },
];

const SOURCE_TYPES = [
  { value: 'article', label: 'Journal Article' },
  { value: 'book', label: 'Book' },
  { value: 'website', label: 'Website' },
  { value: 'conference', label: 'Conference Paper' },
];

const initialMetadata: CitationMetadata = {
  title: '',
  authors: '',
  year: '',
  journal: '',
  volume: '',
  issue: '',
  pages: '',
  doi: '',
  url: '',
  publisher: '',
  type: 'article',
};

export default function CitationGenerator({ user, userDetails }: Props) {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('doi');
  const [doiInput, setDoiInput] = useState('');
  const [metadata, setMetadata] = useState<CitationMetadata>(initialMetadata);
  const [selectedStyle, setSelectedStyle] = useState('apa');
  const [generatedCitation, setGeneratedCitation] = useState<string>('');
  const [allStylesCitations, setAllStylesCitations] = useState<{ [key: string]: string }>({});
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [savedCitations, setSavedCitations] = useState<GeneratedCitation[]>([]);
  const [isLoadingSaved, setIsLoadingSaved] = useState(true);

  useEffect(() => {
    fetchSavedCitations();
  }, []);

  const fetchSavedCitations = async () => {
    try {
      setIsLoadingSaved(true);
      const data = await apiCall<GeneratedCitation[]>(api.citations.saved);
      setSavedCitations(data);
    } catch (error) {
      console.error('Error fetching saved citations:', error);
    } finally {
      setIsLoadingSaved(false);
    }
  };

  const handleDoiLookup = async () => {
    if (!doiInput.trim()) {
      toast({
        title: 'DOI required',
        description: 'Please enter a DOI to look up.',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsLookingUp(true);
      const response = await apiCall<{ metadata: CitationMetadata }>(
        api.citations.doiLookup,
        {
          method: 'POST',
          body: JSON.stringify({ doi: doiInput.trim() }),
        }
      );

      setMetadata(response.metadata);
      setActiveTab('manual');
      toast({
        title: 'DOI found',
        description: 'Metadata has been populated. Review and generate citation.',
      });
    } catch (error: any) {
      toast({
        title: 'Lookup failed',
        description: error.message || 'Could not find metadata for this DOI.',
        variant: 'destructive',
      });
    } finally {
      setIsLookingUp(false);
    }
  };

  const handleGenerateCitation = async () => {
    if (!metadata.title || !metadata.authors || !metadata.year) {
      toast({
        title: 'Missing required fields',
        description: 'Please fill in at least title, authors, and year.',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsGenerating(true);
      const response = await apiCall<{
        citation: string;
        all_styles: { [key: string]: string };
      }>(api.citations.generate, {
        method: 'POST',
        body: JSON.stringify({
          metadata,
          style: selectedStyle,
        }),
      });

      setGeneratedCitation(response.citation);
      setAllStylesCitations(response.all_styles);
      toast({
        title: 'Citation generated',
        description: 'Your citation is ready to use.',
      });
    } catch (error: any) {
      toast({
        title: 'Generation failed',
        description: error.message || 'Failed to generate citation.',
        variant: 'destructive',
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: 'Copied',
        description: 'Citation copied to clipboard.',
      });
    } catch (error) {
      toast({
        title: 'Copy failed',
        description: 'Failed to copy to clipboard.',
        variant: 'destructive',
      });
    }
  };

  const handleExportCitations = async (format: 'bibtex' | 'ris' | 'endnote') => {
    if (!generatedCitation) {
      toast({
        title: 'No citation to export',
        description: 'Generate a citation first.',
        variant: 'destructive',
      });
      return;
    }

    try {
      const response = await apiCall<{ content: string; filename: string }>(
        api.citations.export,
        {
          method: 'POST',
          body: JSON.stringify({
            metadata,
            format,
          }),
        }
      );

      const blob = new Blob([response.content], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: 'Exported',
        description: `Citation exported as ${format.toUpperCase()}.`,
      });
    } catch (error: any) {
      toast({
        title: 'Export failed',
        description: error.message || 'Failed to export citation.',
        variant: 'destructive',
      });
    }
  };

  const handleClearForm = () => {
    setMetadata(initialMetadata);
    setDoiInput('');
    setGeneratedCitation('');
    setAllStylesCitations({});
  };

  const updateMetadata = (field: keyof CitationMetadata, value: string) => {
    setMetadata((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <DashboardLayout
      user={user}
      userDetails={userDetails}
      title="Citation Generator"
      description="Generate citations in multiple formats"
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Section */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HiOutlineBookOpen className="h-5 w-5" />
                Create Citation
              </CardTitle>
              <CardDescription>
                Enter a DOI for automatic lookup or fill in details manually
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="mb-4">
                  <TabsTrigger value="doi">DOI Lookup</TabsTrigger>
                  <TabsTrigger value="manual">Manual Entry</TabsTrigger>
                </TabsList>

                <TabsContent value="doi" className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="doi">DOI (Digital Object Identifier)</Label>
                    <div className="flex gap-2">
                      <Input
                        id="doi"
                        value={doiInput}
                        onChange={(e) => setDoiInput(e.target.value)}
                        placeholder="e.g., 10.1000/xyz123"
                        className="flex-1"
                      />
                      <Button onClick={handleDoiLookup} disabled={isLookingUp}>
                        <HiOutlineMagnifyingGlass className="mr-2 h-4 w-4" />
                        {isLookingUp ? 'Looking up...' : 'Lookup'}
                      </Button>
                    </div>
                    <p className="text-xs text-zinc-500">
                      Enter the DOI of the publication to automatically fetch citation details
                    </p>
                  </div>
                </TabsContent>

                <TabsContent value="manual" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2 space-y-2">
                      <Label htmlFor="type">Source Type</Label>
                      <Select
                        value={metadata.type}
                        onValueChange={(value) =>
                          updateMetadata('type', value as CitationMetadata['type'])
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {SOURCE_TYPES.map((type) => (
                            <SelectItem key={type.value} value={type.value}>
                              {type.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="md:col-span-2 space-y-2">
                      <Label htmlFor="title">Title *</Label>
                      <Input
                        id="title"
                        value={metadata.title}
                        onChange={(e) => updateMetadata('title', e.target.value)}
                        placeholder="Enter the title of the work"
                      />
                    </div>

                    <div className="md:col-span-2 space-y-2">
                      <Label htmlFor="authors">Authors *</Label>
                      <Input
                        id="authors"
                        value={metadata.authors}
                        onChange={(e) => updateMetadata('authors', e.target.value)}
                        placeholder="e.g., Smith, John; Doe, Jane"
                      />
                      <p className="text-xs text-zinc-500">
                        Separate multiple authors with semicolons
                      </p>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="year">Year *</Label>
                      <Input
                        id="year"
                        value={metadata.year}
                        onChange={(e) => updateMetadata('year', e.target.value)}
                        placeholder="e.g., 2024"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="journal">
                        {metadata.type === 'book' ? 'Publisher' : 'Journal/Source'}
                      </Label>
                      <Input
                        id="journal"
                        value={metadata.journal}
                        onChange={(e) => updateMetadata('journal', e.target.value)}
                        placeholder={
                          metadata.type === 'book'
                            ? 'e.g., Oxford University Press'
                            : 'e.g., Nature'
                        }
                      />
                    </div>

                    {metadata.type === 'article' && (
                      <>
                        <div className="space-y-2">
                          <Label htmlFor="volume">Volume</Label>
                          <Input
                            id="volume"
                            value={metadata.volume}
                            onChange={(e) => updateMetadata('volume', e.target.value)}
                            placeholder="e.g., 12"
                          />
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="issue">Issue</Label>
                          <Input
                            id="issue"
                            value={metadata.issue}
                            onChange={(e) => updateMetadata('issue', e.target.value)}
                            placeholder="e.g., 3"
                          />
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="pages">Pages</Label>
                          <Input
                            id="pages"
                            value={metadata.pages}
                            onChange={(e) => updateMetadata('pages', e.target.value)}
                            placeholder="e.g., 123-145"
                          />
                        </div>
                      </>
                    )}

                    <div className="space-y-2">
                      <Label htmlFor="metadata-doi">DOI</Label>
                      <Input
                        id="metadata-doi"
                        value={metadata.doi}
                        onChange={(e) => updateMetadata('doi', e.target.value)}
                        placeholder="e.g., 10.1000/xyz123"
                      />
                    </div>

                    {(metadata.type === 'website' || metadata.type === 'article') && (
                      <div className="md:col-span-2 space-y-2">
                        <Label htmlFor="url">URL</Label>
                        <Input
                          id="url"
                          value={metadata.url}
                          onChange={(e) => updateMetadata('url', e.target.value)}
                          placeholder="https://..."
                        />
                      </div>
                    )}
                  </div>
                </TabsContent>
              </Tabs>

              <div className="flex items-center justify-between mt-6 pt-4 border-t">
                <div className="flex items-center gap-4">
                  <div className="space-y-1">
                    <Label>Citation Style</Label>
                    <Select value={selectedStyle} onValueChange={setSelectedStyle}>
                      <SelectTrigger className="w-48">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {CITATION_STYLES.map((style) => (
                          <SelectItem key={style.value} value={style.value}>
                            {style.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={handleClearForm}>
                    <HiOutlineTrash className="mr-2 h-4 w-4" />
                    Clear
                  </Button>
                  <Button onClick={handleGenerateCitation} disabled={isGenerating}>
                    <HiOutlineSparkles className="mr-2 h-4 w-4" />
                    {isGenerating ? 'Generating...' : 'Generate Citation'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Generated Citation */}
          {generatedCitation && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <HiOutlineBookOpen className="h-5 w-5" />
                    Generated Citation
                  </span>
                  <Badge>{CITATION_STYLES.find((s) => s.value === selectedStyle)?.label}</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-zinc-50 dark:bg-zinc-900 rounded-lg p-4 border">
                  <p className="text-sm leading-relaxed">{generatedCitation}</p>
                </div>

                <div className="flex flex-wrap gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCopyToClipboard(generatedCitation)}
                  >
                    <HiOutlineClipboardDocument className="mr-2 h-4 w-4" />
                    Copy
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExportCitations('bibtex')}
                  >
                    <HiOutlineArrowDownTray className="mr-2 h-4 w-4" />
                    BibTeX
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExportCitations('ris')}
                  >
                    <HiOutlineArrowDownTray className="mr-2 h-4 w-4" />
                    RIS
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExportCitations('endnote')}
                  >
                    <HiOutlineArrowDownTray className="mr-2 h-4 w-4" />
                    EndNote
                  </Button>
                </div>

                {/* All Styles Preview */}
                {Object.keys(allStylesCitations).length > 0 && (
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">All Citation Styles</Label>
                    <div className="space-y-2 max-h-[300px] overflow-y-auto">
                      {CITATION_STYLES.map((style) => {
                        const citation = allStylesCitations[style.value];
                        if (!citation) return null;
                        return (
                          <div
                            key={style.value}
                            className="bg-zinc-50 dark:bg-zinc-900 rounded p-3 border"
                          >
                            <div className="flex items-center justify-between mb-2">
                              <Badge variant="secondary" className="text-xs">
                                {style.label}
                              </Badge>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleCopyToClipboard(citation)}
                                className="h-6 px-2"
                              >
                                <HiOutlineClipboardDocument className="h-3 w-3" />
                              </Button>
                            </div>
                            <p className="text-xs text-zinc-600 dark:text-zinc-400">
                              {citation}
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Saved Citations Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <HiOutlineBookOpen className="h-5 w-5" />
                Recent Citations
              </CardTitle>
              <CardDescription>Your recently generated citations</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingSaved ? (
                <div className="space-y-3">
                  <Skeleton className="h-20 w-full" />
                  <Skeleton className="h-20 w-full" />
                  <Skeleton className="h-20 w-full" />
                </div>
              ) : savedCitations.length === 0 ? (
                <div className="text-center py-8 text-zinc-500">
                  <HiOutlinePlusCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No saved citations yet</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {savedCitations.map((citation) => (
                    <div
                      key={citation.id}
                      className="p-3 bg-zinc-50 dark:bg-zinc-900 rounded-lg border cursor-pointer hover:border-zinc-300 dark:hover:border-zinc-700 transition-colors"
                      onClick={() => {
                        setMetadata(citation.metadata);
                        setAllStylesCitations(citation.citations);
                        setGeneratedCitation(
                          citation.citations[selectedStyle] || Object.values(citation.citations)[0]
                        );
                        setActiveTab('manual');
                      }}
                    >
                      <p className="text-sm font-medium truncate">{citation.metadata.title}</p>
                      <p className="text-xs text-zinc-500 truncate">
                        {citation.metadata.authors}
                      </p>
                      <p className="text-xs text-zinc-500">{citation.metadata.year}</p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
