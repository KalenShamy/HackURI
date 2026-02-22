<script setup lang="ts">
import type { Feature } from './types'
import { priorityColor, featurePriority } from './types'

defineProps<{
    features: Feature[]
    selectedFeatureId: string | null
    selectedTaskId: string | null
}>()

defineEmits<{
    (e: 'select-feature', featureId: string): void
    (e: 'select-task', featureId: string, taskId: string): void
    (e: 'add-feature'): void
    (e: 'add-task'): void
}>()
</script>

<template>
    <div class="toolbar">
        <div class="toolbar-boxes">Sort By</div>
        <div class="toolbar-boxes" @click="$emit('add-feature')">Add Feature</div>
        <div class="toolbar-boxes" @click="$emit('add-task')">Add Task</div>
    </div>
    <div v-for="feature in features" class="task-label" :key="feature.id">
        <details :open="selectedFeatureId === feature.id">
            <summary @click.prevent="$emit('select-feature', feature.id)">
                <span class="feature-summary-text">{{ feature.name }}</span>
                <span
                    class="feature-priority-dot"
                    :style="{ backgroundColor: priorityColor(featurePriority(feature)) }"
                ></span>
            </summary>
            <div
                v-for="task in feature.tasks"
                :key="task.id"
                class="task-item"
                :class="{
                    'task-item-selected':
                        selectedFeatureId === feature.id && selectedTaskId === task.id
                }"
                @click="$emit('select-task', feature.id, task.id)"
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
</template>

<style scoped>
details {
    border: 1px solid #aaaaaa;
    padding: 0.5em 0.5em 0;
    background-color: #ffc739;
    color: black;
    width: 90%;
    border-radius: 10px;
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

.task-label {
    display: flex;
    flex-direction: column;
    margin-bottom: 20px;
    margin-top: 10px;
    align-items: center;
}

.toolbar {
    background-color: transparent;
    width: 95%;
    height: 70px;
    display: flex;
    text-align: center;
    justify-content: center;
    align-items: center;
    align-self: center;
}
.toolbar-boxes {
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
</style>
