<script setup lang="ts">
import { ref, reactive, computed } from 'vue'

// --- Data ---
const teamName = ref('[Insert Team]')
const showSettings = ref(false)

interface Task {
    id: string
    name: string
    description: string
    types: string[]
    status: string
    priority: string
}

interface Feature {
    id: string
    name: string
    description: string
    deadline: string
    members: string[]
    tasks: Task[]
}

// --- Team members (independent source of truth) ---
const teamMembers = ref<string[]>([
    'Hai-bien Nguyen',
    'Hannah Ritchie',
    'Paul Fang Li',
    'Kaylen Shamey',
    'Joe Schmoe'
])

function addTeamMember(name: string): void {
    const trimmed = name.trim()
    if (trimmed && !teamMembers.value.includes(trimmed)) {
        teamMembers.value.push(trimmed)
    }
}

function removeTeamMember(name: string): void {
    const idx = teamMembers.value.indexOf(name)
    if (idx !== -1) teamMembers.value.splice(idx, 1)
}

function setTeamMembers(members: string[]): void {
    teamMembers.value = [...new Set(members.map((m) => m.trim()).filter(Boolean))]
}

// Future: call this with GitHub collaborators
// async function fetchTeamMembersFromGitHub(): Promise<void> {
//     const res = await api.get('/github/collaborators')
//     setTeamMembers(res.data.map((u: { login: string }) => u.login))
// }

const features = ref<Feature[]>([
    {
        id: 'f1',
        name: 'Feature #1',
        description: 'Core authentication and user management system.',
        deadline: '2026-03-15',
        members: ['Hai-bien Nguyen', 'Paul Fang Li'],
        tasks: [
            {
                id: 'f1t1',
                name: 'Task #1',
                description: 'Something small enough to escape casual notice.',
                types: ['bug'],
                status: 'todo',
                priority: 'low'
            },
            {
                id: 'f1t2',
                name: 'Task #2',
                description: 'Something small enough to escape casual notice.',
                types: ['enhancement'],
                status: 'in progress',
                priority: 'medium'
            },
            {
                id: 'f1t3',
                name: 'Task #3',
                description: 'Something small enough to escape casual notice.',
                types: ['documentation'],
                status: 'review',
                priority: 'high'
            }
        ]
    },
    {
        id: 'f2',
        name: 'Feature #2',
        description: 'Slack integration and webhook event handling.',
        deadline: '2026-04-01',
        members: ['Hannah Ritchie', 'Kaylen Shamey'],
        tasks: [
            {
                id: 'f2t1',
                name: 'Task #1',
                description: 'Something small enough to escape casual notice.',
                types: ['proposal'],
                status: 'blocked',
                priority: 'medium'
            },
            {
                id: 'f2t2',
                name: 'Task #2',
                description: 'Something small enough to escape casual notice.',
                types: ['bug', 'enhancement'],
                status: 'todo',
                priority: 'low'
            },
            {
                id: 'f2t3',
                name: 'Task #3',
                description: 'Something small enough to escape casual notice.',
                types: [],
                status: 'in progress',
                priority: 'high'
            }
        ]
    },
    {
        id: 'f3',
        name: 'Feature #3',
        description: 'Desktop UI polish and responsive layout improvements.',
        deadline: '2026-03-28',
        members: ['Hai-bien Nguyen', 'Joe Schmoe', 'Paul Fang Li'],
        tasks: [
            {
                id: 'f3t1',
                name: 'Task #1',
                description: 'Something small enough to escape casual notice.',
                types: ['documentation', 'proposal'],
                status: 'todo',
                priority: 'low'
            },
            {
                id: 'f3t2',
                name: 'Task #2',
                description: 'Something small enough to escape casual notice.',
                types: ['enhancement'],
                status: 'review',
                priority: 'medium'
            },
            {
                id: 'f3t3',
                name: 'Task #3',
                description: 'Something small enough to escape casual notice.',
                types: ['bug'],
                status: 'blocked',
                priority: 'high'
            }
        ]
    }
])

