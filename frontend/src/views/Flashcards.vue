<template>
  <div class="flashcards">
    <router-link to="/">← Painel</router-link>
    <h1>Flashcards para Revisão</h1>
    <p v-if="!due.length && loaded">Nenhum flashcard pendente 🎉</p>

    <div v-if="current" class="card" @click="flipped = !flipped">
      <div class="card-inner" :class="{ flipped }">
        <div class="front">{{ current.frente }}</div>
        <div class="back">{{ current.verso }}</div>
      </div>
      <p class="hint">{{ flipped ? "Clique para ver a pergunta" : "Clique para ver a resposta" }}</p>
    </div>

    <div v-if="current && flipped" class="review-btns">
      <button @click="review(1)" class="esqueci">✗ Esqueci</button>
      <button @click="review(5)" class="lembrei">✓ Lembrei</button>
    </div>

    <button v-if="reviewed.length" @click="exportCsv" class="export">Exportar CSV</button>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { api } from "../api.js"

const due = ref([])
const loaded = ref(false)
const idx = ref(0)
const flipped = ref(false)
const reviewed = ref([])

const current = computed(() => due.value[idx.value] || null)

onMounted(async () => { due.value = await api.getDueFlashcards(); loaded.value = true })

async function review(quality) {
  if (!current.value) return
  const result = await api.reviewFlashcard(current.value.id, quality)
  reviewed.value.push({ ...current.value, result })
  due.value.splice(idx.value, 1)
  flipped.value = false
}

function exportCsv() {
  const BOM = "\uFEFF"
  const header = "frente,verso,acertos,erros,proxima_revisao"
  const rows = reviewed.value.map(f =>
    [f.frente, f.verso, f.acertos || 0, f.erros || 0, f.result?.next_review || ""]
      .map(v => `"${String(v).replace(/"/g, '""')}"`)
      .join(",")
  )
  const blob = new Blob([BOM + [header, ...rows].join("\n")], { type: "text/csv;charset=utf-8;" })
  const url = URL.createObjectURL(blob)
  Object.assign(document.createElement("a"), { href: url, download: "flashcards.csv" }).click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.flashcards { max-width: 560px; margin: 40px auto; padding: 24px; font-family: sans-serif; text-align: center; }
.card { perspective: 800px; height: 200px; cursor: pointer; margin: 24px 0 8px; }
.card-inner { position: relative; width: 100%; height: 100%; transition: transform .5s; transform-style: preserve-3d; }
.card-inner.flipped { transform: rotateY(180deg); }
.front, .back { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; padding: 24px; border: 2px solid #5b9bd5; border-radius: 12px; backface-visibility: hidden; font-size: 18px; }
.back { transform: rotateY(180deg); background: #f0f7ff; }
.hint { font-size: 12px; color: #aaa; margin-bottom: 16px; }
.review-btns { display: flex; gap: 16px; justify-content: center; }
.esqueci { background: #ef4444; color: white; padding: 12px 24px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
.lembrei { background: #22c55e; color: white; padding: 12px 24px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
.export { margin-top: 32px; padding: 8px 16px; cursor: pointer; border: 1px solid #ccc; border-radius: 4px; }
</style>
