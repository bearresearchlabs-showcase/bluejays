import Sidebar from '@/components/Sidebar'
import DocsContent from '@/components/DocsContent'
import { Box } from '@/components/design-system/layout/Box'

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

export default async function DocsPage({ 
  params 
}: { 
  params: Promise<{ id: string }> 
}) {
  const { id } = await params
  return (
    <Box style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <DocsContent dbId={id} />
    </Box>
  )
}
