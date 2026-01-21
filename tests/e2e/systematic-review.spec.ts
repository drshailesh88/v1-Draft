import { TestUtils, loginAsDrChen, navigateToFeature, testData, TestAssertions, createTestReport, runTestWithTimeout, TestResult } from './utils';

async function testCreateReview() {
  console.log('\n📋 Testing PRISMA Review Creation...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  const startTime = Date.now();
  
  try {
    await loginAsDrChen(utils);
    await navigateToFeature(utils, 'systematic-review');
    results.push({ passed: true, duration: Date.now() - startTime });
    
    await utils.clickElement('@create-new-review');
    await utils.waitForElement('@review-form', 5000);
    results.push({ passed: true, duration: Date.now() - startTime });
    
    await utils.fillInput('@review-title', 'AI in Drug Discovery - Systematic Review');
    await utils.fillInput('@research-question', 'What is the impact of AI on drug discovery processes?');
    await utils.clickElement('@next-step');
    await utils.waitForElement('@criteria-section', 5000);
    results.push({ passed: true, duration: Date.now() - startTime });
    
    return true;
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: Date.now() - startTime });
    await utils.takeScreenshot('create-review-failure.png');
    return false;
  }
}

async function testInclusionCriteria() {
  console.log('\n✅ Testing Inclusion/Exclusion Criteria...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  
  try {
    await utils.fillInput('@inclusion-criteria', 'Published in English, peer-reviewed, AI in drug discovery');
    await utils.fillInput('@exclusion-criteria', 'Non-peer-reviewed articles, non-English publications');
    await utils.clickElement('@save-criteria');
    await utils.waitForElement('@criteria-saved', 5000);
    results.push({ passed: true, duration: 0 });
    
    return true;
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: 0 });
    await utils.takeScreenshot('criteria-failure.png');
    return false;
  }
}

async function testLiteratureSearchForReview() {
  console.log('\n🔍 Testing Literature Search for Review...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  const startTime = Date.now();
  
  try {
    await utils.clickElement('@run-search');
    await utils.waitForElement('@search-progress', 5000);
    await utils.waitForElement('@search-complete', 60000);
    results.push({ passed: true, duration: Date.now() - startTime });
    
    const snapshot = await utils.getSnapshot();
    const resultCount = snapshot.elements.find((e: any) => e.ref === '@result-count');
    TestAssertions.assertGreaterThan(parseInt(resultCount?.text || '0'), 0, 'Should have search results');
    results.push({ passed: true, duration: Date.now() - startTime });
    
    return true;
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: Date.now() - startTime });
    await utils.takeScreenshot('review-search-failure.png');
    return false;
  }
}

async function testPRISMAscreening() {
  console.log('\n🔎 Testing PRISMA Screening...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  
  try {
    await utils.clickElement('@start-screening');
    await utils.waitForElement('@screening-interface', 5000);
    results.push({ passed: true, duration: 0 });
    
    await utils.clickElement('@screen-title-1-include');
    await utils.clickElement('@screen-title-2-exclude');
    await utils.clickElement('@screen-title-3-include');
    await utils.clickElement('@screen-title-4-include');
    await utils.clickElement('@next-papers');
    results.push({ passed: true, duration: 0 });
    
    await utils.waitForElement('@screening-complete', 30000);
    results.push({ passed: true, duration: 0 });
    
    return true;
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: 0 });
    await utils.takeScreenshot('screening-failure.png');
    return false;
  }
}

async function testPRISMAdiagramGeneration() {
  console.log('\n📊 Testing PRISMA Diagram Generation...');
  
  const utils = new TestUtils();
  const results: TestResult[] = [];
  const startTime = Date.now();
  
  try {
    await utils.clickElement('@generate-prisma-diagram');
    await utils.waitForElement('@diagram-generating', 5000);
    await utils.waitForElement('@prisma-diagram', 15000);
    results.push({ passed: true, duration: Date.now() - startTime });
    
    const snapshot = await utils.getSnapshot();
    const hasDiagram = snapshot.elements.some((e: any) => e.ref === '@prisma-diagram');
    TestAssertions.assert(hasDiagram, 'PRISMA diagram should be visible');
    results.push({ passed: true, duration: Date.now() - startTime });
    
    await utils.clickElement('@download-diagram');
    await utils.waitForElement('@download-complete', 10000);
    results.push({ passed: true, duration: Date.now() - startTime });
    
    return true;
  } catch (error) {
    results.push({ passed: false, error: (error as Error).message, duration: Date.now() - startTime });
    await utils.takeScreenshot('diagram-failure.png');
    return false;
  }
}

export async function runSystematicReviewTests() {
  console.log('🚀 Starting Systematic Review Workflow Tests');
  console.log('=' .repeat(50));
  
  const allPassed = await runTestWithTimeout(async () => {
    const createPassed = await testCreateReview();
    if (!createPassed) {
      console.log('\n❌ Review creation failed - applying fix...');
      return false;
    }
    
    const criteriaPassed = await testInclusionCriteria();
    if (!criteriaPassed) {
      console.log('\n❌ Criteria setting failed - applying fix...');
      return false;
    }
    
    const searchPassed = await testLiteratureSearchForReview();
    if (!searchPassed) {
      console.log('\n❌ Literature search failed - applying fix...');
      return false;
    }
    
    const screeningPassed = await testPRISMAscreening();
    if (!screeningPassed) {
      console.log('\n❌ Screening failed - applying fix...');
      return false;
    }
    
    const diagramPassed = await testPRISMAdiagramGeneration();
    if (!diagramPassed) {
      console.log('\n❌ Diagram generation failed - applying fix...');
      return false;
    }
    
    return true;
  }, 300000);
  
  if (allPassed) {
    console.log('\n✅ All Systematic Review tests passed!');
    process.exit(0);
  } else {
    console.log('\n❌ Some tests failed. Check logs above.');
    process.exit(1);
  }
}

if (require.main === module) {
  runSystematicReviewTests().catch(console.error);
}
