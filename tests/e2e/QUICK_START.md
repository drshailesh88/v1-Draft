# E2E Testing Quick Start Guide

Quick setup and execution guide for E2E tests using agent-browser.

## 🚀 5-Minute Setup

### Step 1: Install agent-browser (2 min)

```bash
# Install globally
npm install -g agent-browser

# Install browser drivers
agent-browser install
```

### Step 2: Install test dependencies (1 min)

```bash
cd tests/e2e
npm install
```

### Step 3: Start the application (1 min)

```bash
# In one terminal
cd client
npm run dev
```

### Step 4: Run tests (1 min)

```bash
# In another terminal
cd tests/e2e
npm run test:all
```

## 📋 Test Suite Overview

| Test File | What It Tests | Duration |
|-----------|---------------|----------|
| `literature-review.spec.ts` | Literature search, save, export, chat, data extraction | ~3 min |
| `systematic-review.spec.ts` | PRISMA workflow, screening, diagrams | ~5 min |
| `ai-writer.spec.ts` | Project creation, generation, citations, export | ~10 min |
| `nature-review.spec.ts` | Complete 500+ paper review workflow | ~30 min |

## 🏃 Running Specific Tests

### Literature Review Only

```bash
npm run test:literature
```

### Systematic Review Only

```bash
npm run test:systematic
```

### AI Writer Only

```bash
npm run test:ai-writer
```

### Full Nature Review

```bash
npm run test:nature
```

### All Tests

```bash
npm run test:all
# Or from root:
npm run test:e2e
```

## 🔧 Troubleshooting Common Issues

### "agent-browser: command not found"

```bash
npm install -g agent-browser
```

### "Timeout waiting for element"

- Check if app is running at http://localhost:3000
- Increase timeout in test file
- Take screenshot to debug

### "Element not found"

- Use `agent-browser snapshot -i --json` to find correct refs
- Add `data-testid` attributes to components
- Check if page is fully loaded

### Tests failing randomly

- Run tests in isolation
- Check for flaky test patterns
- Add explicit waits before actions

## 📊 Interpreting Results

### Success

```
✅ All Literature Review tests passed!
Total: 5
Passed: 5
Failed: 0
Duration: 15234ms
```

### Failure

```
❌ Some tests failed. Check logs above.

Test 3 FAILED:
Error: Element @save-button not found within 10000ms
```

**Next Steps**:
1. Check screenshot in `screenshots/` folder
2. Review error message
3. Fix the issue in code
4. Re-run test: `npm run test:literature`

## 🔄 Ralph Loop Testing

Follow this cycle for each feature:

```
1. Run test → See failure
2. Identify problem → Read error + screenshot
3. Fix code → Apply minimal fix
4. Run test again → Verify fix works
5. Repeat until all pass → Exit cycle
```

## 📁 Project Structure

```
tests/e2e/
├── README.md                    # Full documentation
├── RALPH_LOOP.md              # Ralph Loop framework guide
├── .env.example               # Environment variables template
├── package.json               # Test dependencies and scripts
├── tsconfig.json             # TypeScript configuration
├── utils.ts                 # Core testing utilities
├── fixtures.ts              # Test data fixtures
├── literature-review.spec.ts  # Literature workflow tests
├── systematic-review.spec.ts   # PRISMA workflow tests
├── ai-writer.spec.ts         # AI Writer tests
├── nature-review.spec.ts      # Full Nature review tests
└── screenshots/              # Failure screenshots (auto-generated)
```

## 🎯 Dr. Chen's Persona

Tests simulate Dr. Chen's workflow:

- **Profile**: PhD from MIT, Postdoc at Stanford, Professor at UC Berkeley
- **Goal**: Submit systematic review on "AI-Powered Drug Discovery" to Nature
- **Requirements**:
  - 500+ papers reviewed
  - PRISMA methodology
  - Data extraction from 200 papers
  - Full paper generation
  - Nature submission-ready export

## 📝 Customizing Tests

### Change Test Data

Edit `fixtures.ts`:

```typescript
export const testData = {
  users: {
    drChen: {
      email: 'your-email@example.com',
      password: 'your-password'
    }
  },
  queries: {
    literature: 'your-search-term'
  }
};
```

### Add New Test Steps

```typescript
await utils.openUrl('/your-page');
await utils.clickElement('@your-button');
await utils.waitForElement('@your-result', 10000);
TestAssertions.assert(true, 'Your test description');
```

## 🔍 Debug Mode

Enable verbose logging:

```typescript
// In test file
console.log('Current snapshot:', await utils.getSnapshot());
await utils.takeScreenshot('debug.png');
```

## 📈 CI/CD Integration

Add to your pipeline:

```yaml
- name: Run E2E Tests
  run: |
    npm install -g agent-browser
    cd tests/e2e
    npm install
    npm run test:all
```

## 💡 Tips

1. **Start small**: Run one test at a time
2. **Check logs**: Read error messages carefully
3. **Use screenshots**: Visual debugging is faster
4. **Iterate quickly**: Fix one issue, test again
5. **Document changes**: Note what you fixed and why

## 🆘 Getting Help

1. Check README.md for detailed docs
2. Review RALPH_LOOP.md for testing methodology
3. Check ULTIMATE_BUILD_DIRECTIVE.md for context
4. Search issues on agent-browser GitHub

## 📞 Support Channels

- agent-browser: https://github.com/vercel-labs/agent-browser
- Project docs: ../ULTIMATE_BUILD_DIRECTIVE.md
- Testing framework: ./RALPH_LOOP.md

---

**Happy Testing! 🎉**
