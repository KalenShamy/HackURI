<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { Feature } from './types'

defineProps<{
    features: Feature[]
}>()

const emit = defineEmits<{
    (
        e: 'create',
        payload: {
            name: string
            description: string
            types: string[]
            status: string
            priority: string
            featureId: string
        }
    ): void
}>()

const typeOptions = ['bug', 'enhancement', 'proposal', 'documentation']
const statusOptions = ['todo', 'in progress', 'review', 'blocked']
const priorityOptions = ['low', 'medium', 'high']

const form = reactive({
    name: '',
    description: '',
    types: [] as string[],
    status: '',
    priority: '',
    featureId: ''
})

const showTypeDropdown = ref(false)

function toggleType(type: string): void {
    const idx = form.types.indexOf(type)
    if (idx === -1) {
        form.types.push(type)
    } else {
        form.types.splice(idx, 1)
    }
}

function submit(): void {
    if (!form.name || !form.featureId || !form.status || !form.priority) return

    emit('create', {
        name: form.name,
        description: form.description,
        types: [...form.types],
        status: form.status,
        priority: form.priority,
        featureId: form.featureId
    })

    form.name = ''
    form.description = ''
    form.types = []
    form.status = ''
    form.priority = ''
    form.featureId = ''
    showTypeDropdown.value = false
}
</script>

<template>
    <div class="desc-box">
        <h2 class="detail-title">New Task</h2>
        <input v-model="form.name" class="task-input" type="text" placeholder="Task name" />
        <textarea
            v-model="form.description"
            class="task-textarea"
            placeholder="Task description..."
            rows="3"
        ></textarea>
    </div>
    <div class="detail-body">
        <div class="form-row">
            <label class="form-label">Feature</label>
            <select v-model="form.featureId" class="task-select">
                <option value="" disabled>Select feature...</option>
                <option v-for="f in features" :key="f.id" :value="f.id">
                    {{ f.name }}
                </option>
            </select>
        </div>
        <div class="form-row">
            <label class="form-label">Type</label>
            <div class="multi-select-wrapper">
                <div class="multi-select-trigger" @click="showTypeDropdown = !showTypeDropdown">
                    {{ form.types.length ? form.types.join(', ') : 'Select types...' }}
                </div>
                <div v-if="showTypeDropdown" class="multi-select-dropdown">
                    <label v-for="opt in typeOptions" :key="opt" class="checkbox-option">
                        <input
                            type="checkbox"
                            :checked="form.types.includes(opt)"
                            @change="toggleType(opt)"
                        />
                        {{ opt }}
                    </label>
                </div>
            </div>
        </div>
        <div class="form-row">
            <label class="form-label">Status</label>
            <select v-model="form.status" class="task-select">
                <option value="" disabled>Select status...</option>
                <option v-for="opt in statusOptions" :key="opt" :value="opt">
                    {{ opt }}
                </option>
            </select>
        </div>
        <div class="form-row">
            <label class="form-label">Priority</label>
            <select v-model="form.priority" class="task-select">
                <option value="" disabled>Select priority...</option>
                <option v-for="opt in priorityOptions" :key="opt" :value="opt">
                    {{ opt }}
                </option>
            </select>
        </div>
        <button class="create-task-btn" @click="submit">Create Task</button>
    </div>
</template>

<style scoped>
.desc-box {
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

.detail-body {
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

.detail-title {
    margin: 0;
    font-size: 20px;
    color: #3a2e0f;
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
</style>
