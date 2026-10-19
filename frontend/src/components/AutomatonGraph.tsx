"use client";

import type { Automaton } from "@/lib/types";
import { layoutAutomaton } from "@/lib/layout";
import { Background, ReactFlow, type Connection, type NodeChange, type OnNodesChange } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

type Props = {
  automaton: Automaton;
  activeStates?: string[];
  activeEdges?: string[];
  height?: number;
  editable?: boolean;
  onSelectState?: (state: string) => void;
  onMoveState?: (state: string, x: number, y: number) => void;
  onConnect?: (connection: Connection) => void;
};

export function AutomatonGraph({ automaton, activeStates = [], height = 260, editable = false, onSelectState, onMoveState, onConnect }: Props) {
  const graph = layoutAutomaton(automaton);
  const nodes = graph.nodes.map((node) => ({
    id: node.id,
    position: { x: node.x, y: node.y },
    data: { label: node.id },
    style: {
      border: `2px solid ${activeStates.includes(node.id) ? "#67e8f9" : "#94a3b8"}`,
      borderRadius: "9999px",
      background: activeStates.includes(node.id) ? "#155e75" : "#1e293b",
      color: "#e2e8f0",
      width: 48,
      height: 48,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    },
  }));
  const edges = graph.edges.map((edge) => ({ id: edge.id, source: edge.source, target: edge.target, label: edge.label, animated: activeStates.length > 0 }));
  const handleNodesChange: OnNodesChange = (changes: NodeChange[]) => {
    for (const change of changes) {
      if (change.type === "position" && change.position && onMoveState) onMoveState(change.id, change.position.x, change.position.y);
    }
  };
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-950" style={{ height }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        nodesDraggable={editable}
        nodesConnectable={editable}
        elementsSelectable={editable}
        onNodeClick={(_, node) => onSelectState?.(node.id)}
        onNodesChange={editable ? handleNodesChange : undefined}
        onConnect={editable ? onConnect : undefined}
      >
        <Background color="#334155" />
      </ReactFlow>
    </div>
  );
}
