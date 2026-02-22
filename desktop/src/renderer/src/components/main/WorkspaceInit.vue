<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface GitHubRepo {
    id: number
    name: string
    full_name: string
    html_url: string
    owner: { login: string }
    private: boolean
    description: string | null
}

interface Workspace {
    id: string
    name: string
    github_repo_url: string
    github_repo_owner: string
    github_repo_name: string
    members: { username: string }[]
}

const props = defineProps<{ cancelable?: boolean }>()

const emit = defineEmits<{
    (e: 'workspace-created', workspace: Workspace): void
    (e: 'cancel'): void
}>()

const repos = ref<GitHubRepo[]>([])
const loadingRepos = ref(false)
const repoError = ref<string | null>(null)
const search = ref('')
const selectedRepo = ref<GitHubRepo | null>(null)
const workspaceName = ref('')
const creating = ref(false)
const createError = ref<string | null>(null)

const filteredRepos = computed(() => {
    const q = search.value.toLowerCase()
    return repos.value.filter(
        (r) => r.full_name.toLowerCase().includes(q) || (r.description ?? '').toLowerCase().includes(q)
    )
})

onMounted(async () => {
    loadingRepos.value = true
    repoError.value = null
    try {
        repos.value = await window.electron.ipcRenderer.invoke('fetch-github-repos')
    } catch (e) {
        repoError.value = e instanceof Error ? e.message : 'Failed to load repositories'
    } finally {
        loadingRepos.value = false
    }
})

function selectRepo(repo: GitHubRepo): void {
    selectedRepo.value = repo
    workspaceName.value = repo.name
    createError.value = null
}

async function initWorkspace(): Promise<void> {
    if (!selectedRepo.value || !workspaceName.value.trim()) return
    creating.value = true
    createError.value = null
    try {
        const workspace = await window.electron.ipcRenderer.invoke('create-workspace', {
            name: workspaceName.value.trim(),
            github_repo_url: selectedRepo.value.html_url,
            github_repo_owner: selectedRepo.value.owner.login,
            github_repo_name: selectedRepo.value.name
        })
        emit('workspace-created', workspace)
    } catch (e) {
        createError.value = e instanceof Error ? e.message : 'Failed to create workspace'
    } finally {
        creating.value = false
    }
}
</script>

<template>
    <div class="init-wrap">
        <div class="init-card">
            <div class="init-card-header">
                <button v-if="props.cancelable" class="back-button" @click="emit('cancel')">← Back</button>
                <div class="title-pill">Initialize a Workspace</div>
            </div>
            <p class="subtitle">Pick a GitHub repository to track with Hivemind.</p>

            <div v-if="loadingRepos" class="status-msg">Loading repositories…</div>
            <div v-else-if="repoError" class="status-msg error">{{ repoError }}</div>
            <template v-else>
                <input
                    v-model="search"
                    class="search-input"
                    placeholder="Search repositories…"
                    type="text"
                />
                <div class="repo-list">
                    <div v-if="filteredRepos.length === 0" class="empty-repos">No repositories found.</div>
                    <button
                        v-for="repo in filteredRepos"
                        :key="repo.id"
                        class="repo-row"
                        :class="{ selected: selectedRepo?.id === repo.id }"
                        @click="selectRepo(repo)"
                    >
                        <div class="repo-header">
                            <span class="repo-name">{{ repo.full_name }}</span>
                            <span class="repo-badge" :class="repo.private ? 'private' : 'public'">
                                {{ repo.private ? 'private' : 'public' }}
                            </span>
                        </div>
                        <div v-if="repo.description" class="repo-desc">{{ repo.description }}</div>
                    </button>
                </div>

                <template v-if="selectedRepo">
                    <div class="name-row">
                        <label class="name-label">Workspace name</label>
                        <input v-model="workspaceName" class="name-input" type="text" />
                    </div>
                    <div v-if="createError" class="status-msg error">{{ createError }}</div>
                    <div v-if="creating" class="status-msg">Reading repository and generating features…</div>
                    <button
                        class="cta-button"
                        :disabled="creating || !workspaceName.trim()"
                        @click="initWorkspace"
                    >
                        {{ creating ? 'Initializing…' : 'Initialize Workspace' }}
                    </button>
                </template>
            </template>
        </div>
    </div>
