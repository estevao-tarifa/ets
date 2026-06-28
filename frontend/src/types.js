/**
 * @typedef {{ id: number, materia_id: number, nome: string, nivel: string, descricao: string|null, dominio_score: number|null, color: string }} KnowledgeNode
 * @typedef {{ id: number, materia_id: number, status: string, iniciada_em: string }} Session
 * @typedef {{ id: number, session_id: number, node_id: number|null, tipo: string }} SessionEvent
 * @typedef {{ id: number, node_id: number, frente: string, verso: string, ease_factor: number, interval_days: number, next_review: string }} Flashcard
 * @typedef {{ id: number, material_id: number, status: string, current_step: string|null }} ProcessingJob
 * @typedef {{ node_id: number, nome: string, dominio: number|null, risco_score: number }} ExamDiagnostic
 */
export {}
