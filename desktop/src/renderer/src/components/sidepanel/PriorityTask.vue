<script setup lang="ts">
const props = defineProps<{
    taskTitle: string
    taskText: string
    types: string[]
    status: string
    priority: string
}>()

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


</script>

<template>
    <div class="background-prio-tasks">
        <div class="foreground-prio-title">
            {{ taskTitle }}
            <span class="priority-badge" :style="{ backgroundColor: priorityColor(priority) }">
                {{ priority }}
            </span>
        </div>

        <div class="tag-row">
            <span v-for="t in types" :key="t" class="type-tag">
                {{ t }}
            </span>
            <span v-if="!types.length" class="type-tag type-tag-empty">none</span>
            <span class="status-tag" :style="{ backgroundColor: statusColor(status) }">
                {{ status }}
            </span>
        </div>

        <div class="foreground-prio-tasks">
            <div class="foreground-text">{{ taskText }}</div>
        </div>

        <div class="buttonbox">
            <div class="icontextbutton">
                Finish
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
</template>

<style scoped>
.foreground-text {
    width: 95%;
    background-color: #fff4e0;
    border-radius: 15px;
    text-align: left;
    padding: 5px;
    max-height: 200px;
    overflow-y: auto;
    color: #4d3c35;
    min-height: 80px;
}

.foreground-prio-title {
    width: 90%;
    min-height: 20px;
    background-color: #f3bb5b;
    border-radius: 15px;
    text-align: center;
    margin: 5px;
    color: black;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 6px 10px;
    box-sizing: border-box;
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

.background-prio-tasks {
    display: flex;
    width: 90%;
    border-radius: 15px;
    background-color: #ffebba;
    align-self: center;
    align-items: center;
    flex-direction: column;
    flex-shrink: 0;
    padding: 10px 0;
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
    width: 22px;
    height: 22px;
    border-width: 0px;
    border-style: solid;
    border-right: none;
    margin-left: 5px;
    margin-right: 5px;
}

.iconbutton img {
    width: 18px;
    height: 18px;
}

.foreground-prio-tasks {
    margin-top: 5px;
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
    flex-wrap: wrap;
}

.icontextbutton {
    background-color: #f3bb5b;
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
    font-weight: bold;
    width: 90%;
    min-height: 40px;
    background-color: #ffebba;
    margin: 20px;
    color: black;
    display: flex;
    justify-content: center;
    text-align: center;
    align-items: center;
    border-radius: 15px;
    flex-wrap: wrap;
    word-break: break-word;
    padding: 8px;
    gap: 5px;
    box-sizing: border-box;
    flex-shrink: 0;
}
</style>
