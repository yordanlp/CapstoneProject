export interface Image {
  id: number,
  name: string,
  user_id: number,
  mime_type: string,
  model: string,
  status_process?: string | null
}
