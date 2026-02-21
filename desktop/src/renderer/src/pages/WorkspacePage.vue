<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const workspaceId = route.params.id
</script>

<template>
  <div class="workspace-page">
    <h1>Workspace {{ workspaceId }}</h1>
    <p>Task board will go here.</p>
  </div>
</template>
