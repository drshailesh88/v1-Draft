import { spawn } from 'child_process';

interface TestResult {
  passed: boolean;
  error?: string;
  duration: number;
}

export class TestUtils {
  private baseUrl: string;
  
  constructor(baseUrl: string = 'http://localhost:3000') {
    this.baseUrl = baseUrl;
  }

  async runAgentBrowserCommand(args: string[]): Promise<string> {
    return new Promise((resolve, reject) => {
      const output: string[] = [];
      const errorOutput: string[] = [];
      
      const child = spawn('agent-browser', args);
      
      child.stdout.on('data', (data) => {
        output.push(data.toString());
      });
      
      child.stderr.on('data', (data) => {
        errorOutput.push(data.toString());
      });
      
      child.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Command failed with code ${code}: ${errorOutput.join('')}`));
        } else {
          resolve(output.join(''));
        }
      });
      
      child.on('error', (err) => {
        reject(err);
      });
    });
  }

  async openUrl(url: string): Promise<void> {
    await this.runAgentBrowserCommand(['open', url]);
  }

  async clickElement(ref: string): Promise<void> {
    await this.runAgentBrowserCommand(['click', ref]);
  }

  async fillInput(ref: string, value: string): Promise<void> {
    await this.runAgentBrowserCommand(['fill', ref, value]);
  }

  async takeScreenshot(filename: string): Promise<void> {
    await this.runAgentBrowserCommand(['screenshot', filename]);
  }

  async getSnapshot(): Promise<any> {
    const output = await this.runAgentBrowserCommand(['snapshot', '-i', '--json']);
    return JSON.parse(output);
  }

  async waitForElement(ref: string, timeout: number = 10000): Promise<void> {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      try {
        const snapshot = await this.getSnapshot();
        if (snapshot.elements.some((e: any) => e.ref === ref)) {
          return;
        }
      } catch (error) {
        // Element not found yet, continue waiting
      }
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    throw new Error(`Element ${ref} not found within ${timeout}ms`);
  }

  async getTextContent(ref: string): Promise<string> {
    const snapshot = await this.getSnapshot();
    const element = snapshot.elements.find((e: any) => e.ref === ref);
    return element?.text || '';
  }

  async assertElementExists(ref: string): Promise<boolean> {
    const snapshot = await this.getSnapshot();
    return snapshot.elements.some((e: any) => e.ref === ref);
  }

  async assertTextContains(ref: string, text: string): Promise<boolean> {
    const content = await this.getTextContent(ref);
    return content.toLowerCase().includes(text.toLowerCase());
  }
}

export const testData = {
  users: {
    drChen: {
      email: 'dr.chen@berkeley.edu',
      password: 'TestPass123!',
      name: 'Dr. Chen',
      institution: 'UC Berkeley'
    }
  },
  queries: {
    literature: 'AI-powered drug discovery',
    systematic: 'machine learning in drug discovery',
    aiWriter: 'The impact of AI on pharmaceutical research'
  },
  papers: [
    {
      title: 'AI in Drug Discovery: A Review',
      doi: '10.1038/s41587-023-02000-0',
      authors: ['Smith J', 'Johnson A', 'Williams B']
    },
    {
      title: 'Machine Learning for Drug Development',
      doi: '10.1126/science.abc1234',
      authors: ['Davis R', 'Miller K']
    },
    {
      title: 'Deep Learning in Pharma',
      doi: '10.1016/j.drudis.2023.03.015',
      authors: ['Chen L', 'Wang M', 'Zhang Y']
    }
  ]
};

export class TestAssertions {
  static assert(condition: boolean, message: string): void {
    if (!condition) {
      throw new Error(`Assertion failed: ${message}`);
    }
  }

  static assertContains(haystack: string, needle: string): void {
    if (!haystack.toLowerCase().includes(needle.toLowerCase())) {
      throw new Error(`Expected "${haystack}" to contain "${needle}"`);
    }
  }

  static assertGreaterThan(actual: number, expected: number, message?: string): void {
    if (actual <= expected) {
      throw new Error(message || `Expected ${actual} to be greater than ${expected}`);
    }
  }

  static assertEquals(actual: any, expected: any, message?: string): void {
    if (actual !== expected) {
      throw new Error(message || `Expected ${actual} to equal ${expected}`);
    }
  }
}

export async function loginAsDrChen(utils: TestUtils): Promise<void> {
  await utils.openUrl('http://localhost:3000/login');
  await utils.fillInput('@email', testData.users.drChen.email);
  await utils.fillInput('@password', testData.users.drChen.password);
  await utils.clickElement('@login-button');
  await utils.waitForElement('@dashboard', 15000);
}

export async function navigateToFeature(utils: TestUtils, feature: string): Promise<void> {
  await utils.openUrl(`http://localhost:3000/${feature}`);
  await utils.waitForElement('@page-content', 10000);
}

export async function createTestReport(testName: string, results: TestResult[]): void {
  console.log(`\n=== ${testName} Test Report ===`);
  console.log(`Total: ${results.length}`);
  console.log(`Passed: ${results.filter(r => r.passed).length}`);
  console.log(`Failed: ${results.filter(r => !r.passed).length}`);
  console.log(`Duration: ${results.reduce((sum, r) => sum + r.duration, 0)}ms`);
  
  results.forEach((result, index) => {
    if (!result.passed) {
      console.log(`\nTest ${index + 1} FAILED:`);
      console.log(`Error: ${result.error}`);
    }
  });
}

export async function runTestWithTimeout(test: () => Promise<void>, timeout: number = 60000): Promise<void> {
  return Promise.race([
    test(),
    new Promise<void>((_, reject) => {
      setTimeout(() => reject(new Error(`Test timed out after ${timeout}ms`)), timeout);
    })
  ]);
}
