<script setup lang="ts">
import { onMounted, ref } from 'vue'
import SidePanel from '@renderer/components/sidepanel/SidePanel.vue'
import Setup from '@renderer/components/setup/Setup.vue'
import Main from '@renderer/components/main/Main.vue'

const currentPage = ref('')

onMounted(() => {
    if (!currentPage.value) {
        currentPage.value = 'sidepanel'
    }
})
</script>

<template>
    <main>
        <SidePanel v-if="currentPage === 'sidepanel'" />
        <Setup v-else-if="currentPage === 'setup'" />
        <Main v-else-if="currentPage === 'main'" />
    </main>
</template>

<style scoped></style>
