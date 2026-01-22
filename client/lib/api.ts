// V1Draft API Configuration
// This connects the frontend to the FastAPI backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  baseUrl: API_BASE_URL,

  // Chat with PDF
  chat: {
    upload: `${API_BASE_URL}/api/chat/upload`,
    chat: `${API_BASE_URL}/api/chat/chat`,
    documents: `${API_BASE_URL}/api/chat/documents`,
    document: (id: string) => `${API_BASE_URL}/api/chat/documents/${id}`,
  },

  // Literature Search
  literature: {
    search: `${API_BASE_URL}/api/literature/search`,
    savePaper: `${API_BASE_URL}/api/literature/save-paper`,
    savedPapers: `${API_BASE_URL}/api/literature/saved-papers`,
    export: `${API_BASE_URL}/api/literature/export`,
    searchHistory: `${API_BASE_URL}/api/literature/search-history`,
  },

  // Citation Generator
  citations: {
    generate: `${API_BASE_URL}/api/citations/generate`,
    batchGenerate: `${API_BASE_URL}/api/citations/batch-generate`,
    doiLookup: `${API_BASE_URL}/api/citations/doi/lookup`,
    styles: `${API_BASE_URL}/api/citations/styles`,
    export: `${API_BASE_URL}/api/citations/export`,
    saved: `${API_BASE_URL}/api/citations/saved`,
  },

  // Data Extraction
  dataExtraction: {
    extractTables: `${API_BASE_URL}/api/data-extraction/extract-tables`,
    extractFigures: `${API_BASE_URL}/api/data-extraction/extract-figures`,
    exportCsv: `${API_BASE_URL}/api/data-extraction/export-csv`,
    exportExcel: `${API_BASE_URL}/api/data-extraction/export-excel`,
  },

  // AI Detector
  aiDetector: {
    detectText: `${API_BASE_URL}/api/ai-detector/detect-text`,
    detectFile: `${API_BASE_URL}/api/ai-detector/detect-file`,
    history: `${API_BASE_URL}/api/ai-detector/history`,
  },

  // AI Writer
  aiWriter: {
    projects: `${API_BASE_URL}/api/ai-writer/projects`,
    project: (id: string) => `${API_BASE_URL}/api/ai-writer/projects/${id}`,
    generateSection: (id: string) => `${API_BASE_URL}/api/ai-writer/projects/${id}/generate-section`,
    export: (id: string) => `${API_BASE_URL}/api/ai-writer/projects/${id}/export`,
  },

  // Systematic Review
  systematicReview: {
    reviews: `${API_BASE_URL}/api/systematic-review/reviews`,
    review: (id: string) => `${API_BASE_URL}/api/systematic-review/reviews/${id}`,
    search: (id: string) => `${API_BASE_URL}/api/systematic-review/reviews/${id}/search`,
    studies: (id: string) => `${API_BASE_URL}/api/systematic-review/reviews/${id}/studies`,
    prismaFlow: (id: string) => `${API_BASE_URL}/api/systematic-review/reviews/${id}/prisma-flow`,
  },

  // Citation Booster
  citationBooster: {
    analyze: `${API_BASE_URL}/api/citation-booster/analyze`,
    suggest: `${API_BASE_URL}/api/citation-booster/suggest`,
    gaps: `${API_BASE_URL}/api/citation-booster/gaps`,
  },

  // Paraphraser
  paraphraser: {
    paraphrase: `${API_BASE_URL}/api/paraphraser/paraphrase`,
    batch: `${API_BASE_URL}/api/paraphraser/batch`,
    modes: `${API_BASE_URL}/api/paraphraser/modes`,
    history: `${API_BASE_URL}/api/paraphraser/history`,
  },

  // Deep Review
  deepReview: {
    analyze: `${API_BASE_URL}/api/deep-review/analyze`,
    analyzeFile: `${API_BASE_URL}/api/deep-review/analyze-file`,
    review: (id: string) => `${API_BASE_URL}/api/deep-review/review/${id}`,
    export: `${API_BASE_URL}/api/deep-review/export`,
    history: `${API_BASE_URL}/api/deep-review/history`,
  },

  // Find Topics
  findTopics: {
    discover: `${API_BASE_URL}/api/find-topics/discover`,
    trending: `${API_BASE_URL}/api/find-topics/trending`,
    gaps: `${API_BASE_URL}/api/find-topics/gaps`,
    validate: `${API_BASE_URL}/api/find-topics/validate`,
    saved: `${API_BASE_URL}/api/find-topics/saved`,
  },
};

// Helper function for API calls
export async function apiCall<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

// Helper for file uploads
export async function uploadFile(
  url: string,
  file: File,
  additionalData?: Record<string, string>
): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);

  if (additionalData) {
    Object.entries(additionalData).forEach(([key, value]) => {
      formData.append(key, value);
    });
  }

  const response = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || `Upload error: ${response.status}`);
  }

  return response.json();
}

export default api;
