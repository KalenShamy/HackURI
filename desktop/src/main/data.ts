import { app } from 'electron'
import { join } from 'path'
import { writeFileSync, readFileSync } from 'fs'
import { createCipheriv, createDecipheriv, randomBytes, createHash } from 'crypto'

function deriveKey(secret: string): Buffer {
    return createHash('sha256').update(secret).digest()
}

function encrypt(text: string, secret: string): string {
    const key = deriveKey(secret)
    const iv = randomBytes(12)
    const cipher = createCipheriv('aes-256-gcm', key, iv)
    const encrypted = Buffer.concat([cipher.update(text, 'utf8'), cipher.final()])
    const tag = cipher.getAuthTag()
    return [iv.toString('hex'), tag.toString('hex'), encrypted.toString('hex')].join(':')
}

function decrypt(payload: string, secret: string): string {
    const [ivHex, tagHex, encHex] = payload.split(':')
    const key = deriveKey(secret)
    const decipher = createDecipheriv('aes-256-gcm', key, Buffer.from(ivHex, 'hex'))
    decipher.setAuthTag(Buffer.from(tagHex, 'hex'))
    return decipher.update(Buffer.from(encHex, 'hex')) + decipher.final('utf8')
}

export class Store {
    path: string
    data: Data
    private secret: string

    constructor(opts: Options) {
        const userDataPath = app.getPath('userData')
        this.path = join(userDataPath, opts.configName + '.json')
        this.secret = process.env.DATA_SECRET_KEY || ''
        this.data = parseDataFile(this.path, opts.defaults)
    }

    get<K extends keyof Data>(key: K): Data[K] {
        return this.data[key]
    }

    set<K extends keyof Data>(key: K, val: Data[K]): void {
        this.data[key] = val
        writeFileSync(this.path, JSON.stringify(this.data))
    }

    setEncrypted(key: 'token' | 'github_token', val: string): void {
        this.data[key] = encrypt(val, this.secret)
        writeFileSync(this.path, JSON.stringify(this.data))
    }

    getDecrypted(key: 'token' | 'github_token'): string | null {
        const val = this.data[key]
        if (!val) return null
        try {
            return decrypt(val, this.secret)
        } catch {
            // Stored value was encrypted with a different key (e.g. DATA_SECRET_KEY changed).
            // Clear the stale entry so the user is prompted to re-authenticate.
            this.set(key, null)
            return null
        }
    }

    private get baseUrl(): string {
        return process.env.VITE_API_BASE_URL || 'http://localhost:8000'
    }

    reset(): void {
        this.data = { ...emptyData }
        writeFileSync(this.path, JSON.stringify(this.data))
    }

    private async apiFetch<T>(path: string): Promise<T> {
        const token = this.getDecrypted('token')
        const res = await fetch(`${this.baseUrl}/api${path}`, {
            headers: { Authorization: `Token ${token}` }
        })
        if (res.status === 401) {
            this.reset()
            throw new Error('UNAUTHORIZED')
        }
        if (!res.ok) throw new Error(`API ${path} failed: ${res.status}`)
        return res.json() as Promise<T>
    }

    async fetchWorkspaces(): Promise<Workspace[]> {
        return this.apiFetch<Workspace[]>('/workspaces/')
    }

    async fetchWorkspace(id: string): Promise<Workspace> {
        return this.apiFetch<Workspace>(`/workspaces/${id}/`)
    }

    async fetchFeatures(workspaceId: string): Promise<Feature[]> {
        return this.apiFetch<Feature[]>(`/features/?workspace=${workspaceId}`)
    }

    async fetchTasks(params: { workspace?: string; feature?: string }): Promise<Task[]> {
        const entries = Object.entries(params).filter(
            (e): e is [string, string] => e[1] !== undefined
        )
        const qs = new URLSearchParams(entries)
        return this.apiFetch<Task[]>(`/tasks/?${qs}`)
    }

    async createTask(payload: {
        feature: string
        title: string
        description: string
        status: string
        priority: string
    }): Promise<Task> {
        const token = this.getDecrypted('token')
        const res = await fetch(`${this.baseUrl}/api/tasks/`, {
            method: 'POST',
            headers: {
                Authorization: `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        if (!res.ok) throw new Error(`API /tasks/ failed: ${res.status}`)
        return res.json() as Promise<Task>
    }

    async createFeature(payload: {
        workspace: string
        name: string
        description: string
    }): Promise<Feature> {
        const token = this.getDecrypted('token')
        const res = await fetch(`${this.baseUrl}/api/features/`, {
            method: 'POST',
            headers: {
                Authorization: `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        if (!res.ok) throw new Error(`API /features/ failed: ${res.status}`)
        return res.json() as Promise<Feature>
    }

    async fetchGitHubRepos(): Promise<GitHubRepo[]> {
        const token = this.getDecrypted('github_token')
        const res = await fetch('https://api.github.com/user/repos?sort=updated&per_page=100', {
            headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json' }
        })
        if (!res.ok) throw new Error(`GitHub repos fetch failed: ${res.status}`)
        return res.json() as Promise<GitHubRepo[]>
    }

    async createWorkspace(data: {
        name: string
        github_repo_url: string
        github_repo_owner: string
        github_repo_name: string
    }): Promise<Workspace> {
        const token = this.getDecrypted('token')
        const githubToken = this.getDecrypted('github_token')
        const res = await fetch(`${this.baseUrl}/api/workspaces/`, {
            method: 'POST',
            headers: {
                Authorization: `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ...data, github_token: githubToken })
        })
        if (!res.ok) throw new Error(`Create workspace failed: ${res.status}`)
        return res.json() as Promise<Workspace>
    }
}

function parseDataFile(filePath: string, defaults: Data): Data {
    // We'll try/catch it in case the file doesn't exist yet, which will be the case on the first application run.
    // `fs.readFileSync` will return a JSON string which we then parse into a Javascript object
    try {
        return JSON.parse(readFileSync(filePath, 'utf-8'))
    } catch (error) {
        // if there was some kind of error, return the passed in defaults instead.
        return defaults
    }
}

export const emptyData: Data = {
    init: false,
    user: null,
    token: null,
    github_token: null,
    workspaces: []
}

export interface Options {
    configName: string
    defaults: Data
}

export interface Data {
    init: boolean
    user: User | null
    token: string | null
    github_token: string | null
    workspaces: string[]
}

export interface User {
    id: number
    username: string
    email: string
}

export interface Workspace {
    id: string
    name: string
    github_repo_url: string
    github_repo_owner: string
    github_repo_name: string
    created_by: User
    members: User[]
    task_count: number
    created_at: string
    updated_at: string
}

export interface Feature {
    id: string
    workspace: string
    name: string
    description: string
    type: 'issue' | 'pull_request'
    github_number: number | null
    github_id: number | null
    html_url: string
    state: 'open' | 'closed'
    task_count: number
    created_at: string
    updated_at: string
}

export interface GitHubRepo {
    id: number
    name: string
    full_name: string
    html_url: string
    owner: { login: string }
    private: boolean
    description: string | null
}

export interface Task {
    id: string
    feature: string
    title: string
    description: string
    status: 'todo' | 'in_progress' | 'done'
    priority: 'low' | 'medium' | 'high'
    assigned_to: User | null
    completed_by_commit: string
    checkbox_index: number | null
    created_at: string
    updated_at: string
}
