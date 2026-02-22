<script setup lang="ts">
import type { Feature } from './types'
import { featurePriority, featureProgress, priorityColor, statusColor } from './types'

const props = defineProps<{
    feature: Feature
}>()

defineEmits<{
    (e: 'select-task', featureId: string, taskId: string): void
}>()
</script>

<template>
    <div class="desc-box">
        <div class="detail-title-row">
            <h2 class="detail-title">{{ feature.name }}</h2>
            <a
                v-if="feature.github_number"
                :href="feature.html_url"
                class="github-issue-badge"
                target="_blank"
            >#{{ feature.github_number }}</a>
        </div>
        <p class="detail-description">{{ feature.description }}</p>
    </div>
    <div class="detail-body">
        <div class="detail-row">
            <span class="form-label">Overall Priority</span>
            <span
                class="detail-priority-badge"
                :style="{ backgroundColor: priorityColor(featurePriority(feature)) }"
            >
                {{ featurePriority(feature) }}
            </span>
        </div>
        <div class="detail-row">
            <span class="form-label">Deadline</span>
            <span class="detail-value">
                {{ feature.deadline || 'No deadline set' }}
            </span>
        </div>
        <div class="detail-row">
            <span class="form-label">Progress</span>
            <div class="progress-bar-wrapper">
                <div
                    class="progress-bar-fill"
                    :style="{
                        width:
                            featureProgress(feature).total > 0
                                ? (featureProgress(feature).done /
                                      featureProgress(feature).total) *
                                      100 +
                                  '%'
                                : '0%'
                    }"
                ></div>
            </div>
            <span class="detail-value">
                {{ featureProgress(feature).done }} /
                {{ featureProgress(feature).total }} tasks in review or done
            </span>
        </div>
        <div class="detail-row">
            <span class="form-label">Team Members</span>
            <div class="member-list">
                <div v-for="member in feature.members" :key="member" class="member-chip">
                    <img src="/hexagon.svg" alt="icon" class="member-icon" />
                    {{ member }}
                </div>
                <div v-if="!feature.members.length" class="detail-value">
                    No members assigned
                </div>
            </div>
        </div>
        <div class="detail-row">
            <span class="form-label">Tasks Summary</span>
            <div v-if="feature.tasks.length" class="task-summary-list">
                <div
                    v-for="task in feature.tasks"
                    :key="task.id"
                    class="task-summary-item"
                    @click="$emit('select-task', feature.id, task.id)"
                >
                    <span class="task-summary-name">{{ task.name }}</span>
                    <span
                        class="task-summary-status"
                        :style="{ backgroundColor: statusColor(task.status) }"
                    >
                        {{ task.status }}
                    </span>
                    <span
                        class="task-item-priority"
                        :style="{ backgroundColor: priorityColor(task.priority) }"
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

.detail-title-row {
    display: flex;
    align-items: center;
    gap: 10px;
}
.detail-title {
    margin: 0;
    font-size: 20px;
    color: #3a2e0f;
}
.github-issue-badge {
    font-size: 12px;
    font-weight: bold;
    color: #5a4a1e;
    background-color: #e0d0a0;
    padding: 2px 8px;
    border-radius: 10px;
    text-decoration: none;
    white-space: nowrap;
    flex-shrink: 0;
}
.github-issue-badge:hover {
    background-color: #c8b870;
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
.member-icon {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
}

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
.task-item-priority {
    font-size: 11px;
    font-weight: bold;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    text-transform: uppercase;
}
</style>
