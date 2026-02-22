<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Task, Feature, PanelMode } from './types'
import TitleBar from './TitleBar.vue'
import SettingsOverlay from './SettingsOverlay.vue'
import FeatureTaskList from './FeatureTaskList.vue'
import FeatureDetail from './FeatureDetail.vue'
import TaskDetail from './TaskDetail.vue'
import AddTaskForm from './AddTaskForm.vue'
import AddFeatureForm from './AddFeatureForm.vue'
import TeamPanel from './TeamPanel.vue'
import WorkspaceInit from './WorkspaceInit.vue'

// --- Data ---
const teamName = ref('')
const showSettings = ref(false)
const showWorkspaceSwitcher = ref(false)
const showNewWorkspaceForm = ref(false)
const switcherWorkspaces = ref<{ id: string; name: string; members: { username: string }[] }[]>([])
const switcherLoading = ref(false)
const activeWorkspaceId = ref<string | null>(null)
const loading = ref(false)
const loadError = ref<string | null>(null)
const hasNoWorkspaces = ref(false)

// --- Team members ---
const teamMembers = ref<string[]>([])

function addTeamMember(name: string): void {
    const trimmed = name.trim()
    if (trimmed && !teamMembers.value.includes(trimmed)) {
        teamMembers.value.push(trimmed)
    }
}

// --- Features ---
const features = ref<Feature[]>([])

// --- Load from API ---
async function loadWorkspace(workspace: {
    id: string
    name: string
    members: { username: string }[]
}): Promise<void> {
    activeWorkspaceId.value = workspace.id
    teamName.value = workspace.name
    teamMembers.value = workspace.members.map((m) => m.username)

    const [apiFeatures, apiTasks] = await Promise.all([
        window.electron.ipcRenderer.invoke('fetchFeatures', workspace.id),
        window.electron.ipcRenderer.invoke('fetchTasks', { workspace: workspace.id })
    ])

    features.value = apiFeatures.map((f) => ({
        id: f.id,
        name: f.name,
        description: f.description,
        deadline: '',
        members: [],
        github_number: f.github_number ?? null,
        html_url: f.html_url ?? '',
        tasks: apiTasks
            .filter((t) => t.feature === f.id)
            .map((t) => ({
                id: t.id,
                name: t.title,
                description: t.description,
                types: [],
                status: t.status === 'in_progress' ? 'in progress' : t.status,
                priority: t.priority
            }))
    }))
}

onMounted(async () => {
    loading.value = true
    loadError.value = null
    try {
        const workspaces = await window.electron.ipcRenderer.invoke('fetch-workspaces')
        if (!workspaces.length) {
            hasNoWorkspaces.value = true
            return
        }
        await loadWorkspace(workspaces[0])
    } catch (e) {
        loadError.value = e instanceof Error ? e.message : 'Failed to load workspace data'
    } finally {
        loading.value = false
    }
})

async function openWorkspaceSwitcher(): Promise<void> {
    showWorkspaceSwitcher.value = true
    switcherLoading.value = true
    try {
        switcherWorkspaces.value = await window.electron.ipcRenderer.invoke('fetch-workspaces')
    } finally {
        switcherLoading.value = false
    }
}

function openNewWorkspaceForm(): void {
    showWorkspaceSwitcher.value = false
    showNewWorkspaceForm.value = true
}

async function switchToWorkspace(workspace: {
    id: string
    name: string
    members: { username: string }[]
}): Promise<void> {
    showWorkspaceSwitcher.value = false
    loading.value = true
    loadError.value = null
    try {
        await loadWorkspace(workspace)
        hasNoWorkspaces.value = false
    } catch (e) {
        loadError.value = e instanceof Error ? e.message : 'Failed to load workspace data'
    } finally {
        loading.value = false
    }
}

async function onWorkspaceCreated(workspace: {
    id: string
    name: string
    members: { username: string }[]
}): Promise<void> {
    loading.value = true
    loadError.value = null
    try {
        await loadWorkspace(workspace)
        hasNoWorkspaces.value = false
    } catch (e) {
        loadError.value = e instanceof Error ? e.message : 'Failed to load workspace data'
    } finally {
        loading.value = false
    }
}

// --- Panel mode ---
const panelMode = ref<PanelMode>('idle')

// --- Selection state ---
const selectedFeatureId = ref<string | null>(null)
const selectedTaskId = ref<string | null>(null)

const selectedTask = computed<Task | null>(() => {
    if (!selectedFeatureId.value || !selectedTaskId.value) return null
    const feature = features.value.find((f) => f.id === selectedFeatureId.value)
    if (!feature) return null
    return feature.tasks.find((t) => t.id === selectedTaskId.value) ?? null
})

