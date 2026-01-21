import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import Link from 'next/link'

export default function Home() {
  const { user } = useAuth()

  const features = [
    { title: 'Chat with PDF', desc: 'Ask questions about your PDFs with AI-powered answers', path: '/chat' },
    { title: 'Literature Search', desc: 'Search PubMed, arXiv, Semantic Scholar', path: '/literature' },
    { title: 'Find Topics', desc: 'Discover research topics and trending papers', path: '/topics' },
    { title: 'AI Writer', desc: 'Draft academic papers section by section', path: '/ai-writer' },
    { title: 'Paraphraser', desc: 'Rewrite text while preserving meaning', path: '/paraphraser' },
    { title: 'Citation Generator', desc: 'Generate citations in multiple formats', path: '/citations' },
    { title: 'Citation Booster', desc: 'Enhance and enrich your citations', path: '/citation-booster' },
    { title: 'Data Extraction', desc: 'Extract tables and figures from PDFs', path: '/data-extraction' },
    { title: 'AI Detector', desc: 'Detect AI-generated content', path: '/ai-detector' },
    { title: 'Systematic Review', desc: 'Conduct systematic literature reviews', path: '/systematic-review' },
    { title: 'Deep Review', desc: 'Comprehensive paper analysis and insights', path: '/deep-review' },
    { title: 'Subscription', desc: 'Manage your subscription and billing', path: '/subscription' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <nav className="border-b">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Sci-Space Clone</h1>
          <div className="flex gap-2">
            {user ? (
              <Link href="/chat">
                <Button variant="outline">Dashboard</Button>
              </Link>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="ghost">Sign In</Button>
                </Link>
                <Link href="/signup">
                  <Button>Sign Up</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h2 className="text-5xl font-bold mb-4">Academic Research Platform</h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            AI-powered tools for researchers: analyze papers, generate citations, extract data, and more
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature) => (
            <Card key={feature.title} className="hover:shadow-lg transition">
              <CardHeader>
                <CardTitle>{feature.title}</CardTitle>
                <CardDescription>{feature.desc}</CardDescription>
              </CardHeader>
              <CardContent>
                <Link href={feature.path}>
                  <Button className="w-full">Open Tool</Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  )
}