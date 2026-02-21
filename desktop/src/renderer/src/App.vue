<script setup lang="ts">
import { ref } from 'vue'
import Setup from './pages/Main.vue'
import Main from './components/main/Main.vue'

enum pages {
    setup = 'setup',
    main = 'main',
    popup = 'popup'
}

const activePage = ref(pages.setup)

window.electron.ipcRenderer.on('set-view', (_, value: string) => {
    activePage.value = value as pages
})
</script>

<template>
    <Setup v-if="activePage === pages.setup" />
    <Main v-else-if="activePage === pages.main"> </Main>
</template>

<style scoped>
* {
    font-family: 'Google Sans Flex';
    color: #e3e3e3;
}
</style>
