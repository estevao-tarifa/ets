import { ref } from "vue"
import { api } from "../api.js"

export function useSession() {
  const sessionId = ref(null)
  const events = ref([])

  async function startSession(materiaId) {
    const r = await api.createSession(materiaId)
    sessionId.value = r.session_id
    events.value = []
    return r.session_id
  }

  // Max 2 interactions: tipo (required) + nodeId (optional)
  async function addEvent(tipo, nodeId = null) {
    if (!sessionId.value) throw new Error("No active session")
    const r = await api.addEvent(sessionId.value, tipo, nodeId)
    events.value.push({ tipo, nodeId, id: r.event_id })
    return r
  }

  async function closeSession(autoavaliacao, pendente = null) {
    if (!sessionId.value) throw new Error("No active session")
    await api.closeSession(sessionId.value, autoavaliacao, pendente)
    sessionId.value = null
  }

  return { sessionId, events, startSession, addEvent, closeSession }
}
