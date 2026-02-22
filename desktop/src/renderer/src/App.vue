<script setup lang="ts">
import { ref } from 'vue'
import SidePanel from './components/sidepanel/SidePanel.vue'
import SetupView from './components/setup/SetupView.vue'
import MainView from './components/main/MainView.vue'

enum pages {
    sidepanel = 'sidepanel',
    main = 'main',
    setup = 'setup'
}

const activePage = ref<pages | null>(null)

window.electron.ipcRenderer.on('set-view', (_, value: string) => {
    activePage.value = value as pages
})
</script>

<template>
    <main>
        <SidePanel v-if="activePage === pages.sidepanel" />
        <MainView v-else-if="activePage === pages.main" />
        <SetupView v-else-if="activePage === pages.setup" />
    </main>
</template>

<style scoped>
main {
    font-family: 'Google Sans Flex';
    color: #e3e3e3;
}
</style>
