import { useState, useEffect, useRef } from 'react'
import { Upload, FileText, CheckCircle, XCircle, MinusCircle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { reportsAPI } from '../api'

// Nomes "amigaveis" das 15 tabelas (ordem = ordem do resumo do backend)
const TABLE_LABELS: Record<string, string> = {
  invest_executed_trades: 'Invest · Executed trades',
  invest_pending_orders: 'Invest · Pending orders',
  invest_open_positions: 'Invest · Open positions',
  invest_transactions: 'Invest · Transactions',
  invest_dividends: 'Invest · Dividends',
  cfd_executed_trades: 'CFD · Executed trades',
  cfd_pending_orders: 'CFD · Pending orders',
  cfd_open_positions: 'CFD · Open positions',
  cfd_transactions: 'CFD · Transactions',
  cfd_dividend_adjustments: 'CFD · Dividend adjustments',
  cfd_overnight_interest: 'CFD · Overnight interest',
  crypto_executed_trades: 'Crypto · Executed trades',
  crypto_pending_orders: 'Crypto · Pending orders',
  crypto_open_positions: 'Crypto · Open positions',
  crypto_transactions: 'Crypto · Transactions',
}
const TABLE_ORDER = Object.keys(TABLE_LABELS)

interface ProcessedFile {
  id: string
  file_name: string
  customer_id: string | null
  customer_name: string | null
  period_start: string | null
  period_end: string | null
  generated_at: string | null
  pages: number | null
  status: string
  imported_at: string | null
}

interface UploadResult {
  file_name: string
  status: string
  reason?: string
  total_inserted: number
  inserted: Record<string, number>
}

interface UploadResponse {
  files_processed: number
  grand_total: Record<string, number>
  grand_total_inserted: number
  results: UploadResult[]
}

export default function ReportsPage() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadResponse, setUploadResponse] = useState<UploadResponse | null>(null)
  const [files, setFiles] = useState<ProcessedFile[]>([])
  const [summary, setSummary] = useState<{ total_files: number; imported: number; failed: number } | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const loadData = async () => {
    try {
      const [filesRes, summaryRes] = await Promise.all([
        reportsAPI.listFiles(),
        reportsAPI.summary(),
      ])
      setFiles(filesRes.data || [])
      setSummary(summaryRes.data || null)
    } catch (err) {
      console.error('[ReportsPage] Failed to load reports data', err)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const list = e.target.files ? Array.from(e.target.files) : []
    setSelectedFiles(list)
    setUploadResponse(null)
  }

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return
    setUploading(true)
    try {
      const res = await reportsAPI.upload(selectedFiles)
      setUploadResponse(res.data)
      console.log('[ReportsPage] Upload complete', res.data)
      setSelectedFiles([])
      if (inputRef.current) inputRef.current.value = ''
      await loadData()
    } catch (err) {
      console.error('[ReportsPage] Upload failed', err)
    } finally {
      setUploading(false)
    }
  }

  const statusBadge = (status: string) => {
    const s = status?.toLowerCase()
    if (s === 'imported') {
      return (
        <span className="inline-flex items-center gap-1 text-t212-success text-xs font-medium">
          <CheckCircle size={14} /> Imported
        </span>
      )
    }
    if (s === 'skipped') {
      return (
        <span className="inline-flex items-center gap-1 text-t212-muted text-xs font-medium">
          <MinusCircle size={14} /> Skipped
        </span>
      )
    }
    return (
      <span className="inline-flex items-center gap-1 text-t212-error text-xs font-medium">
        <XCircle size={14} /> Failed
      </span>
    )
  }

  const fmtDate = (d: string | null) => {
    if (!d) return '—'
    // aceita 'YYYY-MM-DD' ou ISO timestamp
    return d.length > 10 ? new Date(d).toLocaleString() : d
  }

  return (
    <div className="space-y-6">
      {/* KPI: numero de ficheiros carregados */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardContent>
            <p className="text-xs text-t212-muted mb-1">Files uploaded</p>
            <p className="text-3xl font-bold text-t212-primary">{summary?.total_files ?? 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <p className="text-xs text-t212-muted mb-1">Imported</p>
            <p className="text-3xl font-bold text-t212-success">{summary?.imported ?? 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <p className="text-xs text-t212-muted mb-1">Failed</p>
            <p className="text-3xl font-bold text-t212-error">{summary?.failed ?? 0}</p>
          </CardContent>
        </Card>
      </div>

      {/* Upload */}
      <Card>
        <CardHeader>
          <CardTitle>Upload Activity Statements</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4">
            <label
              htmlFor="report-upload"
              className="flex flex-col items-center justify-center gap-2 border-2 border-dashed border-t212-border rounded-xl py-10 cursor-pointer hover:border-t212-primary transition-colors"
            >
              <Upload size={28} className="text-t212-muted" />
              <span className="text-sm text-t212-secondary">
                Click to select one or more PDF files
              </span>
              <input
                id="report-upload"
                ref={inputRef}
                type="file"
                accept="application/pdf,.pdf"
                multiple
                onChange={handleSelect}
                className="hidden"
              />
            </label>

            {selectedFiles.length > 0 && (
              <div className="space-y-1">
                {selectedFiles.map((f) => (
                  <div key={f.name} className="flex items-center gap-2 text-sm text-t212-secondary">
                    <FileText size={14} /> {f.name}
                  </div>
                ))}
              </div>
            )}

            <div>
              <Button
                variant="primary"
                size="md"
                onClick={handleUpload}
                isLoading={uploading}
                disabled={uploading || selectedFiles.length === 0}
                icon={<Upload size={16} />}
              >
                Upload {selectedFiles.length > 0 ? `(${selectedFiles.length})` : ''}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Resumo do ultimo upload */}
      {uploadResponse && (
        <Card>
          <CardHeader>
            <CardTitle>Import summary</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Por ficheiro */}
            <div className="space-y-2 mb-6">
              {uploadResponse.results.map((r) => (
                <div
                  key={r.file_name}
                  className="flex items-center justify-between p-3 rounded-lg bg-t212-hover border border-t212-border"
                >
                  <div className="flex items-center gap-2">
                    <FileText size={16} className="text-t212-muted" />
                    <span className="text-sm text-t212-primary">{r.file_name}</span>
                    {r.reason && <span className="text-xs text-t212-muted">({r.reason})</span>}
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-t212-secondary">{r.total_inserted} rows</span>
                    {statusBadge(r.status)}
                  </div>
                </div>
              ))}
            </div>

            {/* Registos inseridos por tabela (agregado) */}
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-t212-muted border-b border-t212-border">
                    <th className="py-2 pr-4 font-medium">Table</th>
                    <th className="py-2 font-medium text-right">Records inserted</th>
                  </tr>
                </thead>
                <tbody>
                  {TABLE_ORDER.map((t) => (
                    <tr key={t} className="border-b border-t212-border/50">
                      <td className="py-2 pr-4 text-t212-secondary">{TABLE_LABELS[t]}</td>
                      <td className="py-2 text-right text-t212-primary">
                        {uploadResponse.grand_total[t] ?? 0}
                      </td>
                    </tr>
                  ))}
                  <tr>
                    <td className="py-2 pr-4 font-semibold text-t212-primary">Total</td>
                    <td className="py-2 text-right font-semibold text-t212-primary">
                      {uploadResponse.grand_total_inserted}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Ficheiros processados */}
      <Card>
        <CardHeader>
          <CardTitle>Processed files</CardTitle>
        </CardHeader>
        <CardContent>
          {files.length === 0 ? (
            <p className="text-t212-secondary text-sm">No files processed yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-t212-muted border-b border-t212-border">
                    <th className="py-2 pr-4 font-medium">ID</th>
                    <th className="py-2 pr-4 font-medium">File</th>
                    <th className="py-2 pr-4 font-medium">Period start</th>
                    <th className="py-2 pr-4 font-medium">Period end</th>
                    <th className="py-2 pr-4 font-medium">Uploaded at</th>
                    <th className="py-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {files.map((f) => (
                    <tr key={f.id} className="border-b border-t212-border/50">
                      <td className="py-2 pr-4 text-t212-muted font-mono text-xs" title={f.id}>
                        {f.id.slice(0, 8)}…
                      </td>
                      <td className="py-2 pr-4 text-t212-secondary">{f.file_name}</td>
                      <td className="py-2 pr-4 text-t212-secondary">{fmtDate(f.period_start)}</td>
                      <td className="py-2 pr-4 text-t212-secondary">{fmtDate(f.period_end)}</td>
                      <td className="py-2 pr-4 text-t212-secondary">{fmtDate(f.imported_at)}</td>
                      <td className="py-2">{statusBadge(f.status)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
