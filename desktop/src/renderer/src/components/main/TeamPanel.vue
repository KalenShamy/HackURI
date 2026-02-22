<script setup lang="ts">
defineProps<{
    teamName: string
    teamMembers: string[]
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
    <div class="menu-box-split">
        <div class="item-box">Undo last task</div>
        <div class="item-box">Past tasks</div>
        <!-- <div class="item-box">Placeholder idk</div> -->
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
</style>