// Middle panel modes
type PanelMode = 'idle' | 'viewing' | 'viewingFeature' | 'adding' | 'addingFeature'
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

// Auto-incrementing ID counters
let nextFeatureNum = features.value.length + 1
function generateFeatureId(): string {
    return `f${nextFeatureNum++}`
}

function generateTaskId(featureId: string): string {
    const feature = features.value.find((f) => f.id === featureId)
    const num = feature ? feature.tasks.length + 1 : 1
    return `${featureId}t${num}`
}

// Compute overall feature priority from highest task priority
function featurePriority(feature: Feature): string {
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

// Compute feature progress as fraction of completed/review tasks
function featureProgress(feature: Feature): { done: number; total: number } {
    const total = feature.tasks.length
    const done = feature.tasks.filter((t) => t.status === 'review' || t.status === 'done').length
    return { done, total }
}

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

// --- Add task form ---
const typeOptions = ['bug', 'enhancement', 'proposal', 'documentation']
const statusOptions = ['todo', 'in progress', 'review', 'blocked']
const priorityOptions = ['low', 'medium', 'high']

const newTask = reactive({
    name: '',
    description: '',
    types: [] as string[],
    status: '',
    priority: '',
    featureId: ''
})

const showTypeDropdown = ref(false)

function toggleType(type: string): void {
    const idx = newTask.types.indexOf(type)
    if (idx === -1) {
        newTask.types.push(type)
    } else {
        newTask.types.splice(idx, 1)
    }
}

function addtask(): void {
    clearSelection()
    newTask.name = ''
    newTask.description = ''
    newTask.types = []
    newTask.status = ''
    newTask.priority = ''
    newTask.featureId = features.value.length ? features.value[0].id : ''
    showTypeDropdown.value = false
    panelMode.value = 'adding'
}

function createTask(): void {
    if (!newTask.name || !newTask.featureId || !newTask.status || !newTask.priority) return

    const feature = features.value.find((f) => f.id === newTask.featureId)
    if (!feature) return

    const task: Task = {
        id: generateTaskId(newTask.featureId),
        name: newTask.name,
        description: newTask.description,
        types: [...newTask.types],
        status: newTask.status,
        priority: newTask.priority
    }

    feature.tasks.push(task)
    console.log('Created task:', task, 'in feature:', feature.name)

    selectedFeatureId.value = feature.id
    selectedTaskId.value = task.id
    panelMode.value = 'viewing'

    newTask.name = ''
    newTask.description = ''
    newTask.types = []
    newTask.status = ''
    newTask.priority = ''
    newTask.featureId = ''
    showTypeDropdown.value = false
}

// --- Add feature form ---
const newFeature = reactive({
    name: '',
    description: '',
    deadline: '',
    members: [] as string[],
    newMember: ''
})

function addFeature(): void {
    clearSelection()
    newFeature.name = ''
    newFeature.description = ''
    newFeature.deadline = ''
    newFeature.members = []
    newFeature.newMember = ''
    panelMode.value = 'addingFeature'
}

function addMemberToNewFeature(): void {
    const name = newFeature.newMember.trim()
    if (name && !newFeature.members.includes(name)) {
        newFeature.members.push(name)
    }
    newFeature.newMember = ''
}

function removeMemberFromNewFeature(member: string): void {
    const idx = newFeature.members.indexOf(member)
    if (idx !== -1) newFeature.members.splice(idx, 1)
}

function createFeature(): void {
    if (!newFeature.name) return

    const feature: Feature = {
        id: generateFeatureId(),
        name: newFeature.name,
        description: newFeature.description,
        deadline: newFeature.deadline,
        members: [...newFeature.members],
        tasks: []
    }

    features.value.push(feature)
    console.log('Created feature:', feature)

    // Also add any new members to the team roster
    for (const member of feature.members) {
        addTeamMember(member)
    }

    selectedFeatureId.value = feature.id
    selectedTaskId.value = null
    panelMode.value = 'viewingFeature'

    newFeature.name = ''
    newFeature.description = ''
    newFeature.deadline = ''
    newFeature.members = []
    newFeature.newMember = ''
}

function priorityColor(priority: string): string {
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

function statusColor(status: string): string {
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

function toggleSettings(): void {
    showSettings.value = !showSettings.value
}
</script>

<template>
    <main>
        <div class="whole-box">
            <div id="menu-title">
                <img src="/LOGOCIRCLE.png" alt="Home Icon" class="menu-title-icon" />
                <span class="menu-title-content"> {{ teamName }}'s Current Workspace </span>
                <button class="menu-title-settings-button" @click="toggleSettings">
                    <img src="/settings.png" alt="Settings Icon" class="menu-title-settings-icon" />
                </button>
            </div>

            <!-- Settings overlay panel -->
            <div v-if="showSettings" class="settings-overlay" @click.self="showSettings = false">
                <div class="settings-panel">
                    <div class="settings-header">
                        <span class="settings-title">SETTINGS</span>
                        <button class="settings-close-btn" @click="showSettings = false">
                            <img src="/settings.png" alt="Settings" class="settings-header-icon" />
                        </button>
                    </div>
                    <div class="settings-body">
                        <div class="settings-section">
                            <label class="settings-label">Team Name</label>
                            <input
                                v-model="teamName"
                                class="settings-input"
                                type="text"
                                placeholder="Enter team name"
                            />
                        </div>
                        <div class="settings-section">
                            <label class="settings-label">Theme</label>
                            <div class="settings-placeholder">Default (Honey)</div>
                        </div>
                        <div class="settings-section">
                            <label class="settings-label">GitHub Integration</label>
                            <div class="settings-placeholder">Connected</div>
                        </div>
                        <div class="settings-section">
                            <label class="settings-label">Slack Integration</label>
                            <div class="settings-placeholder">Not connected</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="menu-layout">
                <!-- Left panel: feature/task list -->
                <div class="menu-box">
                    <div id="toolbar">
                        <div class="toolbar-boxes">Sort By</div>
                        <div class="toolbar-boxes" @click="addFeature">Add Feature</div>
                        <div class="toolbar-boxes" @click="addtask">Add Task</div>
                    </div>
                    <div v-for="feature in features" id="task-label" :key="feature.id">
                        <details :open="selectedFeatureId === feature.id">
                            <summary @click.prevent="selectFeature(feature.id)">
                                <span class="feature-summary-text">{{ feature.name }}</span>
                                <span
                                    class="feature-priority-dot"
                                    :style="{
                                        backgroundColor: priorityColor(featurePriority(feature))
                                    }"
                                ></span>
                            </summary>
                            <div
                                v-for="task in feature.tasks"
                                :key="task.id"
                                class="task-item"
                                :class="{
                                    'task-item-selected':
                                        selectedFeatureId === feature.id &&
                                        selectedTaskId === task.id
                                }"
                                @click="selectTask(feature.id, task.id)"
                            >
                                <span class="task-item-name">{{ task.name }}</span>
                                <span
                                    class="task-item-priority"
                                    :style="{ backgroundColor: priorityColor(task.priority) }"
                                >
                                    {{ task.priority }}
                                </span>
                            </div>
                        </details>
                    </div>
                </div>

                <!-- Middle panel: detail / add form -->
                <div class="menu-box">
                    <template v-if="panelMode === 'idle'">
                        <div id="background-box-2" class="idle-message">
                            <p>
                                Select a feature or task, or click <strong>Add Feature</strong> /
                                <strong>Add Task</strong> to create one.
                            </p>
                        </div>
                    </template>

                    <!-- Feature detail view -->
                    <template v-if="panelMode === 'viewingFeature' && selectedFeature">
                        <div id="desc-box">
                            <h2 class="detail-title">{{ selectedFeature.name }}</h2>
                            <p class="detail-description">{{ selectedFeature.description }}</p>
                        </div>
                        <div id="background-box-2">
                            <div class="detail-row">
                                <span class="form-label">Overall Priority</span>
                                <span
                                    class="detail-priority-badge"
                                    :style="{
                                        backgroundColor: priorityColor(
                                            featurePriority(selectedFeature)
                                        )
                                    }"
                                >
                                    {{ featurePriority(selectedFeature) }}
                                </span>
                            </div>
                            <div class="detail-row">
                                <span class="form-label">Deadline</span>
                                <span class="detail-value">
                                    {{ selectedFeature.deadline || 'No deadline set' }}
                                </span>
                            </div>
                            <div class="detail-row">
                                <span class="form-label">Progress</span>
                                <div class="progress-bar-wrapper">
                                    <div
                                        class="progress-bar-fill"
                                        :style="{
                                            width:
                                                featureProgress(selectedFeature).total > 0
                                                    ? (featureProgress(selectedFeature).done /
                                                          featureProgress(selectedFeature).total) *
                                                          100 +
                                                      '%'
                                                    : '0%'
                                        }"
                                    ></div>
                                </div>
                                <span class="detail-value">
                                    {{ featureProgress(selectedFeature).done }} /
                                    {{ featureProgress(selectedFeature).total }} tasks in review or
                                    done
                                </span>
                            </div>
                            <div class="detail-row">
                                <span class="form-label">Team Members</span>
                                <div class="member-list">
                                    <div
                                        v-for="member in selectedFeature.members"
                                        :key="member"
                                        class="member-chip"
                                    >
                                        <img src="/hexagon.svg" alt="icon" class="member-icon" />
                                        {{ member }}
                                    </div>
                                    <div
                                        v-if="!selectedFeature.members.length"
                                        class="detail-value"
                                    >
                                        No members assigned
                                    </div>
                                </div>
                            </div>
                            <div class="detail-row">
                                <span class="form-label">Tasks Summary</span>
                                <div v-if="selectedFeature.tasks.length" class="task-summary-list">
                                    <div
                                        v-for="task in selectedFeature.tasks"
                                        :key="task.id"
                                        class="task-summary-item"
                                        @click="selectTask(selectedFeature.id, task.id)"
                                    >
                                        <span class="task-summary-name">{{ task.name }}</span>
                                        <span
                                            class="task-summary-status"
                                            :style="{
                                                backgroundColor: statusColor(task.status)
                                            }"
                                        >
                                            {{ task.status }}
                                        </span>
                                        <span
                                            class="task-item-priority"
                                            :style="{
                                                backgroundColor: priorityColor(task.priority)
                                            }"
                                        >
                                            {{ task.priority }}
                                        </span>
                                    </div>
                                </div>
                                <div v-else class="detail-value">
                                    No tasks yet — click <strong>Add Task</strong> to create one.
                                </div>
                            </div>
                        </div>
                    </template>

                    <!-- Task detail view -->
                    <template v-if="panelMode === 'viewing' && selectedTask">
                        <div id="desc-box">
                            <h2 class="detail-title">{{ selectedTask.name }}</h2>
                            <p class="detail-feature">{{ selectedFeatureName }}</p>
                            <p class="detail-description">{{ selectedTask.description }}</p>
                        </div>
                        <div id="background-box-2">
                            <div class="detail-row">
                                <span class="form-label">Type</span>
                                <div class="tag-list">
                                    <span v-for="t in selectedTask.types" :key="t" class="tag">
                                        {{ t }}
                                    </span>
                                    <span v-if="!selectedTask.types.length" class="tag tag-empty">
                                        none
                                    </span>
                                </div>
                            </div>
                            <div class="detail-row">
                                <span class="form-label">Status</span>
                                <span class="detail-value">{{ selectedTask.status }}</span>
                            </div>
                            <div class="detail-row">
                                <span class="form-label">Priority</span>
                                <span
                                    class="detail-priority-badge"
                                    :style="{
                                        backgroundColor: priorityColor(selectedTask.priority)
                                    }"
                                >
                                    {{ selectedTask.priority }}
                                </span>
                            </div>
                        </div>
                    </template>

                    <!-- Add task form -->
                    <template v-if="panelMode === 'adding'">
                        <div id="desc-box">
                            <h2 class="detail-title">New Task</h2>
                            <input
                                v-model="newTask.name"
                                class="task-input"
                                type="text"
                                placeholder="Task name"
                            />
                            <textarea
                                v-model="newTask.description"
                                class="task-textarea"
                                placeholder="Task description..."
                                rows="3"
                            ></textarea>
                        </div>
                        <div id="background-box-2">
                            <div class="form-row">
                                <label class="form-label">Feature</label>
                                <select v-model="newTask.featureId" class="task-select">
                                    <option value="" disabled>Select feature...</option>
                                    <option v-for="f in features" :key="f.id" :value="f.id">
                                        {{ f.name }}
                                    </option>
                                </select>
                            </div>
                            <div class="form-row">
                                <label class="form-label">Type</label>
                                <div class="multi-select-wrapper">
                                    <div
                                        class="multi-select-trigger"
                                        @click="showTypeDropdown = !showTypeDropdown"
                                    >
                                        {{
                                            newTask.types.length
                                                ? newTask.types.join(', ')
                                                : 'Select types...'
                                        }}
                                    </div>
                                    <div v-if="showTypeDropdown" class="multi-select-dropdown">
                                        <label
                                            v-for="opt in typeOptions"
                                            :key="opt"
                                            class="checkbox-option"
                                        >
                                            <input
                                                type="checkbox"
                                                :checked="newTask.types.includes(opt)"
                                                @change="toggleType(opt)"
                                            />
                                            {{ opt }}
                                        </label>
                                    </div>
                                </div>
                            </div>
                            <div class="form-row">
                                <label class="form-label">Status</label>
                                <select v-model="newTask.status" class="task-select">
                                    <option value="" disabled>Select status...</option>
                                    <option v-for="opt in statusOptions" :key="opt" :value="opt">
                                        {{ opt }}
                                    </option>
                                </select>
                            </div>
                            <div class="form-row">
                                <label class="form-label">Priority</label>
                                <select v-model="newTask.priority" class="task-select">
                                    <option value="" disabled>Select priority...</option>
                                    <option v-for="opt in priorityOptions" :key="opt" :value="opt">
                                        {{ opt }}
                                    </option>
                                </select>
                            </div>
                            <button class="create-task-btn" @click="createTask">Create Task</button>
                        </div>
                    </template>

                    <!-- Add feature form -->
                    <template v-if="panelMode === 'addingFeature'">
                        <div id="desc-box">
                            <h2 class="detail-title">New Feature</h2>
                            <input
                                v-model="newFeature.name"
                                class="task-input"
                                type="text"
                                placeholder="Feature name"
                            />
                            <textarea
                                v-model="newFeature.description"
                                class="task-textarea"
                                placeholder="Feature description..."
                                rows="3"
                            ></textarea>
                        </div>
                        <div id="background-box-2">
                            <div class="form-row">
                                <label class="form-label">Deadline</label>
                                <input
                                    v-model="newFeature.deadline"
                                    class="task-input"
                                    type="date"
                                />
                            </div>
                            <div class="form-row">
                                <label class="form-label">Team Members</label>
                                <div class="member-input-row">
                                    <input
                                        v-model="newFeature.newMember"
                                        class="task-input member-name-input"
                                        type="text"
                                        placeholder="Member name..."
                                        @keyup.enter="addMemberToNewFeature"
                                    />
                                    <button class="add-member-btn" @click="addMemberToNewFeature">
                                        +
                                    </button>
                                </div>
                                <div v-if="newFeature.members.length" class="member-list">
                                    <div
                                        v-for="member in newFeature.members"
                                        :key="member"
                                        class="member-chip member-chip-removable"
                                    >
                                        <img src="/hexagon.svg" alt="icon" class="member-icon" />
                                        {{ member }}
                                        <button
                                            class="remove-member-btn"
                                            @click="removeMemberFromNewFeature(member)"
                                        >
                                            ×
                                        </button>
                                    </div>
                                </div>
                                <div v-else class="detail-value">No members added yet</div>
                            </div>
                            <button class="create-task-btn" @click="createFeature">
                                Create Feature
                            </button>
                        </div>
                    </template>
                </div>

                <!-- Right panel -->
                <div class="menu-box">
                    <div class="menu-box-split">
                        <div id="people" class="people-box">
                            <img src="/hexagon.svg" alt="icon" />
                            {{ teamName }}
                            <img src="/hexagon.svg" alt="icon" />
                        </div>
                        <div v-for="member in teamMembers" :key="member" class="people-box">
                            <img src="/hexagon.svg" alt="icon" />
                            {{ member }}
                            <img src="/hexagon.svg" alt="icon" />
                        </div>
                    </div>
                    <div class="menu-box-split">
                        <div class="item-box">Undo last task</div>
                        <div class="item-box">Past tasks</div>
                        <div class="item-box">Placeholder idk</div>
                    </div>
                </div>
            </div>
        </div>
    </main>
