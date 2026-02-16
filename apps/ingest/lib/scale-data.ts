/**
 * Scale-style data loading: maps source/db-N queries to Dataset/Delivery/Task model
 */
import { discoverSources, loadQueries } from './data'
import type { Dataset, DatasetTask, DatasetDelivery } from './scale-types'

const DEFAULT_DELIVERY = 'default'
const PAGE_SIZE = 100

export function listDatasets(): Dataset[] {
  const sources = discoverSources().filter((s) => s.startsWith('db-'))
  return sources.map((name) => ({
    dataset_id: name,
    name,
    task_count: 30,
  }))
}

export function getTask(dataset: string, taskId: string): DatasetTask | null {
  const { queries, error } = loadQueries(dataset)
  if (error || !queries.length) return null

  const num = parseInt(taskId, 10)
  if (isNaN(num) || num < 1 || num > queries.length) return null

  const q = queries[num - 1] as Record<string, unknown>
  return {
    task_id: `${dataset}-${num}`,
    dataset,
    delivery: DEFAULT_DELIVERY,
    response: {
      number: num,
      title: q.title as string,
      description: q.description as string,
      sql: q.sql as string,
      question: q.question as string,
      question_id: num,
      ...q,
    },
  }
}

export function getDelivery(
  deliveryId: string,
  nextToken?: string
): DatasetDelivery | null {
  const effectiveDataset = deliveryId.replace(/-delivery-.*$/, '') || deliveryId
  const { queries, error } = loadQueries(effectiveDataset)
  if (error || !queries.length) return null

  const offset = nextToken ? parseInt(nextToken, 10) || 0 : 0
  const slice = queries.slice(offset, offset + PAGE_SIZE)
  const tasks: DatasetTask[] = slice.map((q, i) => {
    const n = offset + i + 1
    const rec = q as Record<string, unknown>
    return {
      task_id: `${effectiveDataset}-${n}`,
      dataset: effectiveDataset,
      delivery: DEFAULT_DELIVERY,
      response: {
        number: n,
        title: rec.title as string,
        description: rec.description as string,
        sql: rec.sql as string,
        question: rec.question as string,
        question_id: n,
        ...rec,
      },
    }
  })

  const hasMore = offset + PAGE_SIZE < queries.length
  return {
    delivery_id: `${effectiveDataset}-delivery-${DEFAULT_DELIVERY}`,
    dataset: effectiveDataset,
    tasks,
    next_token: hasMore ? String(offset + PAGE_SIZE) : undefined,
  }
}

export function searchTasks(
  dataset?: string,
  delivery?: string,
  nextToken?: string
): { tasks: DatasetTask[]; next_token?: string } {
  const sources = dataset ? [dataset] : discoverSources().filter((s) => s.startsWith('db-'))
  const tasks: DatasetTask[] = []
  const offset = nextToken ? parseInt(nextToken, 10) || 0 : 0

  for (const ds of sources) {
    const { queries, error } = loadQueries(ds)
    if (error || !queries.length) continue

    const start = dataset === ds ? offset : 0
    const end = Math.min(start + PAGE_SIZE, queries.length)

    for (let i = start; i < end; i++) {
      const q = queries[i] as Record<string, unknown>
      const n = i + 1
      tasks.push({
        task_id: `${ds}-${n}`,
        dataset: ds,
        delivery: delivery || DEFAULT_DELIVERY,
        response: {
          number: n,
          title: q.title as string,
          description: q.description as string,
          sql: q.sql as string,
          question: q.question as string,
          question_id: n,
          ...q,
        },
      })
    }
  }

  const hasMore = tasks.length >= PAGE_SIZE
  return {
    tasks,
    next_token: hasMore ? String(offset + PAGE_SIZE) : undefined,
  }
}
