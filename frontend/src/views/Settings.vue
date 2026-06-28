<template>
  <div class="settings">
    <h1>Configurar LLM</h1>
    <form @submit.prevent="save">
      <label>Provedor
        <select v-model="form.provider">
          <option value="groq">Groq (free tier)</option>
          <option value="openai">OpenAI</option>
          <option value="anthropic">Anthropic</option>
          <option value="deepseek">DeepSeek</option>
          <option value="google">Google</option>
        </select>
      </label>
      <label>Modelo
        <input v-model="form.model" placeholder="llama3-8b-8192" required />
      </label>
      <label>Chave de API
        <input
          v-model="form.api_key"
          type="password"
          :placeholder="keyHint || 'Sua chave de API'"
          required
        />
      </label>
      <button type="button" @click="testConn" :disabled="testing">
        {{ testing ? "Testando..." : "Testar conexão" }}
      </button>
      <p v-if="testResult" :class="testResult.ok ? 'ok' : 'error'">
        {{ testResult.ok ? "Conexão OK — modelo respondeu" : testResult.error }}
      </p>
      <button type="submit" :disabled="!testResult?.ok">Salvar</button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { api } from "../api.js"

const router = useRouter()
const form = ref({ provider: "groq", model: "llama3-8b-8192", api_key: "" })
const keyHint = ref("")
const testing = ref(false)
const testResult = ref(null)

onMounted(async () => {
  try {
    const config = await api.getConfig()
    form.value.provider = config.provider
    form.value.model = config.model
    keyHint.value = config.api_key_hint
  } catch {}
})

async function testConn() {
  testing.value = true
  testResult.value = null
  try {
    testResult.value = await api.testConfig(form.value)
  } catch (e) {
    testResult.value = { ok: false, error: String(e) }
  } finally {
    testing.value = false
  }
}

function save() {
  localStorage.setItem("llm_provider", form.value.provider)
  localStorage.setItem("llm_model", form.value.model)
  localStorage.setItem("llm_configured", "true")
  router.push("/")
}
</script>

<style scoped>
.settings { max-width: 480px; margin: 60px auto; padding: 24px; font-family: sans-serif; }
form { display: flex; flex-direction: column; gap: 16px; }
label { display: flex; flex-direction: column; gap: 4px; font-size: 14px; font-weight: 500; }
.ok { color: #22c55e; }
.error { color: #ef4444; }
input, select { width: 100%; padding: 8px; margin-top: 4px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
button { padding: 10px; cursor: pointer; border-radius: 4px; border: 1px solid #ccc; }
button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
