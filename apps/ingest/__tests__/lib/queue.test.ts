/**
 * Message queue: push/pop FIFO, subscribe receives messages
 * No Redis in tests (mock or skip when REDIS_URL unset)
 */
import { push, pop, subscribe } from '@/lib/queue'

beforeEach(async () => {
  while (await pop()) {
    // drain queue
  }
})

describe('Queue push/pop', () => {
  it('push returns message id', async () => {
    const id = await push('task_updated', { source: 'db-1', question_id: 1 })
    expect(id).toMatch(/^msg_\d+_[a-z0-9]+$/)
  })

  it('pop returns messages in FIFO order', async () => {
    await push('task_updated', { a: 1 })
    await push('audit_complete', { b: 2 })
    const first = await pop()
    const second = await pop()
    const third = await pop()
    expect(first).not.toBeNull()
    expect(first!.type).toBe('task_updated')
    expect(first!.payload).toEqual({ a: 1 })
    expect(second).not.toBeNull()
    expect(second!.type).toBe('audit_complete')
    expect(third).toBeNull()
  })
})

describe('Queue subscribe', () => {
  it('subscribe receives messages for matching type', async () => {
    const received: unknown[] = []
    const unsub = subscribe('task_updated', (msg) => {
      received.push(msg)
    })
    await push('task_updated', { source: 'db-1', question_id: 1 })
    await push('audit_complete', { source: 'db-1', audit_status: 'Fixed' })
    expect(received.length).toBe(1)
    expect(received[0]).toMatchObject({ type: 'task_updated', payload: { source: 'db-1', question_id: 1 } })
    unsub()
  })

  it('wildcard subscriber receives all message types', async () => {
    const received: unknown[] = []
    const unsub = subscribe('*', (msg) => {
      received.push(msg)
    })
    await push('task_updated', { a: 1 })
    await push('audit_complete', { b: 2 })
    await push('session_sync', { c: 3 })
    expect(received.length).toBe(3)
    unsub()
  })

  it('unsubscribe stops receiving', async () => {
    const received: unknown[] = []
    const unsub = subscribe('task_updated', (msg) => {
      received.push(msg)
    })
    await push('task_updated', { a: 1 })
    unsub()
    await push('task_updated', { b: 2 })
    expect(received.length).toBe(1)
  })
})
