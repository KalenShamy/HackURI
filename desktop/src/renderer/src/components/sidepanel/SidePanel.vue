<script setup lang="ts">
import { onMounted, ref, computed, Ref } from 'vue'
import PriorityTask from './PriorityTask.vue'
import OtherTask from './OtherTask.vue'

type Task = {
    id: string
    taskTitle: string
    taskText: string
    teamName: string
    types: string[]
    status: string
    priority: string
    isImportantTask?: boolean
}

const menuVisible = ref(false)
const hoveringInvisBox = ref(false)

const teamName = ref('[Insert Team]')

const priorityTask: Ref<Task> = ref({
    id: 'f1t3',
    taskTitle: 'Task #3',
    taskText: 'Something small enough to escape casual notice.',
    teamName: teamName.value,
    types: ['documentation'],
    status: 'review',
    priority: 'high'
})

const otherTasks: Ref<Task[]> = ref([
    {
        id: 'f1t1',
        taskTitle: 'Task #1',
        taskText: 'Something small enough to escape casual notice.',
        teamName: teamName.value,
        types: ['bug'],
        status: 'todo',
        priority: 'low',
        isImportantTask: true
    },
    {
        id: 'f1t2',
        taskTitle: 'Task #2',
        taskText: 'Something small enough to escape casual notice.',
        teamName: teamName.value,
        types: ['enhancement'],
        status: 'in progress',
        priority: 'medium'
    },
    {
        id: 'f2t1',
        taskTitle: 'Task #1',
        taskText: 'Something small enough to escape casual notice.',
        teamName: teamName.value,
        types: ['proposal'],
        status: 'blocked',
        priority: 'medium'
    }
])

onMounted(() => {
    const sideMenu = document.getElementById('sidemenudiv')!

    window.addEventListener('mousemove', (e) => {
        const children = sideMenu.getElementsByTagName('*')
        let hovering = false
        for (const child of children) {
            const rect = child.getBoundingClientRect()
            if (
                e.clientX >= rect.left &&
                e.clientX <= rect.right &&
                e.clientY >= rect.top &&
                e.clientY <= rect.bottom
            ) {
                hovering = true
                break
            }
        }
        hoveringInvisBox.value = hovering
        window.electron.ipcRenderer.send('set-ignore-mouse', !hovering)
    })

    sideMenu.addEventListener('mouseleave', () => {
        hoveringInvisBox.value = false
        window.electron.ipcRenderer.send('set-ignore-mouse', true)
    })
})

const arrowicon = computed(() => (menuVisible.value ? '/arrow_forward.svg' : '/arrow_back.svg'))
const showButton = computed(() => menuVisible.value || hoveringInvisBox.value)

function toggleMenu(): void {
    menuVisible.value = !menuVisible.value
}
</script>

<template>
    <div id="invisbox" class="invisible-box">
        <!-- side menu panel, slides in/out -->
        <div id="sidemenudiv" class="sidemenudiv" :class="{ visible: menuVisible }">
            <div class="floating-widget" :class="{ hidden: !showButton }" @click="toggleMenu">
                <img :src="arrowicon" alt="close arrow" />
            </div>
            <div class="sidemenu">
                <PriorityTask
                    :task-title="priorityTask.taskTitle"
                    :task-text="priorityTask.taskText"
                    :team-name="priorityTask.teamName"
                    :types="priorityTask.types"
                    :status="priorityTask.status"
                    :priority="priorityTask.priority"
                />
                <OtherTask
                    v-for="task in otherTasks"
                    :key="task.id"
                    :task-title="task.taskTitle"
                    :task-text="task.taskText"
                    :team-name="task.teamName"
                    :types="task.types"
                    :status="task.status"
                    :priority="task.priority"
                    :is-important-task="task.isImportantTask ?? false"
                />
            </div>
        </div>
    </div>
</template>

<style scoped>
.sidemenu {
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    background-color: #e9c17d;
    width: 350px;
    height: 100vh;
    border-radius: 30px;
    display: flex;
    justify-content: flex-start;
    flex-direction: column;
    overflow-y: auto;
    overflow-x: hidden;
    pointer-events: auto;
    padding-bottom: 20px;
}
h1 {
    color: white;
}
.invisible-box {
    position: fixed;
    top: 0;
    right: 0;
    background-color: transparent;
    border-width: 0px;
    pointer-events: none;
    width: 100%;
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: flex-end;
}

/* Slide the whole panel in/out */
.sidemenudiv {
    position: absolute;
    right: 0;
    top: 0;
    height: 100%;
    display: flex;
    flex-direction: row;
    align-items: center;
    transform: translateX(calc(100% - 52px));
    transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.sidemenudiv.visible {
    transform: translateX(0%);
}
/* Fade out the open button when menu is visible */
.open-btn {
    opacity: 1;
    pointer-events: auto;
    transition: opacity 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.open-btn.hidden {
    opacity: 0;
    pointer-events: none;
}

.floating-widget {
    position: relative;
    width: 50px;
    height: 80px;
    border-width: 2px;
    border-style: solid;
    border-right: none;
    border-color: var(--brownish);
    border-top-left-radius: 50px;
    border-bottom-left-radius: 50px;
    background-color: var(--off-black);
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    pointer-events: auto;
    z-index: 9999;
    box-shadow: -2px 0 5px rgba(0, 0, 0, 0.2);
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
    opacity: 1;
}

.floating-widget.hidden {
    opacity: 0;
    pointer-events: none;
    transition-delay: 4s;
}

h1 {
    color: white;
}

.icon {
    width: 30px;
    height: 30px;
    color: #a0a0a0;
}
#other-task-background {
    width: 90%;
    height: 128px;
    background-color: #ffebba;
}

#background-large {
    width: 80%;
    height: 480px;
}
.sidemenu::-webkit-scrollbar {
    display: none;
}
</style>