</template>

<style scoped>
.init-wrap {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
}

.init-card {
    width: 92%;
    max-width: 500px;
    background-color: #ffebba;
    border-radius: 28px;
    padding: 28px 28px 24px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    box-shadow: 0 4px 20px rgba(37, 33, 31, 0.12);
}

.init-card-header {
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.back-button {
    position: absolute;
    left: 0;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    color: #7a5c20;
    font-family: inherit;
    padding: 4px 8px;
    border-radius: 8px;
    transition: background-color 0.15s, color 0.15s;
}

.back-button:hover {
    background-color: #e9c17d;
    color: #4a3510;
}

.title-pill {
    background-color: #e9c17d;
    border-radius: 50px;
    padding: 8px 24px;
    font-size: 18px;
    font-weight: 700;
    color: #4a3510;
    text-align: center;
    align-self: center;
}

.subtitle {
    margin: 0;
    font-size: 13px;
    color: #7a5c20;
    text-align: center;
}

.status-msg {
    font-size: 13px;
    color: #7a5c20;
    text-align: center;
    padding: 8px 0;
}

.status-msg.error {
    color: #d9534f;
}

.search-input {
    width: 100%;
    box-sizing: border-box;
    padding: 9px 14px;
    border-radius: 50px;
    border: none;
    background-color: #e9c17d;
    font-size: 13px;
    color: #4a3510;
    font-family: inherit;
    outline: none;
}

.search-input::placeholder {
    color: #a07a3a;
}

.repo-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-height: 260px;
    overflow-y: auto;
    scrollbar-width: none;
}

.repo-list::-webkit-scrollbar {
    display: none;
}

.empty-repos {
    font-size: 13px;
    color: #a07a3a;
    text-align: center;
    padding: 16px 0;
}

.repo-row {
    background-color: #e9c17d;
    border: 2px solid transparent;
    border-radius: 14px;
    padding: 10px 14px;
    text-align: left;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    gap: 4px;
    transition: border-color 0.15s, background-color 0.15s;
    font-family: inherit;
}

.repo-row:hover {
    background-color: #ddb468;
}

.repo-row.selected {
    border-color: #4a3510;
    background-color: #ddb468;
}

.repo-header {
    display: flex;
    align-items: center;
    gap: 8px;
}

.repo-name {
    font-size: 13px;
    font-weight: 600;
    color: #4a3510;
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.repo-badge {
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 50px;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    flex-shrink: 0;
}

.repo-badge.public {
    background-color: #c5e8b0;
    color: #2a5a10;
}

.repo-badge.private {
    background-color: #f0d090;
    color: #7a4a00;
}

.repo-desc {
    font-size: 12px;
    color: #7a5c20;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.name-row {
    display: flex;
    align-items: center;
    gap: 10px;
}

.name-label {
    font-size: 13px;
    font-weight: 600;
    color: #4a3510;
    white-space: nowrap;
}

.name-input {
    flex: 1;
    padding: 8px 14px;
    border-radius: 50px;
    border: none;
    background-color: #e9c17d;
    font-size: 13px;
    color: #4a3510;
    font-family: inherit;
    outline: none;
}

.cta-button {
    background-color: #4a3510;
    color: #ffebba;
    border: none;
    border-radius: 50px;
    padding: 12px 28px;
    font-size: 14px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    align-self: center;
    transition: background-color 0.2s, transform 0.15s;
}

.cta-button:hover:not(:disabled) {
    background-color: #6b4e1a;
    transform: translateY(-1px);
}

.cta-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
</style>
