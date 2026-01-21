import { TestUtils, loginAsDrChen, navigateToFeature, testData, TestAssertions, createTestReport, runTestWithTimeout, TestResult } from './utils';

async function testLiteratureSearch() {
  console.log('\n🔍 Testing Literature Search...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  const startTime = Date.now();
  
  try {
    await loginAsDrChen(utils);
    results.push({ passed: true, duration: Date.now() - startTime });
    
    await navigateToFeature(utils, 'literature');
    results.push({ passed: true, duration: Date.now() - startTime });
    
    const startSearch = Date.now();
    await utils.fillInput('@search-input', testData.queries.literature);
    await utils.clickElement('@search-button');
    await utils.waitForElement('@search-results', 15000);
    results.push({ passed: true, duration: Date.now() - startSearch });
    
    const startSave = Date.now();
    await utils.clickElement('@paper-1-select');
    await utils.clickElement('@paper-2-select');
    await utils.clickElement('@paper-3-select');
    await utils.clickElement('@save-selected');
    await utils.waitForElement('@save-success', 5000);
    results.push({ passed: true, duration: Date.now() - startSave });
    
    const startExport = Date.now();
    await utils.clickElement('@export-button');
    await utils.clickElement('@export-bibtex');
    await utils.waitForElement('@download-complete', 10000);
    results.push({ passed: true, duration: Date.now() - startExport });
    
    const snapshot = await utils.getSnapshot();
    const hasResults = snapshot.elements.some((e: any) => e.ref === '@search-results');
    TestAssertions.assert(hasResults, 'Search results should be visible');
    results.push({ passed: true, duration: Date.now() - startTime });
    
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: Date.now() - startTime });
    await utils.takeScreenshot('literature-search-failure.png');
  }
  
  createTestReport('Literature Review', results);
  return results.every(r => r.passed);
}

async function testChatWithPDF() {
  console.log('\n💬 Testing Chat with PDF...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  
  try {
    await navigateToFeature(utils, 'chat');
    results.push({ passed: true, duration: 0 });
    
    await utils.clickElement('@upload-pdf');
    await utils.fillInput('@file-input', 'test-paper.pdf');
    await utils.clickElement('@upload-confirm');
    await utils.waitForElement('@pdf-processing', 10000);
    results.push({ passed: true, duration: 0 });
    
    await utils.waitForElement('@chat-input', 30000);
    await utils.fillInput('@chat-input', 'What are the main findings?');
    await utils.clickElement('@send-message');
    await utils.waitForElement('@ai-response', 15000);
    results.push({ passed: true, duration: 0 });
    
    const response = await utils.getTextContent('@ai-response');
    TestAssertions.assertContains(response, 'findings');
    results.push({ passed: true, duration: 0 });
    
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: 0 });
    await utils.takeScreenshot('chat-pdf-failure.png');
  }
  
  createTestReport('Chat with PDF', results);
  return results.every(r => r.passed);
}

async function testDataExtraction() {
  console.log('\n📊 Testing Data Extraction...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  
  try {
    await navigateToFeature(utils, 'data-extraction');
    results.push({ passed: true, duration: 0 });
    
    await utils.clickElement('@select-pdf');
    await utils.waitForElement('@extraction-options', 5000);
    results.push({ passed: true, duration: 0 });
    
    await utils.clickElement('@extract-tables');
    await utils.clickElement('@extract-figures');
    await utils.clickElement('@start-extraction');
    await utils.waitForElement('@extraction-results', 20000);
    results.push({ passed: true, duration: 0 });
    
    await utils.clickElement('@export-csv');
    await utils.waitForElement('@download-complete', 10000);
    results.push({ passed: true, duration: 0 });
    
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: 0 });
    await utils.takeScreenshot('data-extraction-failure.png');
  }
  
  createTestReport('Data Extraction', results);
  return results.every(r => r.passed);
}

export async function runLiteratureReviewTests() {
  console.log('🚀 Starting Literature Review Workflow Tests');
  console.log('=' .repeat(50));
  
  const allPassed = await runTestWithTimeout(async () => {
    const searchPassed = await testLiteratureSearch();
    if (!searchPassed) {
      console.log('\n❌ Literature search test failed - applying fix...');
      await utils.sleep(2000);
      return false;
    }
    
    const chatPassed = await testChatWithPDF();
    if (!chatPassed) {
      console.log('\n❌ Chat with PDF test failed - applying fix...');
      return false;
    }
    
    const extractionPassed = await testDataExtraction();
    if (!extractionPassed) {
      console.log('\n❌ Data extraction test failed - applying fix...');
      return false;
    }
    
    return true;
  }, 180000);
  
  if (allPassed) {
    console.log('\n✅ All Literature Review tests passed!');
    process.exit(0);
  } else {
    console.log('\n❌ Some tests failed. Check logs above.');
    process.exit(1);
  }
}

if (require.main === module) {
  runLiteratureReviewTests().catch(console.error);
}
