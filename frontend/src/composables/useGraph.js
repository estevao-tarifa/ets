import { Network } from "vis-network"

// ponytail: module-level map, not reactive — vis-network owns its state
const networks = new Map()

const COLORS = {
  azul: "#5b9bd5",
  verde: "#70ad47",
  amarelo: "#ffc000",
  vermelho: "#ff0000",
}

function toVisNodes(nodes) {
  return nodes.map(n => ({
    id: n.id,
    label: n.nome,
    color: COLORS[n.color] || COLORS.azul,
    title: `${n.nome}\nDomínio: ${n.dominio_score != null ? Math.round(n.dominio_score * 100) + "%" : "Não estudado"}`,
  }))
}

function toVisEdges(edges) {
  return edges.map(e => ({ from: e.from_node_id, to: e.to_node_id, arrows: "to" }))
}

const BASE_OPTIONS = {
  layout: { hierarchical: { direction: "UD", sortMethod: "directed" } },
  physics: { enabled: false },
  interaction: { hover: true },
}

export function useGraph(containerId) {
  function init(container, graphData) {
    const net = new Network(
      container,
      { nodes: toVisNodes(graphData.nodes), edges: toVisEdges(graphData.edges) },
      { ...BASE_OPTIONS }
    )
    networks.set(containerId, net)
    return net
  }

  function getNet() { return networks.get(containerId) }

  function setMode(mode) {
    const net = getNet()
    if (!net) return
    if (mode === "exploracao") net.setOptions({ physics: { enabled: true } })
    else net.setOptions({ physics: { enabled: false } })
  }

  function expandNode(nodeId, childNodes, childEdges) {
    const net = getNet()
    if (!net) return
    const existing = new Set(net.body.data.nodes.getIds())
    const newNodes = toVisNodes(childNodes.filter(n => !existing.has(n.id)))
    const newEdges = toVisEdges(childEdges)
    net.body.data.nodes.add(newNodes)
    net.body.data.edges.add(newEdges)
  }

  function highlightDependencies(nodeId) {
    const net = getNet()
    if (!net) return
    const connected = net.getConnectedNodes(nodeId)
    net.selectNodes([nodeId, ...connected])
  }

  function filterByColor(color) {
    const net = getNet()
    if (!net) return
    if (!color) { net.selectNodes([]); return }
    const matching = net.body.data.nodes.get().filter(n => n.color === COLORS[color]).map(n => n.id)
    net.selectNodes(matching)
  }

  function destroy() {
    const net = networks.get(containerId)
    if (net) { net.destroy(); networks.delete(containerId) }
  }

  return { init, setMode, expandNode, highlightDependencies, filterByColor, destroy }
}
