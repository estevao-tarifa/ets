<template>
  <div class="chips">
    <button
      v-for="chip in chips"
      :key="String(chip.value)"
      :class="['chip', { active: active === chip.value }]"
      @click="select(chip.value)"
    >{{ chip.label }}</button>
  </div>
</template>

<script setup>
import { ref } from "vue"

const emit = defineEmits(["filter-change"])
const chips = [
  { label: "Todos", value: null },
  { label: "Críticos", value: "vermelho" },
  { label: "Não Estudados", value: "azul" },
  { label: "Dominados", value: "verde" },
]
const active = ref(null)

function select(value) {
  active.value = value
  emit("filter-change", value)
}
</script>

<style scoped>
.chips { display: flex; gap: 8px; padding: 8px 16px; background: #f5f5f5; flex-wrap: wrap; }
.chip { padding: 6px 14px; border-radius: 16px; border: 1px solid #ccc; cursor: pointer; background: white; font-size: 13px; }
.chip.active { background: #5b9bd5; color: white; border-color: #5b9bd5; }
</style>
