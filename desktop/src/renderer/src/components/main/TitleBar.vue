<script setup lang="ts">
defineProps<{
    teamName: string
}>()

defineEmits<{
    (e: 'toggle-settings'): void
    (e: 'switch-workspace'): void
}>()
</script>

<template>
    <div class="menu-title">
        <img src="/LOGOCIRCLE.png" alt="Home Icon" class="menu-title-icon" />
        <span class="menu-title-content"> {{ teamName }}'s Current Workspace </span>
        <button class="menu-title-switch-button" @click="$emit('switch-workspace')">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="menu-title-switch-icon">
                <path d="M17 3l4 4-4 4"/>
                <path d="M3 7h18"/>
                <path d="M7 21l-4-4 4-4"/>
                <path d="M21 17H3"/>
            </svg>
        </button>
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

.menu-title-switch-button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-left: 12px;
    z-index: 1;
    color: inherit;
}

.menu-title-switch-icon {
    height: 26px;
    width: 26px;
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
