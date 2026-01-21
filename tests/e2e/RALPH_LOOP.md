# Ralph Loop Testing Framework

This directory contains the Ralph Loop testing framework for iterative feature testing.

## Overview

The Ralph Loop methodology follows this pattern for each feature:
```
Test → Find Problem → Fix → Test Again → Exit When Complete
```

## Implementation

Each test spec file follows the Ralph Loop pattern:

1. **Test**: Execute test steps
2. **Find Problem**: Capture errors and take screenshots
3. **Fix**: (Manual) Apply fixes based on test results
4. **Test Again**: Re-run the test
5. **Exit**: When all tests pass

## Ralph Loop Example

```typescript
async function testFeature() {
  const utils = new TestUtils();
  const results: TestResult[] = [];
  
  try {
    // 1. Test: Execute feature
    await utils.openUrl('/feature');
    await utils.clickElement('@action-button');
    await utils.waitForElement('@success', 5000);
    
    // 2. Validate: Check expected outcome
    const snapshot = await utils.getSnapshot();
    TestAssertions.assert(
      snapshot.elements.some(e => e.ref === '@success'),
      'Success element should be visible'
    );
    
    results.push({ passed: true, duration: Date.now() - startTime });
    
  } catch (error) {
    // 3. Find Problem: Log error and capture evidence
    results.push({
      passed: false,
      error: (error as Error).message,
      duration: Date.now() - startTime
    });
    
    // 4. Evidence: Take screenshot
    await utils.takeScreenshot('feature-failure.png');
    
    // 5. Report: Generate detailed report
    createTestReport('Feature Test', results);
    
    return false; // Signal fix needed
  }
}
```

## Running Ralph Loop Tests

```bash
# Run specific test with Ralph Loop
npm run test:literature

# Test fails → Fix → Run again
npm run test:literature

# Continue until all tests pass
```

## Exit Criteria

Each test suite has specific exit criteria defined in ULTIMATE_BUILD_DIRECTIVE.md:

- **Literature Review**: Search works, papers save, export succeeds
- **Systematic Review**: PRISMA flow complete, diagram generates
- **AI Writer**: All sections generate, exports work
- **Nature Review**: Complete workflow passes end-to-end

## Best Practices

1. **Test before fix**: Always run test first to see failure
2. **Minimal fixes**: Fix only what's broken
3. **Immediate re-test**: Test again after each fix
4. **Document learnings**: Note what was fixed and why
5. **Screenshot on failure**: Always capture visual evidence
6. **Timebox fixes**: If fix takes too long, escalate or refactor

## Test Status Tracking

Track test runs in a simple log:

```
2026-01-21 14:30 - Literature Review: FAILED (Element not found)
2026-01-21 14:45 - Literature Review: PASSED ✓
```

## Fix Examples

### Example 1: Element Not Found

**Test**: `@search-button`
**Error**: Element not found
**Fix**: Check if button has correct ID or add data-testid
**Re-test**: ✅ Pass

### Example 2: Timeout

**Test**: Wait for search results (10s timeout)
**Error**: Timeout exceeded
**Fix**: Increase timeout or optimize search query
**Re-test**: ✅ Pass

### Example 3: Assertion Failed

**Test**: Verify export complete
**Error**: Expected "complete", got "downloading"
**Fix**: Wait for final state before asserting
**Re-test**: ✅ Pass
