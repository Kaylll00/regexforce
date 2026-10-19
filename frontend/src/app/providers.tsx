"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import Link from "next/link";
import { apiPost } from "@/lib/api";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient());
  const [projects, setProjects] = useState<Array<{ id: number; name: string }>>([]);
  const [projectId, setProjectId] = useState("");
  useEffect(() => { void fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/projects`).then((response) => response.json() as Promise<Array<{ id: number; name: string }>>).then(setProjects).catch(() => undefined); }, []);
  async function createProject() {
    const name = window.prompt("Project name", "Untitled project");
    if (!name) return;
    const project = await apiPost<{ id: number; name: string }>("/api/projects", { name });
    setProjects((current) => [...current, project]); setProjectId(String(project.id));
  }
  return (
    <QueryClientProvider client={queryClient}>
      <header className="border-b border-slate-800 bg-slate-950">
        <nav className="mx-auto flex max-w-7xl flex-wrap gap-4 px-6 py-4 text-sm">
          {[
            ["Home", "/"], ["Studio", "/studio"], ["Lab", "/lab"], ["Grammar", "/grammar"],
            ["Analyzer", "/analyzer"], ["Proofs", "/proofs"], ["Help", "/help"],
          ].map(([label, href]) => <Link className="rounded text-slate-300 outline-none hover:text-cyan-200 focus:ring-2 focus:ring-cyan-300" href={href} key={href}>{label}</Link>)}
          <select aria-label="Project" className="rounded bg-slate-800 px-2" value={projectId} onChange={(event) => { setProjectId(event.target.value); sessionStorage.setItem("regexforge-project-id", event.target.value); }}><option value="">Project</option>{projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select>
          <button className="rounded bg-slate-700 px-2" onClick={() => void createProject()}>New project</button>
          <button className="rounded bg-slate-700 px-2" onClick={() => { const project = projects.find((item) => String(item.id) === projectId); const name = window.prompt("New project name", project?.name); if (project && name) void apiPost(`/api/projects/${project.id}`, { name }).then(() => setProjects((current) => current.map((item) => item.id === project.id ? { ...item, name } : item))); }}>Rename</button>
          <button className="rounded bg-red-900 px-2" onClick={() => { if (projectId && window.confirm("Delete selected project?")) void fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/projects/${projectId}`, { method: "DELETE" }).then(() => setProjects((current) => current.filter((item) => String(item.id) !== projectId))); }}>Delete</button>
        </nav>
      </header>
      {children}
    </QueryClientProvider>
  );
}
