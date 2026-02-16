/**
 * Message queue client for microservices (SSO-style architecture).
 * In-memory by default; extend with Redis (ioredis) when REDIS_URL is set for production.
 * Message types: task_assigned, task_updated, audit_complete, session_sync
 */

export type QueueMessage = {
  id: string
  type: string
  payload: Record<string, unknown>
  createdAt: number
}

type SubscriberCallback = (msg: QueueMessage) => void

const memoryQueue: QueueMessage[] = []
const subscribers = new Map<string, Set<SubscriberCallback>>()

function generateId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
}

function notifySubscribers(type: string, msg: QueueMessage): void {
  const wildcard = subscribers.get('*')
  if (wildcard) {
    wildcard.forEach((cb) => {
      try {
        cb(msg)
      } catch {
        // ignore subscriber errors
      }
    })
  }
  const typeSubs = subscribers.get(type)
  if (typeSubs) {
    typeSubs.forEach((cb) => {
      try {
        cb(msg)
      } catch {
        // ignore subscriber errors
      }
    })
  }
}

/**
 * Subscribe to messages by type. Use '*' for all types.
 * Returns unsubscribe function.
 */
export function subscribe(type: string, callback: SubscriberCallback): () => void {
  let set = subscribers.get(type)
  if (!set) {
    set = new Set()
    subscribers.set(type, set)
  }
  set.add(callback)
  return () => {
    set!.delete(callback)
    if (set!.size === 0) subscribers.delete(type)
  }
}

/**
 * Push a message to the queue.
 * Notifies subscribers synchronously (in-memory).
 */
export async function push(type: string, payload: Record<string, unknown>): Promise<string> {
  const id = generateId()
  const msg: QueueMessage = { id, type, payload, createdAt: Date.now() }
  memoryQueue.push(msg)
  notifySubscribers(type, msg)
  return id
}

/**
 * Pop a message from the queue (FIFO).
 */
export async function pop(): Promise<QueueMessage | null> {
  return memoryQueue.shift() ?? null
}
