<template>
  <div class="dashboard">
    <header>
      <h1>ETS — Painel</h1>
      <nav>
        <router-link to="/flashcards">Flashcards</router-link>
        <router-link to="/settings">Configurações</router-link>
      </nav>
    </header>

    <section>
      <h2>Matérias</h2>
      <div class="materias">
        <div v-for="m in materias" :key="m.id" class="card">
          <strong>{{ m.nome }}</strong>
          <div class="card-actions">
            <router-link :to="`/graph/${m.id}`"><button>Grafo</button></router-link>
            <router-link :to="`/exam/${m.id}`"><button>Diagnóstico</button></router-link>
            <button @click="startStudy(m.id)">Estudar</button>
            <button @click="triggerUpload(m.id)">Upload PDF</button>
          </div>
        </div>
      </div>

      <div class="new-materia">
        <input v-model="newNome" placeholder="Nome da nova matéria" @keyup.enter="createMateria" />
        <button @click="createMateria">Criar matéria</button>
      </div>
    </section>

    <section v-if="activeJobs.length">
      <h2>Em processamento</h2>
      <SSEProgress
        v-for="j in activeJobs"
        :key="j.materialId"
        :material-id="j.materialId"
        @done="removeJob(j.materialId)"
      />
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { api } from "../api.js"
import SSEProgress from "../components/SSEProgress.vue"

const router = useRouter()
const materias = ref([])
const activeJobs = ref([])
const newNome = ref("")

onMounted(async () => {
  try { materias.value = await fetch("/api/materias").then(r => r.ok ? r.json() : []) } catch {}
})

async function createMateria() {
  if (!newNome.value.trim()) return
  try {
    const r = await fetch("/api/materias", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome: newNome.value }),
    }).then(r => r.json())
    materias.value.push(r)
    newNome.value = ""
  } catch (e) { alert("Erro: " + e) }
}

function triggerUpload(materiaId) {
  const input = document.createElement("input")
  input.type = "file"; input.accept = ".pdf"
  input.onchange = async e => {
    const file = e.target.files[0]
    if (!file) return
    try {
      const r = await api.uploadMaterial(materiaId, file)
      activeJobs.value.push({ materialId: r.material_id })
    } catch (e) { alert("Erro no upload: " + e) }
  }
  input.click()
}

function removeJob(materialId) {
  activeJobs.value = activeJobs.value.filter(j => j.materialId !== materialId)
}

async function startStudy(materiaId) {
  const r = await api.createSession(materiaId)
  router.push(`/study/${r.session_id}`)
}
</script>

<style scoped>
.dashboard { max-width: 900px; margin: 0 auto; padding: 24px; font-family: sans-serif; }
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
nav { display: flex; gap: 16px; }
.materias { display: flex; flex-wrap: wrap; gap: 16px; margin: 16px 0; }
.card { border: 1px solid #eee; border-radius: 8px; padding: 16px; min-width: 220px; }
.card-actions { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
button { padding: 6px 12px; cursor: pointer; border: 1px solid #ccc; border-radius: 4px; background: white; }
.new-materia { display: flex; gap: 8px; margin-top: 16px; }
.new-materia input { padding: 8px; border: 1px solid #ccc; border-radius: 4px; flex: 1; }
</style>
