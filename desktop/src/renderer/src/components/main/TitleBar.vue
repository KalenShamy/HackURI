<script setup lang="ts">
defineProps<{
    teamName: string
}>()

defineEmits<{
    (e: 'toggle-settings'): void
}>()
</script>

<template>
    <div class="menu-title">
        <img src="/LOGOCIRCLE.png" alt="Home Icon" class="menu-title-icon" />
        <span class="menu-title-content"> {{ teamName }}'s Current Workspace </span>
        <button class="menu-title-settings-button" @click="$emit('toggle-settings')">
            <img src="/settings.png" alt="Settings Icon" class="menu-title-settings-icon" />
        </button>
    </div>
</template>

<style scoped>
.menu-title {
    color: black;
    width: 100%;
    height: 55px;
    padding: 0 25px;
    background-color: #f3bb5b;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    position: relative;
}

.menu-title-icon {
    height: 30px;
    width: 30px;
    flex-shrink: 0;
}

.menu-title-content {
    position: absolute;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 40px;
    line-height: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    pointer-events: none;
    padding: 0 70px;
}

.menu-title-settings-button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: auto;
    z-index: 1;
}

.menu-title-settings-icon {
    height: 30px;
    width: 30px;
}

@media (max-width: 900px) {
    .menu-title {
        height: 35px;
    }
    .menu-title-content {
        font-size: 28px;
        padding: 0 55px;
    }
    .menu-title-icon,
    .menu-title-settings-icon {
        height: 24px;
        width: 24px;
    }
}
</style>
