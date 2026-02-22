<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{
    taskTitle: string
    taskText: string
    teamName: string
}>()

function switchscreen(): void {
    window.electron.ipcRenderer.send('open-main-window')
}
</script>
<template>
    <!-- menu, put all divs in here -->
    <div class="team-features">
        <div class="iconbutton" @click="switchscreen">
            <img src="/home.svg" />
        </div>
        {{ teamName }}'s Assigned Tasks
        <div class="iconbutton" @click="">
            <img src="/filter.svg" />
        </div>
    </div>
    <!-- team features first div -->
    <div class="background-prio-tasks">
        <div class="foreground-prio-title">{{ taskTitle }}</div>
        <div class="foreground-prio-tasks">
            <div class="foreground-text">{{ taskText }}</div>
        </div>
        <div class="buttonbox">
            <div class="icontextbutton" @click="">
                Finish
                <img src="/star.svg" />
            </div>
            <div class="icontextbutton" @click="">
                Drop
                <img src="/checkmark.svg" />
            </div>
            <div class="icontextbutton" @click="">
                Deadline
                <img src="/clock.svg" />
            </div>
        </div>
    </div>
</template>

<style scoped>
.foreground-text {
    width: 95%;
    height: 105px;
    background-color: #fff4e0;
    border-radius: 15px;
    text-align: center;
}
.foreground-prio-title {
    width: 90%;
    height: 20px;
    background-color: #f3bb5b;
    border-radius: 15px;
    text-align: center;
    margin: 5px;
    color: black;
}
.background-prio-tasks {
    display: flex;
    width: 90%;
    height: 200px;
    border-radius: 50px;
    background-color: #ffebba;
    border-radius: 15px;
    align-self: center;
    align-items: center;
    flex-direction: column;
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
    margin-top: 5px;
    width: 90%;
    height: 120px;
    background-color: #f3bb5b;
    border-radius: 15px;
    display: flex;
    justify-content: center;
    align-items: center;
}
.buttonbox {
    display: flex;
    justify-content: center;
    text-align: center;
    align-items: center;
    border-radius: 15px;
    align-content: center;
    justify-content: center;
    display: flex;
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
    margin-left: 5px;
    color: #4d3c35;
    gap: 5px;
    margin: 5px;
    padding-left: 10px;
    padding-right: 10px;
    height: 30px;
    margin-top: 5px;
}
.team-features {
    width: 90%;
    height: 40px;
    background-color: #ffebba;
    margin: 20px;
    color: black;
    display: flex;
    justify-content: center;
    text-align: center;
    align-items: center;
    border-radius: 15px;
    align-content: center;
    justify-content: center;
    display: flex;
}
</style>
