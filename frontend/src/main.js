import { createApp } from "vue"
import { createRouter, createWebHistory } from "vue-router"
import App from "./App.vue"
import Settings from "./views/Settings.vue"
import Dashboard from "./views/Dashboard.vue"
import GraphView from "./views/GraphView.vue"
import StudySession from "./views/StudySession.vue"
import NodeDetail from "./views/NodeDetail.vue"
import Flashcards from "./views/Flashcards.vue"
import ExamDiagnostic from "./views/ExamDiagnostic.vue"

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/settings", component: Settings },
    { path: "/", component: Dashboard, meta: { requiresLLM: true } },
    { path: "/graph/:materiaId", component: GraphView, meta: { requiresLLM: true } },
    { path: "/study/:sessionId", component: StudySession, meta: { requiresLLM: true } },
    { path: "/nodes/:nodeId", component: NodeDetail, meta: { requiresLLM: true } },
    { path: "/flashcards", component: Flashcards, meta: { requiresLLM: true } },
    { path: "/exam/:materiaId", component: ExamDiagnostic, meta: { requiresLLM: true } },
  ],
})

// HARD GATE: redirect to /settings if LLM not configured
router.beforeEach((to) => {
  if (to.meta.requiresLLM && localStorage.getItem("llm_configured") !== "true") {
    return "/settings"
  }
})

createApp(App).use(router).mount("#app")