const selectedFeature = computed<Feature | null>(() => {
    if (!selectedFeatureId.value) return null
    return features.value.find((f) => f.id === selectedFeatureId.value) ?? null
})

const selectedFeatureName = computed<string>(() => {
    if (!selectedFeatureId.value) return ''
    return features.value.find((f) => f.id === selectedFeatureId.value)?.name ?? ''
})

// --- Selection handlers ---
function selectFeature(featureId: string): void {
    if (selectedFeatureId.value === featureId && !selectedTaskId.value) {
        selectedFeatureId.value = null
        selectedTaskId.value = null
        if (panelMode.value !== 'adding' && panelMode.value !== 'addingFeature')
            panelMode.value = 'idle'
    } else {
        selectedFeatureId.value = featureId
        selectedTaskId.value = null
        if (panelMode.value !== 'adding' && panelMode.value !== 'addingFeature')
            panelMode.value = 'viewingFeature'
    }
}

function selectTask(featureId: string, taskId: string): void {
    selectedFeatureId.value = featureId
    selectedTaskId.value = taskId
    panelMode.value = 'viewing'
}

function clearSelection(): void {
    selectedFeatureId.value = null
    selectedTaskId.value = null
}

// --- Form triggers ---
function addtask(): void {
    clearSelection()
    panelMode.value = 'adding'
}

function addFeature(): void {
    clearSelection()
    panelMode.value = 'addingFeature'
}

// --- Create handlers ---
async function handleCreateTask(payload: {
    name: string
    description: string
    types: string[]
    status: string
    priority: string
    featureId: string
}): Promise<void> {
    const feature = features.value.find((f) => f.id === payload.featureId)
    if (!feature) return

    // Translate display status to API format before sending
    const apiStatus = payload.status === 'in progress' ? 'in_progress' : payload.status

    const apiTask = await window.electron.ipcRenderer.invoke('create-task', {
        feature: payload.featureId,
        title: payload.name,
        description: payload.description,
        status: apiStatus,
        priority: payload.priority
    })

    const task: Task = {
        id: apiTask.id,
        name: apiTask.title,
        description: apiTask.description,
        types: payload.types,
        status: apiTask.status === 'in_progress' ? 'in progress' : apiTask.status,
        priority: apiTask.priority
    }

    feature.tasks.push(task)
    selectedFeatureId.value = feature.id
    selectedTaskId.value = task.id
    panelMode.value = 'viewing'
}

async function handleCreateFeature(payload: {
    name: string
    description: string
    deadline: string
    members: string[]
}): Promise<void> {
    if (!activeWorkspaceId.value) return

    const apiFeature = await window.electron.ipcRenderer.invoke('create-feature', {
        workspace: activeWorkspaceId.value,
        name: payload.name,
        description: payload.description
    })

    const feature: Feature = {
        id: apiFeature.id,
        name: apiFeature.name,
        description: apiFeature.description,
        deadline: payload.deadline,
        members: payload.members,
        github_number: apiFeature.github_number ?? null,
        html_url: apiFeature.html_url ?? '',
        tasks: []
    }

    features.value.push(feature)

    for (const member of feature.members) {
        addTeamMember(member)
    }

    selectedFeatureId.value = feature.id
    selectedTaskId.value = null
    panelMode.value = 'viewingFeature'
}
</script>

