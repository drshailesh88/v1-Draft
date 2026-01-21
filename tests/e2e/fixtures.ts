# Test fixtures and test data

import { testData } from './utils';

export const literatureReviewFixtures = {
  sampleQuery: testData.queries.literature,
  expectedResults: [
    {
      title: 'AI in Drug Discovery: A Review',
      source: 'PubMed',
      year: 2023,
      citations: 45
    },
    {
      title: 'Machine Learning for Drug Development',
      source: 'arXiv',
      year: 2022,
      citations: 32
    }
  ]
};

export const systematicReviewFixtures = {
  researchQuestion: 'What is the impact of AI on drug discovery processes?',
  inclusionCriteria: [
    'Published in English',
    'Peer-reviewed articles',
    'AI applications in drug discovery',
    'Published between 2018-2024'
  ],
  exclusionCriteria: [
    'Non-peer-reviewed articles',
    'Non-English publications',
    'Review articles without data',
    'Articles before 2018'
  ],
  expectedPapers: 500
};

export const aiWriterFixtures = {
  project: {
    title: 'AI-Powered Drug Discovery: A Systematic Review',
    type: 'Review Article',
    targetJournal: 'Nature',
    sections: [
      'Abstract',
      'Introduction',
      'Methods',
      'Results',
      'Discussion',
      'Conclusion'
    ]
  },
  sections: {
    abstract: {
      prompt: 'Generate an abstract for a systematic review on AI in drug discovery',
      minWords: 200,
      maxWords: 300
    },
    introduction: {
      prompt: 'Write an introduction covering drug discovery challenges, AI applications, research gap, and objectives',
      minWords: 500,
      maxWords: 800
    },
    methods: {
      prompt: 'Describe PRISMA methodology, search strategy, inclusion/exclusion criteria, and data extraction',
      minWords: 400,
      maxWords: 600
    }
  }
};

export const natureReviewFixtures = {
  totalPapers: 500,
  papersToExtract: 200,
  searchTerms: [
    'AI drug discovery',
    'machine learning drug development',
    'deep learning pharma',
    'artificial intelligence pharmaceutical',
    'neural networks drug screening'
  ],
  exportFormats: ['LaTeX', 'Word', 'PDF'],
  submissionRequirements: {
    wordCount: { min: 5000, max: 8000 },
    citations: { min: 100 },
    figures: { min: 5, max: 10 },
    tables: { min: 3, max: 6 }
  }
};
