<template>
  <div class="exam">
    <router-link to="/">← Painel</router-link>
    <h1>Diagnóstico de Prova</h1>

    <div class="config">
      <label>Dias até a prova:
        <input v-model.number="days" type="number" min="1" max="365" style="width:80px;padding:6px" />
      </label>
      <button @click="runDiag" :disabled="loading">{{ loading ? "Analisando..." : "Analisar" }}</button>
    </div>

    <div v-if="diagnostic.length" class="results">
      <h2>Ranking de Risco</h2>
      <div v-for="(item, i) in diagnostic" :key="item.node_id" class="risk-item">
        <span class="rank">#{{ i + 1 }}</span>
        <span class="nome">{{ item.nome }}</span>
        <div class="risk-bar">
          <div class="risk-fill" :style="{ width: item.risco_score * 100 + '%' }" />
        </div>
        <span class="pct">{{ Math.round(item.risco_score * 100) }}% risco</span>
      </div>

      <button @click="genPlan" :disabled="generating" style="margin-top:24px">
        {{ generating ? "Gerando..." : "Gerar Plano de Revisão" }}
      </button>
    </div>

    <pre v-if="plan" class="plan">{{ plan }}</pre>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRoute } from "vue-router"
import { api } from "../api.js"

const route = useRoute()
const materiaId = Number(route.params.materiaId)
const days = ref(7)
const loading = ref(false)
const generating = ref(false)
const diagnostic = ref([])
const plan = ref("")

async function runDiag() {
  loading.value = true
  try { diagnostic.value = await api.getDiagnostic(materiaId) }
  finally { loading.value = false }
}

async function genPlan() {
  generating.value = true
  try { const r = await api.getRevisionPlan(materiaId, days.value); plan.value = r.plan }
  finally { generating.value = false }
}
</script>

<style scoped>
.exam { max-width: 700px; margin: 40px auto; padding: 24px; font-family: sans-serif; }
.config { display: flex; gap: 16px; align-items: center; margin: 16px 0 24px; }
.risk-item { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid #eee; }
.rank { width: 32px; font-weight: bold; color: #888; }
.nome { flex: 1; }
.risk-bar { width: 120px; height: 8px; background: #eee; border-radius: 4px; }
.risk-fill { height: 100%; background: #ef4444; border-radius: 4px; }
.pct { width: 80px; text-align: right; font-size: 13px; color: #888; }
.plan { background: #f5f5f5; padding: 16px; border-radius: 8px; white-space: pre-wrap; margin-top: 24px; font-size: 14px; }
button { padding: 8px 16px; cursor: pointer; border: 1px solid #ccc; border-radius: 4px; }
</style>
