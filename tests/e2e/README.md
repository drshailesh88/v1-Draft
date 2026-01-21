# E2E Testing for Academic Research Platform

End-to-end testing infrastructure using **agent-browser** for validating the academic research platform features.

## 📋 Overview

This test suite validates all core features of the platform through comprehensive browser automation tests. The tests simulate real researcher workflows, particularly focusing on Dr. Chen's Nature review submission.

### Test Scenarios

1. **Literature Review Workflow** (`literature-review.spec.ts`)
   - Literature search across multiple databases
   - Paper selection and saving to library
   - Citation export (BibTeX, RIS, etc.)
   - Chat with PDF functionality
   - Data extraction from papers

2. **Systematic Review Workflow** (`systematic-review.spec.ts`)
   - PRISMA review creation
   - Inclusion/exclusion criteria setup
   - Title and abstract screening
   - PRISMA flow diagram generation
   - Study data management

3. **AI Writer Workflow** (`ai-writer.spec.ts`)
   - Writing project creation
   - Section-by-section generation (Abstract, Introduction, Methods, Results, Discussion, Conclusion)
   - Citation insertion and management
   - Export to LaTeX and Word formats

4. **Full Nature Review Workflow** (`nature-review.spec.ts`)
   - Complete end-to-end simulation
   - Literature search (500+ papers)
   - Systematic screening (PRISMA)
   - Data extraction (200 papers)
   - Full paper generation
   - Nature submission-ready export

## 🚀 Setup

### Prerequisites

