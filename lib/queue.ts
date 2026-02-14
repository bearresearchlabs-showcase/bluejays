/**
 * Message queue client for microservices (SSO-style architecture).
 * In-memory by default; extend with Redis (ioredis) when REDIS_URL is set for production.
 */

export type QueueMessage = {
  id: string
  type: string
  payload: Record<string, unknown>
  createdAt: number
}

const memoryQueue: QueueMessage[] = []

function generateId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
}

/**
 * Push a message to the queue.
 */
export async function push(type: string, payload: Record<string, unknown>): Promise<string> {
  const id = generateId()
  memoryQueue.push({ id, type, payload, createdAt: Date.now() })
  return id
}

/**
 * Pop a message from the queue (FIFO).
 */
export async function pop(): Promise<QueueMessage | null> {
  return memoryQueue.shift() ?? null
}
