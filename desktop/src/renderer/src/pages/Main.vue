<script setup lang="ts">
import { ref } from 'vue'
import SidePanel from '@renderer/components/sidepanel/SidePanel.vue'
import Setup from '@renderer/components/setup/Setup.vue'
import Main from '@renderer/components/main/Main.vue'

const currentPage = ref('sidepanel')
</script>

<template>
    <main>
        <SidePanel v-if="currentPage === 'sidepanel'" />
        <Setup v-else-if="currentPage === 'setup'" />
        <Main v-else-if="currentPage === 'main'" />
    </main>
</template>

<style scoped></style>
