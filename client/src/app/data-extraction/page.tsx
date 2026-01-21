'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useRouter } from 'next/navigation'

interface TableData {
  table_id: string
  page: number
  data: string[][]
  csv: string
}

export default function DataExtractionPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [documents, setDocuments] = useState<any[]>([])
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null)
  const [tables, setTables] = useState<TableData[]>([])
  const [extracting, setExtracting] = useState(false)
  const API_URL = process.env.NEXT_PUBLIC_API_URL || ''

  useEffect(() => {
    if (!loading && !user) router.push('/login')
    else if (user) fetchDocuments()
  }, [user, loading, router])

  const fetchDocuments = async () => {
    const { data } = await supabase
      .from('documents')
      .select('*')
      .eq('user_id', user?.id)
      .order('created_at', { ascending: false })
    setDocuments(data || [])
  }

  const handleExtractTables = async () => {
    if (!selectedDoc) return
    setExtracting(true)
    try {
      const token = (await supabase.auth.getSession()).data.session?.access_token
      const res = await fetch(`${API_URL}/api/data-extraction/extract-tables`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_id: selectedDoc, token }),
      })
      if (!res.ok) throw new Error('Extraction failed')
      const data = await res.json()
      setTables(data.tables)
    } catch (error: any) {
      alert(error.message)
    } finally {
      setExtracting(false)
    }
  }

  const handleExportCSV = (table: TableData) => {
    const blob = new Blob([table.csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `table-${table.table_id}.csv`
    a.click()
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Data Extraction</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="block mb-2">Select Document</label>
                <select
                  value={selectedDoc || ''}
                  onChange={(e) => setSelectedDoc(e.target.value)}
                  className="w-full p-2 border rounded"
                >
                  <option value="">-- Select a document --</option>
                  {documents.map((doc) => (
                    <option key={doc.id} value={doc.id}>
                      {doc.title || doc.filename}
                    </option>
                  ))}
                </select>
              </div>
              <Button onClick={handleExtractTables} disabled={!selectedDoc || extracting}>
                {extracting ? 'Extracting...' : 'Extract Tables'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {tables.length > 0 && (
          <div className="mt-6 space-y-6">
            <h3 className="text-xl font-semibold">Extracted Tables ({tables.length})</h3>
            {tables.map((table) => (
              <Card key={table.table_id}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <CardTitle>Table {table.table_id} (Page {table.page})</CardTitle>
                    <Button size="sm" onClick={() => handleExportCSV(table)}>
                      Export CSV
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          {table.data[0]?.map((cell, idx) => (
                            <TableHead key={idx}>{cell}</TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {table.data.slice(1).map((row, rowIdx) => (
                          <TableRow key={rowIdx}>
                            {row.map((cell, cellIdx) => (
                              <TableCell key={cellIdx}>{cell}</TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}