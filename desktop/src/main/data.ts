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
        return decrypt(val, this.secret)
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
    workspaces: Workspace[]
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

export type FeatureType = 'issue' | 'pull_request'
export type FeatureState = 'open' | 'closed'

export interface Feature {
    id: number
    workspace: string
    name: string
    description: string
    type: FeatureType
    github_number: number | null
    github_id: number | null
    html_url: string
    state: FeatureState
    task_count: number
    created_at: string
    updated_at: string
}

export type TaskStatus = 'todo' | 'in_progress' | 'done'
export type TaskPriority = 'low' | 'medium' | 'high'

export interface Task {
    id: string
    feature: string
    title: string
    description: string
    status: TaskStatus
    priority: TaskPriority
    assigned_to: User | null
    completed_by_commit: string
    checkbox_index: number | null
    created_at: string
    updated_at: string
}