<template>
    <main>
        <div class="whole-box">
            <TitleBar
                :team-name="teamName"
                @toggle-settings="showSettings = !showSettings"
                @switch-workspace="openWorkspaceSwitcher"
            />

            <SettingsOverlay
                :show="showSettings"
                :team-name="teamName"
                @close="showSettings = false"
                @update:team-name="teamName = $event"
            />

            <div
                v-if="showWorkspaceSwitcher"
                class="switcher-backdrop"
                @click.self="showWorkspaceSwitcher = false"
            >
                <div class="switcher-panel">
                    <div class="switcher-header">
                        <span>Switch Workspace</span>
                        <button class="switcher-close" @click="showWorkspaceSwitcher = false">
                            ✕
                        </button>
                    </div>
                    <div v-if="switcherLoading" class="switcher-loading">Loading…</div>
                    <ul v-else class="switcher-list">
                        <li
                            v-for="ws in switcherWorkspaces"
                            :key="ws.id"
                            class="switcher-item"
                            :class="{ active: ws.id === activeWorkspaceId }"
                            @click="switchToWorkspace(ws)"
                        >
                            {{ ws.name }}
                        </li>
                        <li class="switcher-item switcher-new" @click="openNewWorkspaceForm">
                            + New Workspace
                        </li>
                    </ul>
                </div>
            </div>

            <div
                v-if="showNewWorkspaceForm"
                class="switcher-backdrop"
                @click.self="showNewWorkspaceForm = false"
            >
                <WorkspaceInit
                    :cancelable="true"
                    @workspace-created="(ws) => { showNewWorkspaceForm = false; onWorkspaceCreated(ws) }"
                    @cancel="showNewWorkspaceForm = false"
                />
            </div>

            <div v-if="loading" class="loading-overlay">Loading workspace…</div>
            <div v-else-if="loadError" class="error-overlay">{{ loadError }}</div>

            <WorkspaceInit v-else-if="hasNoWorkspaces" @workspace-created="onWorkspaceCreated" />

            <div v-else class="menu-layout">
                <!-- Left panel: feature/task list -->
                <div class="menu-box">
                    <FeatureTaskList
                        :features="features"
                        :selected-feature-id="selectedFeatureId"
                        :selected-task-id="selectedTaskId"
                        @select-feature="selectFeature"
                        @select-task="selectTask"
                        @add-feature="addFeature"
                        @add-task="addtask"
                    />
                </div>

                <!-- Middle panel: detail / add form -->
                <div class="menu-box">
                    <template v-if="panelMode === 'idle'">
                        <div class="idle-box">
                            <p>
                                Select a feature or task, or click <strong>Add Feature</strong> /
                                <strong>Add Task</strong> to create one.
                            </p>
                        </div>
                    </template>

                    <FeatureDetail
                        v-if="panelMode === 'viewingFeature' && selectedFeature"
                        :feature="selectedFeature"
                        @select-task="selectTask"
                    />

                    <TaskDetail
                        v-if="panelMode === 'viewing' && selectedTask"
                        :task="selectedTask"
                        :feature-name="selectedFeatureName"
                    />

                    <AddTaskForm
                        v-if="panelMode === 'adding'"
                        :features="features"
                        @create="handleCreateTask"
                    />

                    <AddFeatureForm
                        v-if="panelMode === 'addingFeature'"
                        @create="handleCreateFeature"
                    />
                </div>

                <!-- Right panel -->
                <div class="menu-box">
                    <TeamPanel :team-name="teamName" :team-members="teamMembers" />
                </div>
            </div>
        </div>
    </main>
</template>

<style scoped>
main {
    background: var(--background-color);
    color: black;
    font-family: 'Google Sans Flex';
}
.whole-box {
    background-color: #ffebba;
    padding: 20px;
    height: 100vh;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
    position: relative;
}
.menu-layout {
    width: calc(100%);
    flex: 1;
    min-height: 0;
    border-radius: 10px;
    align-items: center;
    display: flex;
}
.menu-box {
    height: 100%;
    min-height: 0;
    width: 33%;
    background-color: #e9c17d;
    border-radius: 40px;
    margin: 0.8%;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    color: black;
    font-family: 'Google Sans Flex';
}

.menu-box:nth-child(1),
.menu-box:nth-child(2) {
    scrollbar-width: none;
    -ms-overflow-style: none;
}

.menu-box:nth-child(1)::-webkit-scrollbar,
.menu-box:nth-child(2)::-webkit-scrollbar {
    display: none;
}

.idle-box {
    align-self: center;
    width: 90%;
    flex: 1;
    border-radius: 15px;
    background-color: #ffebba;
    margin-top: 15px;
    margin-bottom: 20px;
    padding: 15px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: #8a7540;
    font-size: 15px;
    text-align: center;
}

.loading-overlay,
.error-overlay {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    color: #8a7540;
}

.error-overlay {
    color: #d9534f;
}

.switcher-backdrop {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
    border-radius: inherit;
}

.switcher-panel {
    background: #ffebba;
    border-radius: 20px;
    padding: 20px;
    min-width: 260px;
    max-width: 360px;
    width: 100%;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
}

.switcher-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 14px;
    color: #5a4010;
}

.switcher-close {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 16px;
    color: #8a7540;
    line-height: 1;
    padding: 2px 6px;
    border-radius: 6px;
}

.switcher-close:hover {
    background: #f3bb5b;
}

.switcher-loading {
    text-align: center;
    color: #8a7540;
    padding: 12px 0;
}

.switcher-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.switcher-item {
    padding: 10px 14px;
    border-radius: 12px;
    cursor: pointer;
    background: #e9c17d;
    color: #3a2800;
    font-size: 15px;
    transition: background 0.15s;
}

.switcher-item:hover {
    background: #f3bb5b;
}

.switcher-item.active {
    background: #f3bb5b;
    font-weight: 600;
    cursor: default;
}

.switcher-new {
    border-top: 1px solid #e9c17d;
    margin-top: 4px;
    padding-top: 14px;
    color: #5a4010;
    font-weight: 600;
}
</style>
