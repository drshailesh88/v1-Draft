'use client';

import { useState, useRef, useEffect } from 'react';
import DashboardLayout from '@/components/layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { api, uploadFile, apiCall } from '@/lib/api';
import { User } from '@supabase/supabase-js';
import { useToast } from '@/hooks/use-toast';
import {
  HiOutlineDocumentText,
  HiOutlinePaperAirplane,
  HiOutlineCloudArrowUp,
  HiOutlineTrash,
  HiOutlineUser,
  HiOutlineSparkles,
  HiOutlineDocumentMagnifyingGlass,
} from 'react-icons/hi2';

interface Props {
  user: User | null | undefined;
  userDetails: { [x: string]: any } | null;
}

interface Document {
  id: string;
  filename: string;
  upload_date: string;
  page_count: number;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

interface Source {
  page: number;
  text: string;
  relevance: number;
}

export default function ChatPDF({ user, userDetails }: Props) {
  const { toast } = useToast();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingDocs, setIsLoadingDocs] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setIsLoadingDocs(true);
      const data = await apiCall<Document[]>(api.chat.documents);
      setDocuments(data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    } finally {
      setIsLoadingDocs(false);
    }
  };

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
      const result = await uploadFile(api.chat.upload, file);
      toast({
        title: 'Upload successful',
        description: `${file.name} has been uploaded.`,
      });
      await fetchDocuments();
      if (result.document_id) {
        const newDoc = documents.find(d => d.id === result.document_id);
        if (newDoc) {
          setSelectedDocument(newDoc);
        }
      }
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

  const handleDeleteDocument = async (docId: string) => {
    try {
      await apiCall(api.chat.document(docId), { method: 'DELETE' });
      toast({
        title: 'Document deleted',
        description: 'The document has been removed.',
      });
      if (selectedDocument?.id === docId) {
        setSelectedDocument(null);
        setMessages([]);
      }
      await fetchDocuments();
    } catch (error: any) {
      toast({
        title: 'Delete failed',
        description: error.message || 'Failed to delete document.',
        variant: 'destructive',
      });
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedDocument) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await apiCall<{
        response: string;
        sources: Source[];
      }>(api.chat.chat, {
        method: 'POST',
        body: JSON.stringify({
          document_id: selectedDocument.id,
          message: inputMessage,
        }),
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        sources: response.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to get response.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <DashboardLayout
      user={user}
      userDetails={userDetails}
      title="Chat with PDF"
      description="Chat with your PDF documents"
    >
      <div className="flex h-[calc(100vh-200px)] gap-4">
        {/* Document Sidebar */}
        <Card className="w-80 flex-shrink-0">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <HiOutlineDocumentText className="h-5 w-5" />
              Documents
            </CardTitle>
            <CardDescription>Upload and select PDFs to chat with</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                className="hidden"
              />
              <Button
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                className="w-full"
              >
                <HiOutlineCloudArrowUp className="mr-2 h-4 w-4" />
                {isUploading ? 'Uploading...' : 'Upload PDF'}
              </Button>
            </div>

            <ScrollArea className="h-[calc(100vh-400px)]">
              <div className="space-y-2">
                {isLoadingDocs ? (
                  <>
                    <Skeleton className="h-16 w-full" />
                    <Skeleton className="h-16 w-full" />
                    <Skeleton className="h-16 w-full" />
                  </>
                ) : documents.length === 0 ? (
                  <p className="text-center text-sm text-zinc-500 py-4">
                    No documents uploaded yet.
                  </p>
                ) : (
                  documents.map((doc) => (
                    <div
                      key={doc.id}
                      className={`group flex items-center justify-between rounded-lg border p-3 cursor-pointer transition-colors ${
                        selectedDocument?.id === doc.id
                          ? 'border-zinc-900 bg-zinc-100 dark:border-zinc-50 dark:bg-zinc-800'
                          : 'border-zinc-200 hover:border-zinc-300 dark:border-zinc-700 dark:hover:border-zinc-600'
                      }`}
                      onClick={() => {
                        setSelectedDocument(doc);
                        setMessages([]);
                      }}
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{doc.filename}</p>
                        <p className="text-xs text-zinc-500">
                          {doc.page_count} pages
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="opacity-0 group-hover:opacity-100 h-8 w-8"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteDocument(doc.id);
                        }}
                      >
                        <HiOutlineTrash className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Chat Area */}
        <Card className="flex-1 flex flex-col">
          <CardHeader className="pb-3 border-b">
            <CardTitle className="flex items-center gap-2 text-lg">
              <HiOutlineDocumentMagnifyingGlass className="h-5 w-5" />
              {selectedDocument ? selectedDocument.filename : 'Select a Document'}
            </CardTitle>
            {selectedDocument && (
              <CardDescription>
                Ask questions about this document
              </CardDescription>
            )}
          </CardHeader>

          <CardContent className="flex-1 flex flex-col p-0">
            {!selectedDocument ? (
              <div className="flex-1 flex items-center justify-center text-zinc-500">
                <div className="text-center">
                  <HiOutlineDocumentText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Select a document from the sidebar to start chatting</p>
                </div>
              </div>
            ) : (
              <>
                {/* Messages */}
                <ScrollArea className="flex-1 p-4">
                  <div className="space-y-4">
                    {messages.length === 0 && (
                      <div className="text-center text-zinc-500 py-8">
                        <HiOutlineSparkles className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p>Start by asking a question about the document</p>
                      </div>
                    )}
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex gap-3 ${
                          message.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        {message.role === 'assistant' && (
                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-900 dark:bg-zinc-50">
                            <HiOutlineSparkles className="h-4 w-4 text-white dark:text-zinc-900" />
                          </div>
                        )}
                        <div
                          className={`max-w-[80%] rounded-lg p-4 ${
                            message.role === 'user'
                              ? 'bg-zinc-900 text-white dark:bg-zinc-50 dark:text-zinc-900'
                              : 'bg-zinc-100 dark:bg-zinc-800'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                          {message.sources && message.sources.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-zinc-200 dark:border-zinc-700">
                              <p className="text-xs font-medium mb-2">Sources:</p>
                              <div className="space-y-2">
                                {message.sources.map((source, idx) => (
                                  <div
                                    key={idx}
                                    className="text-xs bg-white dark:bg-zinc-900 rounded p-2"
                                  >
                                    <Badge variant="secondary" className="mb-1">
                                      Page {source.page}
                                    </Badge>
                                    <p className="text-zinc-600 dark:text-zinc-400 line-clamp-2">
                                      {source.text}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                        {message.role === 'user' && (
                          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-zinc-200 dark:border-zinc-700">
                            <HiOutlineUser className="h-4 w-4" />
                          </div>
                        )}
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex gap-3">
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-900 dark:bg-zinc-50">
                          <HiOutlineSparkles className="h-4 w-4 text-white dark:text-zinc-900" />
                        </div>
                        <div className="bg-zinc-100 dark:bg-zinc-800 rounded-lg p-4">
                          <div className="flex space-x-2">
                            <div className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce" />
                            <div className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce delay-100" />
                            <div className="w-2 h-2 bg-zinc-400 rounded-full animate-bounce delay-200" />
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                </ScrollArea>

                {/* Input */}
                <div className="p-4 border-t">
                  <div className="flex gap-2">
                    <Input
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask a question about the document..."
                      disabled={isLoading}
                      className="flex-1"
                    />
                    <Button
                      onClick={handleSendMessage}
                      disabled={!inputMessage.trim() || isLoading}
                    >
                      <HiOutlinePaperAirplane className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