- Node.js 18+ and npm
- agent-browser installed globally
- Test environment running (http://localhost:3000)

### Installation

```bash
# Navigate to tests directory
cd tests/e2e

# Install dependencies
npm install

# Install agent-browser (if not already installed)
npm install -g agent-browser
agent-browser install
```

## 🏃 Running Tests

### Run All Tests

```bash
npm run test:all
```

### Run Specific Test Scenarios

```bash
# Literature Review Workflow
npm run test:literature

# Systematic Review Workflow
npm run test:systematic

# AI Writer Workflow
npm run test:ai-writer

# Full Nature Review Workflow
npm run test:nature
```

### Run from Root Directory

```bash
cd ../..
npm run test:e2e
```

## 📊 Test Results

Each test scenario produces a detailed report showing:

- **Total tests run**
- **Passed vs Failed count**
- **Duration per test**
- **Error messages for failures**
- **Screenshots on failure**

### Sample Output

```
🔍 Testing Literature Search...
✅ Login successful
✅ Navigation to literature page
✅ Search completed (15 papers found)
✅ Papers saved to library
✅ BibTeX export successful

=== Literature Review Test Report ===
Total: 5
Passed: 5
Failed: 0
Duration: 15234ms
```

## 🧪 Test Architecture

### Utilities (`utils.ts`)

Core testing utilities providing:

- **TestUtils class**: Browser automation wrappers
  - `openUrl()` - Navigate to pages
  - `clickElement()` - Click elements by reference
  - `fillInput()` - Fill form fields
  - `waitForElement()` - Wait for elements to appear
  - `takeScreenshot()` - Capture screenshots on failure
  - `getSnapshot()` - Get page structure
  - `getTextContent()` - Extract text from elements

- **TestAssertions class**: Validation helpers
  - `assert()` - Basic assertion
  - `assertContains()` - String contains check
  - `assertGreaterThan()` - Numeric comparison
  - `assertEquals()` - Equality check

- **Test Data** (`testData`)
  - Dr. Chen's test credentials
  - Search queries and sample papers
  - Pre-configured test data

- **Helper Functions**
  - `loginAsDrChen()` - Automated login
  - `navigateToFeature()` - Feature navigation
  - `createTestReport()` - Report generation
  - `runTestWithTimeout()` - Timeout handling

### Ralph Loop Implementation

Each test scenario follows the Ralph Loop methodology:

```
Test → Find Problem → Fix → Test Again → Exit When Complete
```

#### Example: Literature Search Test

```typescript
try {
  // 1. Test: Search for papers
  await utils.fillInput('@search-input', testData.queries.literature);
  await utils.clickElement('@search-button');
  await utils.waitForElement('@search-results', 15000);
  
  // 2. Validate: Check results
  const snapshot = await utils.getSnapshot();
  const hasResults = snapshot.elements.some(e => e.ref === '@search-results');
  TestAssertions.assert(hasResults, 'Search results should be visible');
  
  results.push({ passed: true, duration: Date.now() - startTime });
  
} catch (error) {
  // 3. Find Problem: Capture error
  results.push({ 
    passed: false, 
    error: (error as Error).message, 
    duration: Date.now() - startTime 
  });
  
  // 4. Evidence: Take screenshot
  await utils.takeScreenshot('literature-search-failure.png');
  
  // 5. Report: Document failure
  createTestReport('Literature Review', results);
  
  return false; // Will trigger fix attempt
}
```

## 🎯 Expected Test Outcomes

### Literature Review Workflow

| Test | Expected Result | Duration |
|------|----------------|----------|
| Login | Success | < 10s |
| Literature Search | 10+ papers found | < 15s |
| Save Papers | 3 papers saved | < 5s |
| Export BibTeX | Download complete | < 10s |
| Chat with PDF | AI responds with citations | < 30s |
| Data Extraction | Tables extracted | < 20s |

### Systematic Review Workflow

| Test | Expected Result | Duration |
|------|----------------|----------|
| Create Review | Form opens | < 5s |
| Set Criteria | Criteria saved | < 5s |
| Literature Search | Results returned | < 60s |
| Title Screening | Batch screened | < 30s |
| PRISMA Diagram | Diagram generated | < 15s |
| Export Diagram | Download complete | < 10s |

### AI Writer Workflow

| Test | Expected Result | Duration |
|------|----------------|----------|
| Create Project | Dashboard opens | < 10s |
| Generate Abstract | 200+ words | < 60s |
| Generate Introduction | 500+ words | < 90s |
| Generate Methods | 400+ words | < 90s |
| Insert Citations | Citations added | < 15s |
| Export LaTeX | File downloaded | < 15s |
| Export Word | File downloaded | < 15s |

### Full Nature Review Workflow

| Test | Expected Result | Duration |
|------|----------------|----------|
| Literature Search | 500+ papers | < 5min |
| Systematic Screening | PRISMA complete | < 5min |
| Data Extraction | 200 papers analyzed | < 5min |
| AI Writing | All sections generated | < 10min |
| Citation Management | Validated & formatted | < 1min |
| Export Package | Nature-ready | < 30s |

**Total Duration**: ~30 minutes

## 🔧 Troubleshooting

### Common Issues

#### 1. agent-browser not found

```bash
# Solution: Install agent-browser globally
npm install -g agent-browser
agent-browser install
```

#### 2. Tests timeout

```bash
# Solution: Check if app is running
curl http://localhost:3000

# Start the development server
cd client
npm run dev
```

#### 3. Element not found errors

**Possible causes:**
- Page not fully loaded
- Element reference changed
- Dynamic content not rendered

**Solution:**
- Increase timeout in `waitForElement()` calls
- Check element references in test files
- Take screenshots to debug

#### 4. Authentication failures

```bash
# Solution: Reset test user credentials
# Update testData.users.drChen in utils.ts

# Or create test user in app first
```

#### 5. Screenshots not saving

**Solution:**
```bash
# Create screenshots directory
mkdir -p tests/e2e/screenshots

# Check permissions
chmod 755 tests/e2e/screenshots
```

### Debug Mode

To debug failing tests, add console logging:

```typescript
// Before failing action
console.log('Current page:', await utils.getSnapshot());

// After action
await utils.takeScreenshot('debug-before-click.png');
await utils.clickElement('@button');
await utils.takeScreenshot('debug-after-click.png');
```

## 📈 Performance Metrics

Track test performance over time:

- **Test duration trends**
- **Success rate by feature**
- **Flaky test identification**
- **Common failure patterns**

Generate performance report:

```bash
npm run test:all > results.log
grep "Duration:" results.log
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          npm install -g agent-browser
          cd tests/e2e
          npm install
      - name: Start app
        run: |
          cd client
          npm install
          npm run build
          npm start &
      - name: Run tests
        run: |
          cd tests/e2e
          npm run test:all
```

## 📝 Test Maintenance

### Adding New Tests

1. Create new `.spec.ts` file
2. Import utilities from `utils.ts`
3. Follow Ralph Loop pattern:
   - Define test steps
   - Add assertions
   - Handle failures with screenshots
4. Add npm script in `package.json`
5. Update README with new test info

### Updating Test Data

Modify `testData` object in `utils.ts`:

```typescript
export const testData = {
  users: {
    newTestUser: {
      email: 'test@example.com',
      password: 'password123'
    }
  },
  queries: {
    newQuery: 'test search term'
  }
};
```

## 🎓 Best Practices

1. **Use descriptive test names** - Clearly explain what's being tested
2. **Wait for elements properly** - Use `waitForElement()` instead of fixed sleeps
3. **Take screenshots on failure** - Crucial for debugging
4. **Clean up test data** - Don't leave test artifacts
5. **Isolate tests** - Each test should run independently
6. **Use timeouts wisely** - Balance between reliability and speed
7. **Document assumptions** - Note prerequisites and setup requirements

## 📞 Support

For issues or questions:

1. Check this README's troubleshooting section
2. Review test logs and screenshots
3. Consult ULTIMATE_BUILD_DIRECTIVE.md for context
4. Review agent-browser documentation: https://github.com/vercel-labs/agent-browser

## 📚 Additional Resources

- [agent-browser Documentation](https://github.com/vercel-labs/agent-browser)
- [Project ULTIMATE_BUILD_DIRECTIVE.md](../../ULTIMATE_BUILD_DIRECTIVE.md)
- [Dr. Chen's Test Persona](../../ULTIMATE_BUILD_DIRECTIVE.md#-testing-persona-dr-chen)
