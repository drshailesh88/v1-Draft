'use client';

import { useState, useRef } from 'react';
import DashboardLayout from '@/components/layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { api, uploadFile, apiCall } from '@/lib/api';
import { User } from '@supabase/supabase-js';
import { useToast } from '@/hooks/use-toast';
import {
  HiOutlineTableCells,
  HiOutlinePhoto,
  HiOutlineCloudArrowUp,
  HiOutlineArrowDownTray,
  HiOutlineDocumentText,
  HiOutlineTrash,
  HiOutlineEye,
  HiOutlineDocumentArrowDown,
} from 'react-icons/hi2';

interface Props {
  user: User | null | undefined;
  userDetails: { [x: string]: any } | null;
}

interface ExtractedTable {
  id: string;
  page: number;
  title?: string;
  headers: string[];
  rows: string[][];
  confidence: number;
}

interface ExtractedFigure {
  id: string;
  page: number;
  caption?: string;
  image_url: string;
  type: string;
  confidence: number;
}

interface UploadedDocument {
  id: string;
  filename: string;
  page_count: number;
  upload_date: string;
}

export default function DataExtraction({ user, userDetails }: Props) {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('tables');
  const [uploadedDocument, setUploadedDocument] = useState<UploadedDocument | null>(null);
  const [tables, setTables] = useState<ExtractedTable[]>([]);
  const [figures, setFigures] = useState<ExtractedFigure[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractionProgress, setExtractionProgress] = useState(0);
  const [selectedTable, setSelectedTable] = useState<ExtractedTable | null>(null);
  const [selectedFigure, setSelectedFigure] = useState<ExtractedFigure | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      toast({
        title: 'Invalid file type',
        description: 'Please upload a PDF file.',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsUploading(true);
      setTables([]);
      setFigures([]);
      setSelectedTable(null);
      setSelectedFigure(null);

      // Upload and extract in one step
      const result = await uploadFile(api.dataExtraction.extractTables, file);

      setUploadedDocument({
        id: result.document_id,
        filename: file.name,
        page_count: result.page_count,
        upload_date: new Date().toISOString(),
      });

      toast({
        title: 'Upload successful',
        description: `${file.name} has been uploaded. Starting extraction...`,
      });

      // Extract data
      await extractData(result.document_id);
    } catch (error: any) {
      toast({
        title: 'Upload failed',
        description: error.message || 'Failed to upload document.',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const extractData = async (documentId: string) => {
    try {
      setIsExtracting(true);
      setExtractionProgress(10);

      // Extract tables
      const tablesResult = await apiCall<{ tables: ExtractedTable[] }>(
        api.dataExtraction.extractTables,
        {
          method: 'POST',
          body: JSON.stringify({ document_id: documentId }),
        }
      );
      setTables(tablesResult.tables);
      setExtractionProgress(50);

      // Extract figures
      const figuresResult = await apiCall<{ figures: ExtractedFigure[] }>(
        api.dataExtraction.extractFigures,
        {
          method: 'POST',
          body: JSON.stringify({ document_id: documentId }),
        }
      );
      setFigures(figuresResult.figures);
      setExtractionProgress(100);

      toast({
        title: 'Extraction complete',
        description: `Found ${tablesResult.tables.length} tables and ${figuresResult.figures.length} figures.`,
      });
    } catch (error: any) {
      toast({
        title: 'Extraction failed',
        description: error.message || 'Failed to extract data.',
        variant: 'destructive',
      });
    } finally {
      setIsExtracting(false);
      setExtractionProgress(0);
    }
  };

  const handleExportTable = async (table: ExtractedTable, format: 'csv' | 'excel') => {
    try {
      const endpoint = format === 'csv' ? api.dataExtraction.exportCsv : api.dataExtraction.exportExcel;

      const response = await apiCall<{ content: string; filename: string }>(endpoint, {
        method: 'POST',
        body: JSON.stringify({
          table_id: table.id,
          headers: table.headers,
          rows: table.rows,
        }),
      });

      // For CSV, we can handle it directly
      if (format === 'csv') {
        const blob = new Blob([response.content], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = response.filename || `table_${table.id}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        // For Excel, the response should be a download URL or base64
        const blob = new Blob([atob(response.content)], {
          type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = response.filename || `table_${table.id}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }

      toast({
        title: 'Export successful',
        description: `Table exported as ${format.toUpperCase()}.`,
      });
    } catch (error: any) {
      toast({
        title: 'Export failed',
        description: error.message || 'Failed to export table.',
        variant: 'destructive',
      });
    }
  };

  const handleExportAllTables = async (format: 'csv' | 'excel') => {
    for (const table of tables) {
      await handleExportTable(table, format);
    }
  };

  const handleDownloadFigure = (figure: ExtractedFigure) => {
    const a = document.createElement('a');
    a.href = figure.image_url;
    a.download = `figure_page${figure.page}_${figure.id}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const handleClearDocument = () => {
    setUploadedDocument(null);
    setTables([]);
    setFigures([]);
    setSelectedTable(null);
    setSelectedFigure(null);
  };

  return (
    <DashboardLayout
      user={user}
      userDetails={userDetails}
      title="Data Extraction"
      description="Extract tables and figures from PDFs"
    >
      <div className="space-y-6">
        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <HiOutlineTableCells className="h-5 w-5" />
              Extract Data from PDF
            </CardTitle>
            <CardDescription>
              Upload a PDF to automatically extract tables and figures
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!uploadedDocument ? (
              <div className="border-2 border-dashed border-zinc-200 dark:border-zinc-700 rounded-lg p-8 text-center">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <HiOutlineDocumentText className="h-12 w-12 mx-auto mb-4 text-zinc-400" />
                <h3 className="text-lg font-medium mb-2">Upload a PDF Document</h3>
                <p className="text-sm text-zinc-500 mb-4">
                  Drop your PDF here or click to browse
                </p>
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                >
                  <HiOutlineCloudArrowUp className="mr-2 h-4 w-4" />
                  {isUploading ? 'Uploading...' : 'Select PDF'}
                </Button>
              </div>
            ) : (
              <div className="flex items-center justify-between bg-zinc-50 dark:bg-zinc-900 rounded-lg p-4">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-lg bg-zinc-200 dark:bg-zinc-700 flex items-center justify-center">
                    <HiOutlineDocumentText className="h-6 w-6 text-zinc-500" />
                  </div>
                  <div>
                    <p className="font-medium">{uploadedDocument.filename}</p>
                    <p className="text-sm text-zinc-500">
                      {uploadedDocument.page_count} pages
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {isExtracting && (
                    <div className="flex items-center gap-2">
                      <div className="w-32 h-2 bg-zinc-200 dark:bg-zinc-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-zinc-900 dark:bg-zinc-50 transition-all duration-300"
                          style={{ width: `${extractionProgress}%` }}
                        />
                      </div>
                      <span className="text-sm text-zinc-500">{extractionProgress}%</span>
                    </div>
                  )}
                  <Button variant="outline" onClick={handleClearDocument}>
                    <HiOutlineTrash className="mr-2 h-4 w-4" />
                    Remove
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results Section */}
        {uploadedDocument && !isExtracting && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Extracted Content</CardTitle>
                  <CardDescription>
                    Found {tables.length} tables and {figures.length} figures
                  </CardDescription>
                </div>
                {tables.length > 0 && (
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleExportAllTables('csv')}
                    >
                      <HiOutlineArrowDownTray className="mr-2 h-4 w-4" />
                      Export All (CSV)
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleExportAllTables('excel')}
                    >
                      <HiOutlineDocumentArrowDown className="mr-2 h-4 w-4" />
                      Export All (Excel)
                    </Button>
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList>
                  <TabsTrigger value="tables" className="flex items-center gap-2">
                    <HiOutlineTableCells className="h-4 w-4" />
                    Tables ({tables.length})
                  </TabsTrigger>
                  <TabsTrigger value="figures" className="flex items-center gap-2">
                    <HiOutlinePhoto className="h-4 w-4" />
                    Figures ({figures.length})
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="tables" className="mt-4">
                  {tables.length === 0 ? (
                    <div className="text-center py-12 text-zinc-500">
                      <HiOutlineTableCells className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No tables found in this document</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      {/* Table List */}
                      <ScrollArea className="h-[500px]">
                        <div className="space-y-2 pr-4">
                          {tables.map((table) => (
                            <Card
                              key={table.id}
                              className={`cursor-pointer transition-colors ${
                                selectedTable?.id === table.id
                                  ? 'border-zinc-900 dark:border-zinc-50'
                                  : 'hover:border-zinc-300 dark:hover:border-zinc-700'
                              }`}
                              onClick={() => setSelectedTable(table)}
                            >
                              <CardContent className="p-4">
                                <div className="flex items-center justify-between mb-2">
                                  <h4 className="font-medium">
                                    {table.title || `Table on Page ${table.page}`}
                                  </h4>
                                  <Badge variant="secondary">Page {table.page}</Badge>
                                </div>
                                <p className="text-sm text-zinc-500">
                                  {table.headers.length} columns, {table.rows.length} rows
                                </p>
                                <div className="flex gap-2 mt-3">
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleExportTable(table, 'csv');
                                    }}
                                  >
                                    CSV
                                  </Button>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleExportTable(table, 'excel');
                                    }}
                                  >
                                    Excel
                                  </Button>
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      </ScrollArea>

                      {/* Table Preview */}
                      <Card className="bg-zinc-50 dark:bg-zinc-900">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-base flex items-center gap-2">
                            <HiOutlineEye className="h-4 w-4" />
                            Table Preview
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          {selectedTable ? (
                            <ScrollArea className="h-[400px]">
                              <div className="overflow-x-auto">
                                <table className="w-full text-sm">
                                  <thead>
                                    <tr className="border-b dark:border-zinc-700">
                                      {selectedTable.headers.map((header, idx) => (
                                        <th
                                          key={idx}
                                          className="text-left p-2 font-medium bg-zinc-100 dark:bg-zinc-800"
                                        >
                                          {header}
                                        </th>
                                      ))}
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {selectedTable.rows.map((row, rowIdx) => (
                                      <tr
                                        key={rowIdx}
                                        className="border-b dark:border-zinc-700"
                                      >
                                        {row.map((cell, cellIdx) => (
                                          <td key={cellIdx} className="p-2">
                                            {cell}
                                          </td>
                                        ))}
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </ScrollArea>
                          ) : (
                            <div className="h-[400px] flex items-center justify-center text-zinc-500">
                              <p>Select a table to preview</p>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="figures" className="mt-4">
                  {figures.length === 0 ? (
                    <div className="text-center py-12 text-zinc-500">
                      <HiOutlinePhoto className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>No figures found in this document</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      {/* Figure Grid */}
                      <ScrollArea className="h-[500px]">
                        <div className="grid grid-cols-2 gap-4 pr-4">
                          {figures.map((figure) => (
                            <Card
                              key={figure.id}
                              className={`cursor-pointer transition-colors overflow-hidden ${
                                selectedFigure?.id === figure.id
                                  ? 'border-zinc-900 dark:border-zinc-50'
                                  : 'hover:border-zinc-300 dark:hover:border-zinc-700'
                              }`}
                              onClick={() => setSelectedFigure(figure)}
                            >
                              <div className="aspect-square bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center">
                                <img
                                  src={figure.image_url}
                                  alt={figure.caption || `Figure from page ${figure.page}`}
                                  className="max-w-full max-h-full object-contain"
                                  onError={(e) => {
                                    (e.target as HTMLImageElement).src =
                                      'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="50" x="50" text-anchor="middle" fill="%23999">No Preview</text></svg>';
                                  }}
                                />
                              </div>
                              <CardContent className="p-3">
                                <div className="flex items-center justify-between">
                                  <Badge variant="secondary" className="text-xs">
                                    Page {figure.page}
                                  </Badge>
                                  <Badge variant="outline" className="text-xs">
                                    {figure.type}
                                  </Badge>
                                </div>
                                {figure.caption && (
                                  <p className="text-xs text-zinc-500 mt-2 line-clamp-2">
                                    {figure.caption}
                                  </p>
                                )}
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      </ScrollArea>

                      {/* Figure Preview */}
                      <Card className="bg-zinc-50 dark:bg-zinc-900">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-base flex items-center justify-between">
                            <span className="flex items-center gap-2">
                              <HiOutlineEye className="h-4 w-4" />
                              Figure Preview
                            </span>
                            {selectedFigure && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDownloadFigure(selectedFigure)}
                              >
                                <HiOutlineArrowDownTray className="mr-2 h-4 w-4" />
                                Download
                              </Button>
                            )}
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          {selectedFigure ? (
                            <div className="space-y-4">
                              <div className="bg-white dark:bg-zinc-800 rounded-lg p-4 flex items-center justify-center min-h-[300px]">
                                <img
                                  src={selectedFigure.image_url}
                                  alt={selectedFigure.caption || 'Figure preview'}
                                  className="max-w-full max-h-[300px] object-contain"
                                />
                              </div>
                              {selectedFigure.caption && (
                                <div className="p-3 bg-zinc-100 dark:bg-zinc-800 rounded-lg">
                                  <p className="text-sm font-medium mb-1">Caption</p>
                                  <p className="text-sm text-zinc-600 dark:text-zinc-400">
                                    {selectedFigure.caption}
                                  </p>
                                </div>
                              )}
                              <div className="flex gap-4 text-sm text-zinc-500">
                                <span>Page: {selectedFigure.page}</span>
                                <span>Type: {selectedFigure.type}</span>
                                <span>
                                  Confidence: {Math.round(selectedFigure.confidence * 100)}%
                                </span>
                              </div>
                            </div>
                          ) : (
                            <div className="h-[400px] flex items-center justify-center text-zinc-500">
                              <p>Select a figure to preview</p>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        )}

        {/* Loading State */}
        {isExtracting && (
          <Card>
            <CardContent className="py-12">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-zinc-100 dark:bg-zinc-800 mb-4">
                  <div className="w-8 h-8 border-2 border-zinc-900 dark:border-zinc-50 border-t-transparent rounded-full animate-spin" />
                </div>
                <h3 className="text-lg font-medium mb-2">Extracting Data</h3>
                <p className="text-sm text-zinc-500 mb-4">
                  Analyzing document and extracting tables and figures...
                </p>
                <div className="max-w-xs mx-auto">
                  <div className="w-full h-2 bg-zinc-200 dark:bg-zinc-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-zinc-900 dark:bg-zinc-50 transition-all duration-300"
                      style={{ width: `${extractionProgress}%` }}
                    />
                  </div>
                  <p className="text-sm text-zinc-500 mt-2">{extractionProgress}% complete</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
