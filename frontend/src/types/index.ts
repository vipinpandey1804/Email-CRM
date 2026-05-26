export interface User {
  id: string
  email: string
  full_name: string
  is_staff: boolean
}

export interface Organization {
  id: number
  name: string
  slug: string
  is_active: boolean
  plan: string
  logo_url: string
}

export interface EmailTemplate {
  id: string
  name: string
  category: string
  thumbnail_url: string
  is_system: boolean
  gjs_components: Record<string, unknown>
  gjs_styles: Record<string, unknown>
  mjml_source: string
  html_output: string
  updated_at: string
}

export interface Campaign {
  id: string
  name: string
  subject_line: string
  preview_text: string
  from_name: string
  from_email: string
  reply_to: string
  tags: string[]
  status: 'draft' | 'scheduled' | 'sending' | 'sent' | 'failed'
  scheduled_at: string | null
  sent_at: string | null
  created_at: string
  template?: string | null
}

export interface CampaignRecipient {
  id: string
  email: string
  name: string
  status: 'queued' | 'sent' | 'failed'
  sent_at: string | null
  error_message: string
}

export interface AIJob {
  id: string
  job_type: string
  status: 'pending' | 'running' | 'done' | 'failed'
  input_data: Record<string, unknown>
  output_data: Record<string, unknown> | null
  created_at: string
  completed_at: string | null
}

export interface SMTPConfig {
  host: string
  port: number
  username: string
  use_tls: boolean
  use_ssl: boolean
  is_verified: boolean
}
