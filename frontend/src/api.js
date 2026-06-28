const BASE = "/api"

async function req(method, path, body, opts = {}) {
  const res = await fetch(BASE + path, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
    ...opts,
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export const api = {
  // Config
  getConfig: () => req("GET", "/config"),
  testConfig: (body) => req("POST", "/config/test", body),
  saveConfig: (body) => fetch(`${BASE}/config`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }).then(r => { if (!r.ok) throw new Error("Falha ao salvar config") }),

  // Health
  health: () => req("GET", "/health"),

  // Materials
  uploadMaterial: (materiaId, file) => {
    const form = new FormData()
    form.append("file", file)
    return fetch(`${BASE}/materials/upload?materia_id=${materiaId}`, { method: "POST", body: form })
      .then(r => r.ok ? r.json() : r.text().then(t => Promise.reject(t)))
  },
  materialProgress: (materialId) => new EventSource(`${BASE}/materials/${materialId}/progress`),

  // Graph
  getGraph: (materiaId) => req("GET", `/graph?materia_id=${materiaId}`),
  getNode: (nodeId) => req("GET", `/nodes/${nodeId}`),
  mergeNodes: (keepId, discardId) => req("POST", "/nodes/merge", { keep_id: keepId, discard_id: discardId }),

  // Study
  createSession: (materiaId) => req("POST", `/sessions?materia_id=${materiaId}`),
  addEvent: (sessionId, tipo, nodeId) => req("POST", `/sessions/${sessionId}/events`, { tipo, node_id: nodeId }),
  closeSession: (sessionId, autoavaliacao, pendente) => req("POST", `/sessions/${sessionId}/close`, { autoavaliacao, pendente }),

  // Flashcards
  getDueFlashcards: () => req("GET", "/flashcards/due"),
  generateFlashcard: (nodeId) => req("POST", `/flashcards/generate?node_id=${nodeId}`),
  reviewFlashcard: (flashcardId, quality) => req("POST", `/flashcards/${flashcardId}/review`, { quality }),

  // Exercises
  generateExercise: (nodeId) => req("POST", `/exercises/generate?node_id=${nodeId}`),

  // Exams
  getDiagnostic: (materiaId) => req("POST", `/exams/diagnostic?materia_id=${materiaId}`),
  getRevisionPlan: (materiaId, daysUntilExam) => req("POST", "/exams/plan", { materia_id: materiaId, days_until_exam: daysUntilExam }),
}
