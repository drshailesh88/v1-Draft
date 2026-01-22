'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/layout';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { User } from '@supabase/supabase-js';
import { api, apiCall } from '@/lib/api';
import {
  HiOutlineArrowPath,
  HiOutlineClipboard,
  HiOutlineCheck,
  HiOutlineDocumentDuplicate,
} from 'react-icons/hi2';

interface Props {
  user: User | null | undefined;
  userDetails: { [x: string]: any } | null;
}

interface ParaphraseVariation {
  id: string;
  text: string;
  mode: string;
  wordCount: number;
}

interface ParaphraseResponse {
  variations: ParaphraseVariation[];
  originalWordCount: number;
}

const PARAPHRASE_MODES = [
  { value: 'standard', label: 'Standard', description: 'Balanced rewriting' },
  { value: 'academic', label: 'Academic', description: 'Formal scholarly tone' },
  { value: 'simplified', label: 'Simplified', description: 'Easier to understand' },
  { value: 'formal', label: 'Formal', description: 'Professional language' },
  { value: 'creative', label: 'Creative', description: 'More expressive style' },
];

export default function Paraphraser(props: Props) {
  const [inputText, setInputText] = useState('');
  const [mode, setMode] = useState('standard');
  const [variations, setVariations] = useState<ParaphraseVariation[]>([]);
  const [originalWordCount, setOriginalWordCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const countWords = (text: string) => {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  };

  const handleParaphrase = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text to paraphrase.');
      return;
    }

    setLoading(true);
    setError(null);
    setVariations([]);

    try {
      const response = await apiCall<ParaphraseResponse>(api.paraphraser.paraphrase, {
        method: 'POST',
        body: JSON.stringify({
          text: inputText,
          mode: mode,
          num_variations: 3,
        }),
      });

      setVariations(response.variations);
      setOriginalWordCount(response.originalWordCount);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to paraphrase text. Please try again.');
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

  const getWordCountDiff = (newCount: number) => {
    const diff = newCount - originalWordCount;
    if (diff === 0) return null;
    return diff > 0 ? `+${diff}` : `${diff}`;
  };

  const inputWordCount = countWords(inputText);

  return (
    <DashboardLayout
      user={props.user}
      userDetails={props.userDetails}
      title="Paraphraser"
      description="Rewrite text in different styles"
    >
      <div className="mx-auto max-w-6xl px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-zinc-950 dark:text-white">
            Paraphraser
          </h1>
          <p className="mt-2 text-zinc-500 dark:text-zinc-400">
            Transform your text into different styles while preserving the original meaning.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Input Section */}
          <Card className="dark:border-zinc-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HiOutlineDocumentDuplicate className="h-5 w-5" />
                Original Text
              </CardTitle>
              <CardDescription>
                Enter the text you want to paraphrase
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="mode">Paraphrase Mode</Label>
                <Select value={mode} onValueChange={setMode}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a mode" />
                  </SelectTrigger>
                  <SelectContent>
                    {PARAPHRASE_MODES.map((m) => (
                      <SelectItem key={m.value} value={m.value}>
                        <div className="flex flex-col">
                          <span className="font-medium">{m.label}</span>
                          <span className="text-xs text-zinc-500">{m.description}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="input-text">Your Text</Label>
                  <Badge variant="secondary" className="text-xs">
                    {inputWordCount} words
                  </Badge>
                </div>
                <Textarea
                  id="input-text"
                  placeholder="Paste or type your text here..."
                  className="min-h-[250px] resize-none"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                />
              </div>

              <Button
                className="w-full"
                onClick={handleParaphrase}
                disabled={loading || !inputText.trim()}
              >
                {loading ? (
                  <>
                    <HiOutlineArrowPath className="mr-2 h-4 w-4 animate-spin" />
                    Paraphrasing...
                  </>
                ) : (
                  <>
                    <HiOutlineArrowPath className="mr-2 h-4 w-4" />
                    Paraphrase Text
                  </>
                )}
              </Button>

              {error && (
                <div className="rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
                  {error}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Output Section */}
          <Card className="dark:border-zinc-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <HiOutlineArrowPath className="h-5 w-5" />
                Paraphrased Variations
              </CardTitle>
              <CardDescription>
                {variations.length > 0
                  ? `${variations.length} variations generated`
                  : 'Your paraphrased text will appear here'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {variations.length === 0 && !loading ? (
                <div className="flex min-h-[300px] items-center justify-center rounded-lg border border-dashed border-zinc-200 dark:border-zinc-800">
                  <p className="text-sm text-zinc-500 dark:text-zinc-400">
                    Enter text and click Paraphrase to see variations
                  </p>
                </div>
              ) : loading ? (
                <div className="flex min-h-[300px] items-center justify-center">
                  <div className="text-center">
                    <HiOutlineArrowPath className="mx-auto h-8 w-8 animate-spin text-zinc-400" />
                    <p className="mt-2 text-sm text-zinc-500">Generating variations...</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {variations.map((variation, index) => (
                    <div
                      key={variation.id}
                      className="rounded-lg border border-zinc-200 bg-zinc-50 p-4 dark:border-zinc-700 dark:bg-zinc-900"
                    >
                      <div className="mb-2 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            Variation {index + 1}
                          </Badge>
                          <Badge variant="secondary" className="text-xs">
                            {variation.wordCount} words
                            {getWordCountDiff(variation.wordCount) && (
                              <span className={`ml-1 ${
                                variation.wordCount > originalWordCount
                                  ? 'text-green-600 dark:text-green-400'
                                  : 'text-orange-600 dark:text-orange-400'
                              }`}>
                                ({getWordCountDiff(variation.wordCount)})
                              </span>
                            )}
                          </Badge>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyToClipboard(variation.text, variation.id)}
                        >
                          {copiedId === variation.id ? (
                            <>
                              <HiOutlineCheck className="mr-1 h-4 w-4 text-green-500" />
                              Copied
                            </>
                          ) : (
                            <>
                              <HiOutlineClipboard className="mr-1 h-4 w-4" />
                              Copy
                            </>
                          )}
                        </Button>
                      </div>
                      <p className="text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">
                        {variation.text}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Word Count Comparison */}
              {variations.length > 0 && (
                <div className="mt-4 rounded-lg bg-zinc-100 p-4 dark:bg-zinc-800">
                  <h4 className="mb-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
                    Word Count Comparison
                  </h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-zinc-600 dark:text-zinc-400">Original</span>
                      <span className="font-medium">{originalWordCount} words</span>
                    </div>
                    {variations.map((variation, index) => (
                      <div key={variation.id} className="flex items-center justify-between text-sm">
                        <span className="text-zinc-600 dark:text-zinc-400">
                          Variation {index + 1}
                        </span>
                        <span className="font-medium">
                          {variation.wordCount} words
                          {getWordCountDiff(variation.wordCount) && (
                            <span className={`ml-2 text-xs ${
                              variation.wordCount > originalWordCount
                                ? 'text-green-600 dark:text-green-400'
                                : 'text-orange-600 dark:text-orange-400'
                            }`}>
                              ({getWordCountDiff(variation.wordCount)})
                            </span>
                          )}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Mode Descriptions */}
        <Card className="mt-6 dark:border-zinc-800">
          <CardHeader>
            <CardTitle className="text-lg">Paraphrase Modes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-5">
              {PARAPHRASE_MODES.map((m) => (
                <div
                  key={m.value}
                  className={`rounded-lg border p-4 ${
                    mode === m.value
                      ? 'border-zinc-950 bg-zinc-50 dark:border-zinc-50 dark:bg-zinc-900'
                      : 'border-zinc-200 dark:border-zinc-800'
                  }`}
                >
                  <h4 className="font-medium text-zinc-900 dark:text-white">{m.label}</h4>
                  <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
                    {m.description}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
