import { ViewSelector } from '@/components/ViewSelector'
import { AnnotatorWorkbench } from '@/components/AnnotatorWorkbench'
import { SchemaViewWrapper } from '@/components/SchemaViewWrapper'

export default function AnnotatorPage() {
  return (
    <div className="container">
      <ViewSelector />
      <h1 className="text-xl font-semibold mb-2 text-[var(--fg)]">SQL Annotator</h1>
      <p className="text-sm text-[var(--fg-muted)] mb-6">
        Select a database, pick a query, and edit question, SQL, evidence, and difficulty. Save writes to queries.json.
      </p>
      <AnnotatorWorkbench />
      <SchemaViewWrapper />
    </div>
  )
}
