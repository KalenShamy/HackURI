<script setup lang="ts">
import { ref, reactive, computed } from 'vue'

// --- Data ---
const teamName = ref('[Insert Team]')

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
    tasks: Task[]
}

const features = ref<Feature[]>([
    {
        id: 'f1',
        name: 'Feature #1',
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

// --- State machine for middle panel ---
// Modes: 'idle' | 'viewing' | 'adding'
type PanelMode = 'idle' | 'viewing' | 'adding'
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

const selectedFeatureName = computed<string>(() => {
    if (!selectedFeatureId.value) return ''
    return features.value.find((f) => f.id === selectedFeatureId.value)?.name ?? ''
})

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
    priority: ''
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
    showTypeDropdown.value = false
    panelMode.value = 'adding'
}

function createTask(): void {
    console.log('Creating task:', { ...newTask })
    // TODO: send to API
    newTask.name = ''
    newTask.description = ''
    newTask.types = []
    newTask.status = ''
    newTask.priority = ''
    showTypeDropdown.value = false
    panelMode.value = 'idle'
}

// --- Priority badge color ---
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
</script>

<template>
    <main>
        <div class="whole-box">
            <div id="menu-title">
                <img src="/LOGOCIRCLE.png" alt="Home Icon" class="menu-title-icon" />
                <span class="menu-title-content">{{ teamName }}'s Current Workspace</span>
                <button class="menu-title-settings-button">
                    <img src="/settings.png" alt="Settings Icon" class="menu-title-settings-icon" />
                </button>
            </div>
            <div class="menu-layout">
                <!-- Left panel: feature/task list -->
                <div class="menu-box">
                    <div id="toolbar">
                        <div class="toolbar-boxes">Sort By</div>
                        <div class="toolbar-boxes" @click="addtask">Add</div>
                    </div>
                    <div v-for="feature in features" id="task-label" :key="feature.id">
                        <details :open="selectedFeatureId === feature.id">
                            <summary
                                @click.prevent="
                                    selectedFeatureId === feature.id
                                        ? ((selectedFeatureId = null),
                                          (selectedTaskId = null),
                                          (panelMode = panelMode === 'adding' ? 'adding' : 'idle'))
                                        : ((selectedFeatureId = feature.id),
                                          (selectedTaskId = null),
                                          (panelMode = panelMode === 'adding' ? 'adding' : 'idle'))
                                "
                            >
                                {{ feature.name }}
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
                    <!-- IDLE state -->
                    <template v-if="panelMode === 'idle'">
                        <div id="background-box-2" class="idle-message">
                            <p>Select a task or click <strong>Add</strong> to create one.</p>
                        </div>
                    </template>

                    <!-- VIEWING state -->
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

                    <!-- ADDING state -->
                    <template v-if="panelMode === 'adding'">
                        <div id="desc-box">
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
                </div>

                <!-- Right panel: people / actions -->
                <div id="trans" class="menu-box">
                    <div class="menu-box-split">
                        <div id="people" class="people-box">
                            <img src="/star.svg" />
                        </div>
                        <div id="people" class="people-box">Hai-bien Nguyen</div>
                        <div class="people-box">Hannah Ritchie</div>
                        <div class="people-box">Paul Fang Li</div>
                        <div class="people-box">Kaylen Shamey</div>
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

.menu-box-split {
    height: 45%;
    width: 90%;
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
    border-radius: 40px;
    width: 65%;
    height: 50px;
    margin: 10px;
    box-sizing: border-box;
    color: black;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
#menu-title {
    color: black;
    align-self: flex-start;
    height: 55px;
    width: calc(100% - 50px);
    padding: 20px 25px;
    background-color: #f3bb5b;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.menu-title-icon {
    height: 30px;
    width: 30px;
    flex-shrink: 0;
}

.menu-title-content {
    flex-grow: 1;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin: 0 10px;
    font-size: 40px;
    line-height: 1;
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
    }
    .menu-title-icon,
    .menu-title-settings-icon {
        height: 24px;
        width: 24px;
    }
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
    justify-content: center;
    align-items: center;
    width: 80%;
    height: 10%;
    border-radius: 10px;
    background-color: #ffebba;
    color: black;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
#people {
    margin-top: 28px;
}
</style>
