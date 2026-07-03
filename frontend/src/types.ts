export type ContentType = "vocabulary" | "grammar";

export interface ContentItem {
  id: number;
  item_type: ContentType;
  text: string;
  translation: string;
  notes: string | null;
  difficulty_level: number;
}

export interface LearningItem {
  id: number;
  content_item: ContentItem;
  easiness_factor: number;
  interval_days: number;
  repetitions: number;
  next_review_at: string;
  last_reviewed_at: string | null;
}

export interface User {
  id: number;
  email: string;
  username: string;
  created_at: string;
}

export interface ReviewSubmission {
  learning_item_id: number;
  quality: number;
  response_time_ms?: number;
}