</template>

<style scoped>
details {
    border: 1px solid #aaaaaa;
    padding: 0.5em 0.5em 0;
    background-color: #ffebba;
    color: black;
    width: 90%;
    border-radius: 10px;
}

details > .features {
    border-radius: 15px;
}

summary {
    font-weight: bold;
    margin: -0.5em -0.5em 0;
    padding: 0.5em;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.feature-summary-text {
    flex: 1;
}

.feature-priority-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    flex-shrink: 0;
    margin-left: 8px;
}

details[open] {
    padding: 0.5em;
}
details[open] summary {
    border-bottom: 1px solid #aaaaaa;
    margin-bottom: 0.5em;
}
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

.menu-box-split {
    height: 45%;
    width: 100%;
    background-color: #e9c17d;
    border-radius: 15px;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    gap: 10px;
}
#task-label {
    display: flex;
    flex-direction: column;
    margin-bottom: 20px;
    margin-top: 10px;
    align-items: center;
}
#task-label .box-label {
    width: min(90%, 400px);
    height: 50px;
    background-color: #ffebba;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: black;
}

#toolbar {
    background-color: transparent;
    width: 95%;
    height: 70px;
    display: flex;
    text-align: center;
    justify-content: center;
    align-items: center;
    align-self: center;
}
#toolbar .toolbar-boxes {
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #ffebba;
    border-radius: 15px;
    width: 65%;
    height: 50px;
    margin: 10px;
    box-sizing: border-box;
    color: black;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: clamp(10px, 1.2vw, 14px);
}

