export interface Task {
    id: string
    name: string
    description: string
    types: string[]
    status: string
    priority: string
}

export interface Feature {
    id: string
    name: string
    description: string
    deadline: string
    members: string[]
    tasks: Task[]
    github_number: number | null
    html_url: string
}

export type PanelMode = 'idle' | 'viewing' | 'viewingFeature' | 'adding' | 'addingFeature'

export function priorityColor(priority: string): string {
    switch (priority) {
        case 'high':
            return '#d9534f'
        case 'medium':
            return '#f0ad4e'
        case 'low':
            return '#5cb85c'
        default:
            return '#999'
    }
}

export function statusColor(status: string): string {
    switch (status) {
        case 'todo':
            return '#6c757d'
        case 'in progress':
            return '#0d6efd'
        case 'review':
            return '#6f42c1'
        case 'blocked':
            return '#d9534f'
        case 'done':
            return '#5cb85c'
        default:
            return '#999'
    }
}

export function featurePriority(feature: Feature): string {
    const priorityRank: Record<string, number> = { high: 3, medium: 2, low: 1 }
    let highest = 0
    for (const task of feature.tasks) {
        const rank = priorityRank[task.priority] ?? 0
        if (rank > highest) highest = rank
    }
    if (highest === 3) return 'high'
    if (highest === 2) return 'medium'
    if (highest === 1) return 'low'
    return 'none'
}

export function featureProgress(feature: Feature): { done: number; total: number } {
    const total = feature.tasks.length
    const done = feature.tasks.filter((t) => t.status === 'review' || t.status === 'done').length
    return { done, total }
}
