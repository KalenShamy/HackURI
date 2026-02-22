<script setup lang="ts">
import type { Task } from './types'
import { priorityColor } from './types'

defineProps<{
    task: Task
    featureName: string
}>()
</script>

<template>
    <div class="desc-box">
        <h2 class="detail-title">{{ task.name }}</h2>
        <p class="detail-feature">{{ featureName }}</p>
        <p class="detail-description">{{ task.description }}</p>
    </div>
    <div class="detail-body">
        <div class="detail-row">
            <span class="form-label">Type</span>
            <div class="tag-list">
                <span v-for="t in task.types" :key="t" class="tag">{{ t }}</span>
                <span v-if="!task.types.length" class="tag tag-empty">none</span>
            </div>
        </div>
        <div class="detail-row">
            <span class="form-label">Status</span>
            <span class="detail-value">{{ task.status }}</span>
        </div>
        <div class="detail-row">
            <span class="form-label">Priority</span>
            <span
                class="detail-priority-badge"
                :style="{ backgroundColor: priorityColor(task.priority) }"
            >
                {{ task.priority }}
            </span>
        </div>
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
.form-label {
    font-size: 13px;
    font-weight: bold;
    color: #5a4a1e;
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
</style>
