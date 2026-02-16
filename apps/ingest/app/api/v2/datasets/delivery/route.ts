import { NextRequest, NextResponse } from 'next/server'
import { getSession } from '@/lib/auth'
import { getDelivery } from '@/lib/scale-data'

export async function GET(request: NextRequest) {
  const session = await getSession()
  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  const deliveryId = request.nextUrl.searchParams.get('delivery_id')
  const nextToken = request.nextUrl.searchParams.get('next_token') ?? undefined
  if (!deliveryId) {
    return NextResponse.json({ error: 'delivery_id required' }, { status: 400 })
  }
  const dataset = deliveryId.startsWith('db-') && !deliveryId.includes('-delivery-')
    ? deliveryId
    : deliveryId.replace(/-delivery-.*$/, '')
  const delivery = getDelivery(`${dataset}-delivery-default`, nextToken)
  if (!delivery) {
    return NextResponse.json({ error: 'Delivery not found' }, { status: 404 })
  }
  return NextResponse.json(delivery)
}