/* --- Title bar --- */
#menu-title {
    color: black;
    width: 100%;
    height: 55px;
    padding: 0 25px;
    background-color: #f3bb5b;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    position: relative;
}

.menu-title-icon {
    height: 30px;
    width: 30px;
    flex-shrink: 0;
}

.menu-title-content {
    position: absolute;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 40px;
    line-height: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    pointer-events: none;
    padding: 0 70px;
}

.menu-title-settings-button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: auto;
    z-index: 1;
}

.menu-title-settings-icon {
    height: 30px;
    width: 30px;
}

@media (max-width: 900px) {
    #menu-title {
        height: 35px;
    }
    .menu-title-content {
        font-size: 28px;
        padding: 0 55px;
    }
    .menu-title-icon,
    .menu-title-settings-icon {
        height: 24px;
        width: 24px;
    }
}

/* --- Settings overlay --- */
.settings-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 100;
    background-color: rgba(0, 0, 0, 0.4);
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    padding: 20px;
}

.settings-panel {
    width: clamp(280px, 30vw, 360px);
    max-height: calc(100vh - 40px);
    background-color: #5a4226;
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.settings-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: clamp(10px, 1.5vw, 16px) clamp(14px, 1.8vw, 20px);
    background-color: #4a3520;
    border-bottom: 2px solid #3a2815;
}

