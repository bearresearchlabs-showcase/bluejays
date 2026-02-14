import Sidebar from '@/components/Sidebar'
import DatabasesCatalog from '@/components/DatabasesCatalog'
import { Box } from '@/components/design-system/layout/Box'

export default function DatabasesPage() {
  return (
    <Box style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <DatabasesCatalog />
    </Box>
  )
}
