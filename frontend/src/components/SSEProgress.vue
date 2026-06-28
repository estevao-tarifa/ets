<template>
  <div v-if="visible" class="sse-progress">
    <p class="title">Processando material...</p>
    <div v-for="step in STEPS" :key="step.key" class="step">
      <span class="icon">{{ stepIcon(step.key) }}</span>
      <span>{{ step.label }}</span>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from "vue"

const props = defineProps({ materialId: Number })
const emit = defineEmits(["done"])

const visible = ref(true)
const completed = ref(new Set())
const current = ref(null)
const error = ref(null)

const STEPS = [
  { key: "pdf_to_md", label: "PDF → Markdown" },
  { key: "extraction", label: "Extração de conceitos" },
  { key: "normalization", label: "Normalização" },
  { key: "deduplication", label: "Deduplicação" },
  { key: "graph", label: "Construindo grafo" },
  { key: "embeddings", label: "Gerando embeddings" },
]

const es = new EventSource(`/api/materials/${props.materialId}/progress`)
es.onmessage = ({ data }) => {
  const event = JSON.parse(data)
  if (event.step) { completed.value.add(event.step); current.value = event.step }
  if (event.status === "done") { visible.value = false; emit("done"); es.close() }
  if (event.status === "failed") { error.value = "Processamento falhou"; es.close() }
}

function stepIcon(key) {
  if (completed.value.has(key)) return "✓"
  if (current.value === key) return "⏳"
  return "○"
}

onUnmounted(() => es.close())
</script>

<style scoped>
.sse-progress { background: #f0f7ff; border: 1px solid #5b9bd5; border-radius: 8px; padding: 16px; margin: 8px 0; }
.title { font-weight: bold; margin-bottom: 8px; }
.step { display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 14px; }
.icon { width: 20px; text-align: center; }
.error { color: #ef4444; margin-top: 8px; }
</style>