.settings-title {
    font-size: clamp(18px, 2.5vw, 28px);
    font-weight: bold;
    color: #ffebba;
    letter-spacing: 2px;
}

.settings-close-btn {
    background: none;
    border: 2px solid #d4a030;
    border-radius: 50%;
    width: clamp(30px, 3.5vw, 40px);
    height: clamp(30px, 3.5vw, 40px);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
}

.settings-header-icon {
    width: clamp(16px, 2vw, 22px);
    height: clamp(16px, 2vw, 22px);
}

.settings-body {
    padding: clamp(12px, 1.8vw, 20px);
    display: flex;
    flex-direction: column;
    gap: clamp(12px, 1.5vw, 18px);
    overflow-y: auto;
}

.settings-section {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.settings-label {
    font-size: clamp(11px, 1.2vw, 13px);
    font-weight: bold;
    color: #d4a030;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.settings-input {
    width: 100%;
    padding: clamp(6px, 1vw, 10px) clamp(8px, 1.2vw, 12px);
    border: 2px solid #7a5c3a;
    border-radius: 10px;
    background-color: #ffebba;
    color: black;
    font-family: 'Google Sans Flex';
    font-size: clamp(12px, 1.3vw, 14px);
    box-sizing: border-box;
    outline: none;
}
.settings-input:focus {
    border-color: #d4a030;
}

.settings-placeholder {
    padding: clamp(6px, 1vw, 10px) clamp(8px, 1.2vw, 12px);
    border: 2px solid #7a5c3a;
    border-radius: 10px;
    background-color: #ffebba;
    color: #5a4a1e;
    font-size: clamp(12px, 1.3vw, 14px);
}

#desc-box {
    align-self: center;
    width: 80%;
    border-radius: 15px;
    background-color: #ffebba;
    margin-top: 10%;
    padding: 15px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

#background-box-2 {
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
    gap: 12px;
}

