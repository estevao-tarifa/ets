<template>
  <aside class="sidebar">
    <button class="close" @click="$emit('close')">✕</button>
    <h2>{{ node.nome }}</h2>
    <p class="nivel">{{ node.nivel }}</p>
    <div class="dominio">
      <span>Domínio: {{ dominioLabel }}</span>
      <div class="bar"><div class="fill" :style="{ width: barWidth, background: barColor }" /></div>
    </div>
    <p v-if="node.descricao" class="desc">{{ node.descricao }}</p>
    <div class="actions">
      <router-link :to="`/nodes/${node.id}`"><button>Ver detalhes</button></router-link>
    </div>
  </aside>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({ node: Object })
defineEmits(["close"])

const COLORS = { azul: "#5b9bd5", verde: "#70ad47", amarelo: "#ffc000", vermelho: "#ff0000" }
const dominioLabel = computed(() =>
  props.node.dominio_score != null ? Math.round(props.node.dominio_score * 100) + "%" : "Não estudado")
const barWidth = computed(() =>
  (props.node.dominio_score != null ? props.node.dominio_score * 100 : 0) + "%")
const barColor = computed(() => COLORS[props.node.color] || COLORS.azul)
</script>

<style scoped>
.sidebar { position: fixed; right: 0; top: 0; height: 100vh; width: 280px; background: white; box-shadow: -2px 0 8px rgba(0,0,0,.1); padding: 24px; overflow-y: auto; z-index: 100; }
.close { position: absolute; top: 12px; right: 12px; background: none; border: none; font-size: 18px; cursor: pointer; }
.nivel { color: #888; font-size: 13px; text-transform: capitalize; }
.dominio { margin: 16px 0; }
.bar { height: 8px; background: #eee; border-radius: 4px; margin-top: 6px; }
.fill { height: 100%; border-radius: 4px; transition: width .3s; }
.desc { font-size: 14px; color: #444; }
.actions { margin-top: 24px; display: flex; flex-direction: column; gap: 8px; }
button { width: 100%; padding: 10px; cursor: pointer; }
</style>
