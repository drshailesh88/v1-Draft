import { TestUtils, loginAsDrChen, navigateToFeature, testData, TestAssertions, createTestReport, runTestWithTimeout, TestResult } from './utils';

async function testCreateWritingProject() {
  console.log('\n📝 Testing Writing Project Creation...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  const startTime = Date.now();
  
  try {
    await loginAsDrChen(utils);
    await navigateToFeature(utils, 'ai-writer');
    results.push({ passed: true, duration: Date.now() - startTime });
    
    await utils.clickElement('@create-project');
    await utils.waitForElement('@project-form', 5000);
    results.push({ passed: true, duration: Date.now() - startTime });
    
    await utils.fillInput('@project-title', 'AI-Powered Drug Discovery: A Systematic Review');
    await utils.fillInput('@project-type', 'Review Article');
    await utils.fillInput('@target-journal', 'Nature');
    await utils.clickElement('@create');
    await utils.waitForElement('@project-dashboard', 5000);
    results.push({ passed: true, duration: Date.now() - startTime });
    
    return true;
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: Date.now() - startTime });
    await utils.takeScreenshot('create-project-failure.png');
    return false;
  }
}

async function testGenerateAbstract() {
  console.log('\n📄 Testing Abstract Generation...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  const startTime = Date.now();
  
  try {
    await utils.clickElement('@section-abstract');
    await utils.waitForElement('@abstract-editor', 5000);
    results.push({ passed: true, duration: Date.now() - startTime });
    
    await utils.fillInput('@prompt-abstract', 'Generate an abstract for a systematic review on AI in drug discovery focusing on machine learning applications');
    await utils.clickElement('@generate-abstract');
    await utils.waitForElement('@generating', 3000);
    await utils.waitForElement('@abstract-content', 60000);
    results.push({ passed: true, duration: Date.now() - startTime });
    
    const content = await utils.getTextContent('@abstract-content');
    TestAssertions.assertGreaterThan(content.length, 200, 'Abstract should be substantial');
    results.push({ passed: true, duration: Date.now() - startTime });
    
    return true;
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: Date.now() - startTime });
    await utils.takeScreenshot('abstract-failure.png');
    return false;
  }
}

async function testGenerateIntroduction() {
  console.log('\n📚 Testing Introduction Generation...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  
  try {
    await utils.clickElement('@section-introduction');
    await utils.waitForElement('@introduction-editor', 5000);
    results.push({ passed: true, duration: 0 });
    
    await utils.fillInput('@prompt-intro', 'Write an introduction covering: drug discovery challenges, AI applications, research gap, and objectives');
    await utils.clickElement('@generate-intro');
    await utils.waitForElement('@intro-content', 90000);
    results.push({ passed: true, duration: 0 });
    
    return true;
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: 0 });
    await utils.takeScreenshot('introduction-failure.png');
    return false;
  }
}

async function testGenerateMethods() {
  console.log('\n🔬 Testing Methods Generation...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  
  try {
    await utils.clickElement('@section-methods');
    await utils.waitForElement('@methods-editor', 5000);
    results.push({ passed: true, duration: 0 });
    
    await utils.fillInput('@prompt-methods', 'Describe PRISMA methodology, search strategy, inclusion/exclusion criteria, and data extraction');
    await utils.clickElement('@generate-methods');
    await utils.waitForElement('@methods-content', 90000);
    results.push({ passed: true, duration: 0 });
    
    return true;
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: 0 });
    await utils.takeScreenshot('methods-failure.png');
    return false;
  }
}

async function testCitationInsertion() {
  console.log('\n📖 Testing Citation Insertion...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  
  try {
    await utils.clickElement('@insert-citations');
    await utils.waitForElement('@citation-search', 5000);
    results.push({ passed: true, duration: 0 });
    
    await utils.fillInput('@citation-query', 'machine learning drug discovery');
    await utils.clickElement('@search-citations');
    await utils.waitForElement('@citation-results', 10000);
    results.push({ passed: true, duration: 0 });
    
    await utils.clickElement('@citation-1-select');
    await utils.clickElement('@citation-2-select');
    await utils.clickElement('@insert-selected-citations');
    await utils.waitForElement('@citations-inserted', 5000);
    results.push({ passed: true, duration: 0 });
    
    return true;
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: 0 });
    await utils.takeScreenshot('citation-failure.png');
    return false;
  }
}

async function testExportToLaTeX() {
  console.log('\n📤 Testing LaTeX Export...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  
  try {
    await utils.clickElement('@export-button');
    await utils.clickElement('@export-latex');
    await utils.waitForElement('@export-complete', 15000);
    results.push({ passed: true, duration: 0 });
    
    await utils.takeScreenshot('latex-export.png');
    return true;
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: 0 });
    await utils.takeScreenshot('latex-failure.png');
    return false;
  }
}

async function testExportToWord() {
  console.log('\n📝 Testing Word Export...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  
  try {
    await utils.clickElement('@export-button');
    await utils.clickElement('@export-word');
    await utils.waitForElement('@export-complete', 15000);
    results.push({ passed: true, duration: 0 });
    
    await utils.takeScreenshot('word-export.png');
    return true;
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: 0 });
    await utils.takeScreenshot('word-failure.png');
    return false;
  }
}

export async function runAIWriterTests() {
  console.log('🚀 Starting AI Writer Workflow Tests');
  console.log('=' .repeat(50));
  
  const allPassed = await runTestWithTimeout(async () => {
    const projectPassed = await testCreateWritingProject();
    if (!projectPassed) {
      console.log('\n❌ Project creation failed - applying fix...');
      return false;
    }
    
    const abstractPassed = await testGenerateAbstract();
    if (!abstractPassed) {
      console.log('\n❌ Abstract generation failed - applying fix...');
      return false;
    }
    
    const introPassed = await testGenerateIntroduction();
    if (!introPassed) {
      console.log('\n❌ Introduction generation failed - applying fix...');
      return false;
    }
    
    const methodsPassed = await testGenerateMethods();
    if (!methodsPassed) {
      console.log('\n❌ Methods generation failed - applying fix...');
      return false;
    }
    
    const citationPassed = await testCitationInsertion();
    if (!citationPassed) {
      console.log('\n❌ Citation insertion failed - applying fix...');
      return false;
    }
    
    const latexPassed = await testExportToLaTeX();
    if (!latexPassed) {
      console.log('\n❌ LaTeX export failed - applying fix...');
      return false;
    }
    
    const wordPassed = await testExportToWord();
    if (!wordPassed) {
      console.log('\n❌ Word export failed - applying fix...');
      return false;
    }
    
    return true;
  }, 600000);
  
  if (allPassed) {
    console.log('\n✅ All AI Writer tests passed!');
    process.exit(0);
  } else {
    console.log('\n❌ Some tests failed. Check logs above.');
    process.exit(1);
  }
}

if (require.main === module) {
  runAIWriterTests().catch(console.error);
}