.idle-message {
    justify-content: center;
    align-items: center;
    color: #8a7540;
    font-size: 15px;
    text-align: center;
}

/* --- Task list items in left panel --- */
.task-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    margin: 4px 0;
    border-radius: 8px;
    cursor: pointer;
    background-color: #fff8e7;
    border: 2px solid transparent;
    transition:
        border-color 0.15s,
        background-color 0.15s;
}
.task-item:hover {
    background-color: #f3e3b3;
}
.task-item-selected {
    border-color: #b8860b;
    background-color: #f3e3b3;
}
.task-item-name {
    font-size: 14px;
    font-weight: 500;
}
.task-item-priority {
    font-size: 11px;
    font-weight: bold;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    text-transform: uppercase;
}

/* --- Detail view styles --- */
.detail-title {
    margin: 0;
    font-size: 20px;
    color: #3a2e0f;
}
.detail-feature {
    margin: 0;
    font-size: 13px;
    color: #8a7540;
    font-style: italic;
}
.detail-description {
    margin: 0;
    font-size: 14px;
    color: #4a3d1a;
    line-height: 1.5;
}
.detail-row {
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.detail-value {
    font-size: 14px;
    color: #4a3d1a;
    text-transform: capitalize;
}
.tag-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.tag {
    font-size: 12px;
    font-weight: bold;
    padding: 3px 10px;
    border-radius: 12px;
    background-color: #d4a030;
    color: white;
    text-transform: capitalize;
}
.tag-empty {
    background-color: #bbb;
}
.detail-priority-badge {
    display: inline-block;
    width: fit-content;
    font-size: 12px;
    font-weight: bold;
    padding: 3px 10px;
    border-radius: 12px;
    color: white;
    text-transform: uppercase;
}

/* --- Feature detail: progress bar --- */
.progress-bar-wrapper {
    width: 100%;
    height: 10px;
    background-color: #e0d0a0;
    border-radius: 5px;
    overflow: hidden;
}

.progress-bar-fill {
    height: 100%;
    background-color: #5cb85c;
    border-radius: 5px;
    transition: width 0.3s ease;
}

/* --- Feature detail: member chips --- */
.member-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.member-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background-color: #fff8e7;
    border-radius: 10px;
    font-size: 13px;
    color: #3a2e0f;
    font-weight: 500;
}

