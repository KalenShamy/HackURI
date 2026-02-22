<script setup lang="ts">
import type { Task } from './types'
import { statusColor, priorityColor } from './types'

defineProps<{
    teamName: string
    teamMembers: string[]
    primaryFeatureName: string
    primaryFeatureTasks: Task[]
}>()
</script>

<template>
    <div class="menu-box-split">
        <div class="people-header">
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
    <div class="menu-box-split tasks-split">
        <div class="tasks-header">{{ primaryFeatureName || 'Top Feature' }}</div>
        <div v-if="primaryFeatureTasks.length" class="tasks-list">
            <div v-for="task in primaryFeatureTasks" :key="task.id" class="task-item">
                <span class="task-name">{{ task.name }}</span>
                <span class="task-status" :style="{ backgroundColor: statusColor(task.status) }">
                    {{ task.status }}
                </span>
                <span
                    class="task-priority"
                    :style="{ backgroundColor: priorityColor(task.priority) }"
                >
                    {{ task.priority }}
                </span>
            </div>
        </div>
        <div v-else class="tasks-empty">No tasks yet</div>
    </div>
</template>

<style scoped>
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

.people-header {
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

.people-header img {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
}

.tasks-split {
    overflow-y: auto;
    justify-content: flex-start;
    padding: 12px 0;
    scrollbar-width: none;
}

.tasks-split::-webkit-scrollbar {
    display: none;
}

.tasks-header {
    width: 80%;
    font-size: 13px;
    font-weight: bold;
    color: #5a4a1e;
    padding-bottom: 6px;
    border-bottom: 1px solid #c8a84b;
    flex-shrink: 0;
}

.tasks-list {
    width: 80%;
    display: flex;
    flex-direction: column;
    gap: 6px;
    overflow-y: auto;
    scrollbar-width: none;
}

.tasks-list::-webkit-scrollbar {
    display: none;
}

.task-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    background-color: #ffebba;
    border-radius: 8px;
    font-size: 12px;
}

.task-name {
    flex: 1;
    color: #3a2e0f;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.task-status {
    font-size: 10px;
    font-weight: bold;
    color: white;
    padding: 2px 6px;
    border-radius: 8px;
    text-transform: capitalize;
    white-space: nowrap;
    flex-shrink: 0;
}

.task-priority {
    font-size: 10px;
    font-weight: bold;
    color: white;
    padding: 2px 6px;
    border-radius: 8px;
    text-transform: uppercase;
    white-space: nowrap;
    flex-shrink: 0;
}

.tasks-empty {
    font-size: 13px;
    color: #8a7540;
}
</style>
