<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
    taskTitle: string
    taskText: string
    teamName: string
    types: string[]
    status: string
    priority: string
    isImportantTask: boolean
}>()

const isExpanded = ref(false)

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
        default:
            return '#999'
    }
}

function toggleExpand(): void {
    isExpanded.value = !isExpanded.value
}
</script>

<template>
    <div class="other-task-root">
        <!-- "Other tasks" header only on first important task -->
        <div v-if="isImportantTask" class="team-features">
            Other tasks
            <div class="iconbutton">
                <img src="/filter.svg" />
            </div>
        </div>

        <!-- Task card -->
        <div class="background-prio-tasks">
            <!-- Always visible header -->
            <div class="task-header">
                <div class="task-title-container">
                    <span class="task-title">
                        <img src="/hexagon.svg" alt="task icon" />{{ taskTitle }}
                    </span>
                    <span
                        class="priority-badge"
                        :style="{ backgroundColor: priorityColor(priority) }"
                    >
                        {{ priority }}
                    </span>
                </div>
                <div class="iconbutton toggle-btn" @click="toggleExpand">
                    <span v-if="isExpanded" style="color: white">▲</span>
                    <span v-else style="color: white">▼</span>
                </div>
            </div>

            <!-- Collapsible details -->
            <div class="task-body-wrapper" :class="{ expanded: isExpanded }">
                <div class="task-body">
                    <!-- Tags row -->
                    <div class="tag-row">
                        <span v-for="t in types" :key="t" class="type-tag">
                            {{ t }}
                        </span>
                        <span v-if="!types.length" class="type-tag type-tag-empty"> none </span>
                        <span class="status-tag" :style="{ backgroundColor: statusColor(status) }">
                            {{ status }}
                        </span>
                    </div>
                    <div class="foreground-prio-tasks">
                        <div class="foreground-text">{{ taskText }}</div>
                    </div>
                    <div class="buttonbox">
                        <div class="icontextbutton">
                            Prioritize
                            <img src="/star.svg" />
                        </div>
                        <div class="icontextbutton">
                            Drop
                            <img src="/checkmark.svg" />
                        </div>
                        <div class="icontextbutton">
                            Deadline
                            <img src="/clock.svg" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.other-task-root {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}
.foreground-text {
    width: 95%;
    background-color: #fff4e0;
    border-radius: 15px;
    text-align: left;
    padding: 5px;
}
.background-prio-tasks {
    margin-top: 15px;
    display: flex;
    width: 90%;
    padding: 10px 0;
    background-color: #f3bb5b;
    border-radius: 15px;
    align-self: center;
    align-items: center;
    flex-direction: column;
}
.task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 90%;
}
.task-title-container {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}
.task-title {
    align-items: center;
    display: flex;
    gap: 10px;
    font-size: 1.1em;
    color: #4d3c35;
}
.priority-badge {
    font-size: 10px;
    font-weight: bold;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    text-transform: uppercase;
    white-space: nowrap;
    flex-shrink: 0;
}
.tag-row {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    justify-content: center;
    width: 90%;
    margin-top: 8px;
    margin-bottom: 4px;
}
.type-tag {
    font-size: 10px;
    font-weight: bold;
    padding: 2px 8px;
    border-radius: 10px;
    background-color: #d4a030;
    color: white;
    text-transform: capitalize;
    white-space: nowrap;
}
.type-tag-empty {
    background-color: #bbb;
}
.status-tag {
    font-size: 10px;
    font-weight: bold;
    padding: 2px 8px;
    border-radius: 10px;
    color: white;
    text-transform: capitalize;
    white-space: nowrap;
}
.task-body-wrapper {
    display: grid;
    grid-template-rows: 0fr;
    transition: grid-template-rows 0.3s ease;
    width: 100%;
    overflow: hidden;
}
.task-body-wrapper.expanded {
    grid-template-rows: 1fr;
}
.task-body {
    min-height: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.toggle-btn {
    background-color: #25211f;
}
.iconbutton {
    background-color: #25211f;
    border-radius: 10px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    pointer-events: auto;
    position: relative;
    width: 25px;
    height: 25px;
    border-width: 0px;
    border-style: solid;
    border-right: none;
    margin-left: 5px;
    margin-right: 5px;
}
.foreground-prio-tasks {
    margin-top: 8px;
    width: 90%;
    background-color: #fff4e0;
    border-radius: 15px;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 10px 0;
    max-height: 200px;
    overflow-y: auto;
    color: #4d3c35;
}
.buttonbox {
    display: flex;
    justify-content: center;
    text-align: center;
    align-items: center;
    border-radius: 15px;
    margin-top: 10px;
    margin-bottom: 5px;
    flex-wrap: wrap;
}
.icontextbutton {
    background-color: #fff4e0;
    border-radius: 10px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    pointer-events: auto;
    position: relative;
    border-width: 0px;
    border-style: solid;
    border-right: none;
    color: #4d3c35;
    gap: 5px;
    margin: 5px;
    padding-left: 10px;
    padding-right: 10px;
    height: 30px;
    white-space: nowrap;
}
.team-features {
    width: 90%;
    height: 40px;
    background-color: #f3bb5b;
    margin-top: 10px;
    color: #4d3c35;
    display: flex;
    justify-content: space-between;
    padding: 0 15px;
    text-align: center;
    align-items: center;
    border-radius: 15px;
    font-size: 1.2em;
    box-sizing: border-box;
}
</style>