.member-chip-removable {
    justify-content: space-between;
}

.member-icon {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
}

.remove-member-btn {
    background: none;
    border: none;
    color: #d9534f;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    padding: 0 4px;
    line-height: 1;
}
.remove-member-btn:hover {
    color: #a02020;
}

/* --- Feature form: member input row --- */
.member-input-row {
    display: flex;
    gap: 8px;
    align-items: center;
}

.member-name-input {
    flex: 1;
}

.add-member-btn {
    width: 36px;
    height: 36px;
    background-color: #d4a030;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 20px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.add-member-btn:hover {
    background-color: #b8860b;
}

/* --- Feature detail: task summary list --- */
.task-summary-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.task-summary-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 8px 12px;
    background-color: #fff8e7;
    border-radius: 8px;
    cursor: pointer;
    border: 2px solid transparent;
    transition:
        border-color 0.15s,
        background-color 0.15s;
}

.task-summary-item:hover {
    background-color: #f3e3b3;
    border-color: #b8860b;
}

.task-summary-name {
    font-size: 13px;
    font-weight: 500;
    color: #3a2e0f;
    flex: 1;
}

.task-summary-status {
    font-size: 10px;
    font-weight: bold;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    text-transform: capitalize;
    white-space: nowrap;
}

/* --- Form styles --- */
.task-input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #cca94e;
    border-radius: 8px;
    background-color: #fff8e7;
    color: black;
    font-family: 'Google Sans Flex';
    font-size: 16px;
    font-weight: bold;
    box-sizing: border-box;
    outline: none;
}
.task-input:focus {
    border-color: #b8860b;
}

