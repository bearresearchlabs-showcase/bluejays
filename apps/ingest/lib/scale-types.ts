/**
 * Scale AI Data Engine model types
 * https://docs.genai.scale.com
 * Mapping: 1 Dataset = 1 db-N; 1 Delivery = 30 queries; 1 Task = 1 query
 */

export interface DatasetTask {
  task_id: string
  dataset: string
  delivery: string
  response: {
    number?: number
    title?: string
    description?: string
    sql?: string
    question?: string
    question_id?: number
    [key: string]: unknown
  }
}

export interface DatasetDelivery {
  delivery_id: string
  dataset: string
  tasks: DatasetTask[]
  next_token?: string
}

export interface Dataset {
  dataset_id: string
  name: string
  task_count?: number
}
