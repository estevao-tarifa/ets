<template>
  <div class="study">
    <router-link to="/">← Painel</router-link>
    <h1>Sessão de Estudo</h1>
    <p class="counter">Eventos registrados: {{ events.length }}</p>

    <div class="btns">
      <button @click="record('acerto')" class="acerto">✓ Acerto</button>
      <button @click="record('erro')" class="erro">✗ Erro</button>
      <button @click="record('duvida')" class="duvida">? Dúvida</button>
    </div>

    <button @click="showClose = true" class="encerrar">Encerrar sessão</button>

    <div v-if="showClose" class="modal-overlay">
      <div class="modal">
        <h2>Encerrar sessão</h2>
        <p>Autoavaliação <em>(obrigatória)</em></p>
        <div class="scale">
          <button
            v-for="n in 5" :key="n"
            :class="{ active: avaliacao === n }"
            @click="avaliacao = n"
          >{{ n }}</button>
        </div>
        <textarea v-model="pendente" placeholder="O que ficou pendente? (opcional)" />
        <div class="modal-actions">
          <button @click="showClose = false">Cancelar</button>
          <button @click="finish" :disabled="!avaliacao" class="primary">Finalizar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useSession } from "../composables/useSession.js"

const route = useRoute()
const router = useRouter()
const { sessionId, events, addEvent, closeSession } = useSession()
sessionId.value = Number(route.params.sessionId)

const showClose = ref(false)
const avaliacao = ref(null)
const pendente = ref("")

async function record(tipo) {
  await addEvent(tipo)  // 1 click — satisfies ≤2 interactions requirement
}

async function finish() {
  if (!avaliacao.value) return
  await closeSession(avaliacao.value, pendente.value || null)
  router.push("/")
}
</script>

<style scoped>
.study { max-width: 600px; margin: 40px auto; padding: 24px; font-family: sans-serif; }
.counter { color: #888; margin: 8px 0 24px; }
.btns { display: flex; gap: 12px; margin-bottom: 32px; }
.acerto { background: #22c55e; color: white; padding: 16px 28px; border: none; border-radius: 8px; font-size: 18px; cursor: pointer; }
.erro { background: #ef4444; color: white; padding: 16px 28px; border: none; border-radius: 8px; font-size: 18px; cursor: pointer; }
.duvida { background: #f59e0b; color: white; padding: 16px 28px; border: none; border-radius: 8px; font-size: 18px; cursor: pointer; }
.encerrar { padding: 12px 24px; cursor: pointer; border: 1px solid #ccc; border-radius: 6px; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; }
.modal { background: white; border-radius: 12px; padding: 32px; min-width: 360px; }
.scale { display: flex; gap: 8px; margin: 16px 0; }
.scale button { width: 48px; height: 48px; border: 2px solid #ccc; border-radius: 8px; font-size: 18px; cursor: pointer; background: white; }
.scale button.active { border-color: #5b9bd5; background: #5b9bd5; color: white; }
textarea { width: 100%; height: 80px; padding: 8px; margin: 8px 0; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
.primary { background: #5b9bd5; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; }
.primary:disabled { opacity: .5; cursor: not-allowed; }
</style>
