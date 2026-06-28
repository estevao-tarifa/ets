<template>
  <div class="node-detail" v-if="node">
    <router-link to="/">← Painel</router-link>
    <h1>{{ node.nome }}</h1>
    <p class="nivel">{{ node.nivel }}</p>
    <p class="desc">{{ node.descricao || "Sem descrição" }}</p>
    <div class="dominio">
      <span>Domínio: {{ node.dominio_score != null ? Math.round(node.dominio_score * 100) + "%" : "Não estudado" }}</span>
      <div class="bar">
        <div class="fill" :style="{ width: (node.dominio_score || 0) * 100 + '%', background: COLORS[node.color] }" />
      </div>
    </div>
    <button @click="genFlashcard" :disabled="generating">
      {{ generating ? "Gerando..." : "Gerar Flashcard" }}
    </button>
    <p v-if="flashMsg" class="msg">{{ flashMsg }}</p>
  </div>
  <p v-else>Carregando...</p>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRoute } from "vue-router"
import { api } from "../api.js"

const COLORS = { azul: "#5b9bd5", verde: "#70ad47", amarelo: "#ffc000", vermelho: "#ff0000" }
const route = useRoute()
const node = ref(null)
const generating = ref(false)
const flashMsg = ref("")

onMounted(async () => { node.value = await api.getNode(Number(route.params.nodeId)) })

async function genFlashcard() {
  generating.value = true
  try {
    const r = await api.generateFlashcard(node.value.id)
    flashMsg.value = `Flashcard criado (id ${r.flashcard_id})`
  } catch (e) {
    flashMsg.value = "Erro: " + e
  } finally { generating.value = false }
}
</script>

<style scoped>
.node-detail { max-width: 600px; margin: 40px auto; padding: 24px; font-family: sans-serif; }
.nivel { color: #888; text-transform: capitalize; margin: 4px 0; }
.desc { margin: 16px 0; color: #444; }
.bar { height: 8px; background: #eee; border-radius: 4px; margin-top: 6px; }
.fill { height: 100%; border-radius: 4px; }
button { padding: 10px 20px; cursor: pointer; border: 1px solid #ccc; border-radius: 4px; margin-top: 16px; }
.msg { margin-top: 8px; color: #22c55e; }
</style>
