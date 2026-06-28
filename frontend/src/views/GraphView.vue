<template>
  <div class="graph-page">
    <nav class="topbar">
      <router-link to="/">← Painel</router-link>
      <FilterChips @filter-change="onFilter" />
    </nav>
    <div ref="graphContainer" class="graph-container" />
    <NodeSidebar v-if="selectedNode" :node="selectedNode" @close="selectedNode = null" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue"
import { useRoute } from "vue-router"
import { api } from "../api.js"
import { useGraph } from "../composables/useGraph.js"
import FilterChips from "../components/FilterChips.vue"
import NodeSidebar from "../components/NodeSidebar.vue"

const route = useRoute()
const materiaId = Number(route.params.materiaId)
const graphContainer = ref(null)
const selectedNode = ref(null)
const { init, expandNode, filterByColor, destroy } = useGraph(`graph-${materiaId}`)

onMounted(async () => {
  const data = await api.getGraph(materiaId)
  const net = init(graphContainer.value, data)

  net.on("click", async ({ nodes }) => {
    if (!nodes.length) { selectedNode.value = null; return }
    selectedNode.value = await api.getNode(nodes[0])
  })

  net.on("doubleClick", async ({ nodes }) => {
    if (!nodes.length) return
    const children = await api.getGraph(materiaId)
    const childNodes = children.nodes.filter(n =>
      children.edges.some(e => e.from_node_id === nodes[0] && e.to_node_id === n.id)
    )
    const childEdges = children.edges.filter(e => e.from_node_id === nodes[0])
    expandNode(nodes[0], childNodes, childEdges)
  })
})

onUnmounted(() => destroy())
function onFilter(color) { filterByColor(color) }
</script>

<style scoped>
.graph-page { display: flex; flex-direction: column; height: 100vh; }
.topbar { display: flex; align-items: center; gap: 16px; padding: 8px 16px; background: white; border-bottom: 1px solid #eee; }
.graph-container { flex: 1; }
</style>