.task-textarea {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #cca94e;
    border-radius: 8px;
    background-color: #fff8e7;
    color: black;
    font-family: 'Google Sans Flex';
    font-size: 14px;
    box-sizing: border-box;
    resize: vertical;
    outline: none;
}
.task-textarea:focus {
    border-color: #b8860b;
}

.form-row {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.form-label {
    font-size: 13px;
    font-weight: bold;
    color: #5a4a1e;
}

.task-select {
    width: 100%;
    padding: 8px 10px;
    border: 1px solid #cca94e;
    border-radius: 8px;
    background-color: #fff8e7;
    color: black;
    font-family: 'Google Sans Flex';
    font-size: 14px;
    box-sizing: border-box;
    outline: none;
    cursor: pointer;
}
.task-select:focus {
    border-color: #b8860b;
}

.multi-select-wrapper {
    position: relative;
}

.multi-select-trigger {
    width: 100%;
    padding: 8px 10px;
    border: 1px solid #cca94e;
    border-radius: 8px;
    background-color: #fff8e7;
    color: black;
    font-family: 'Google Sans Flex';
    font-size: 14px;
    box-sizing: border-box;
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.multi-select-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background-color: #fff8e7;
    border: 1px solid #cca94e;
    border-radius: 8px;
    margin-top: 4px;
    padding: 6px 0;
    z-index: 10;
    display: flex;
    flex-direction: column;
}

.checkbox-option {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    cursor: pointer;
    font-size: 14px;
    color: black;
}
.checkbox-option:hover {
    background-color: #f3e3b3;
}

.create-task-btn {
    margin-top: auto;
    padding: 10px 20px;
    background-color: #d4a030;
    color: white;
    font-family: 'Google Sans Flex';
    font-size: 15px;
    font-weight: bold;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    align-self: center;
    width: 100%;
}
.create-task-btn:hover {
    background-color: #b8860b;
}

.item-box {
    display: flex;
    align-self: center;
    width: 80%;
    height: 20%;
    border-radius: 15px;
    background-color: #ffebba;
    justify-content: center;
    align-items: center;
    color: black;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.people-box {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 80%;
    height: 10%;
    border-radius: 10px;
    background-color: #ffebba;
    color: black;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 0 10px;
    box-sizing: border-box;
}

.people-box img {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
}
#people {
    width: 60%;
    height: 20%;
    border-radius: 10px;
    background-color: #ffc739;
    color: black;
    display: flex;
    font-size: clamp(12px, 2.5vw, 25px);
    align-items: center;
    gap: 6px;
    white-space: normal;
    overflow: hidden;
    text-align: center;
    justify-content: center;
    padding: 4px 8px;
    box-sizing: border-box;
    line-height: 1.2;
    word-break: break-word;
}
</style>
