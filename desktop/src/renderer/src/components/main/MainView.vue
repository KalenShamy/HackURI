<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Task, Feature, PanelMode } from './types'
import TitleBar from './TitleBar.vue'
import SettingsOverlay from './SettingsOverlay.vue'
import FeatureTaskList from './FeatureTaskList.vue'
import FeatureDetail from './FeatureDetail.vue'
import TaskDetail from './TaskDetail.vue'
import AddTaskForm from './AddTaskForm.vue'
import AddFeatureForm from './AddFeatureForm.vue'
import TeamPanel from './TeamPanel.vue'

// --- Data ---
const teamName = ref('[Insert Team]')
const showSettings = ref(false)

// --- Team members ---
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

// --- Features ---
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

// --- ID generators ---
let nextFeatureNum = features.value.length + 1
function generateFeatureId(): string {
    return `f${nextFeatureNum++}`
}

function generateTaskId(featureId: string): string {
    const feature = features.value.find((f) => f.id === featureId)
    const num = feature ? feature.tasks.length + 1 : 1
    return `${featureId}t${num}`
}

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
function handleCreateTask(payload: {
    name: string
    description: string
    types: string[]
    status: string
    priority: string
    featureId: string
}): void {
    const feature = features.value.find((f) => f.id === payload.featureId)
    if (!feature) return

    const task: Task = {
        id: generateTaskId(payload.featureId),
        name: payload.name,
        description: payload.description,
        types: payload.types,
        status: payload.status,
        priority: payload.priority
    }

    feature.tasks.push(task)
    selectedFeatureId.value = feature.id
    selectedTaskId.value = task.id
    panelMode.value = 'viewing'
}

function handleCreateFeature(payload: {
    name: string
    description: string
    deadline: string
    members: string[]
}): void {
    const feature: Feature = {
        id: generateFeatureId(),
        name: payload.name,
        description: payload.description,
        deadline: payload.deadline,
        members: payload.members,
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
            <TitleBar :team-name="teamName" @toggle-settings="showSettings = !showSettings" />

            <SettingsOverlay
                :show="showSettings"
                :team-name="teamName"
                @close="showSettings = false"
                @update:team-name="teamName = $event"
            />

            <div class="menu-layout">
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
</style>
