<script setup lang="ts">
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
    flex-shrink: 0;
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
    margin-top: 15px;
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
