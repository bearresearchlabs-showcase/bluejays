import Sidebar from '@/components/Sidebar'
import DatabaseDetailView from '@/components/DatabaseDetailView'
import DatabaseContent from '@/components/DatabaseContent'
import { Box } from '@/components/design-system/layout/Box'
import { Stack } from '@/components/design-system/layout/Stack'

export async function generateStaticParams() {
  return [
    { id: 'db6' },
    { id: 'db7' },
    { id: 'db8' },
    { id: 'db9' },
    { id: 'db10' },
    { id: 'db11' },
    { id: 'db12' },
    { id: 'db13' },
    { id: 'db14' },
    { id: 'db15' },
  ]
}

export default async function DatabasePage({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = await params
  return (
    <Box style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <Box style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <DatabaseDetailView dbId={id} />
        <Box style={{ borderTop: '2px solid var(--color-border-primary)', marginTop: 'var(--spacing-8)', paddingTop: 'var(--spacing-8)' }}>
          <DatabaseContent dbId={id} />
        </Box>
      </Box>
    </Box>
  )
}
