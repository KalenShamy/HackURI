<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from 'vue'
import PriorityTask from './PriorityTask.vue'
import OtherTask from './OtherTask.vue'

type SidePanelTask = {
    id: string
    taskTitle: string
    taskText: string
    types: string[]
    status: string
    priority: string
}

const menuVisible = ref(false)
const hoveringInvisBox = ref(false)
const teamName = ref('')
const allTasks = ref<SidePanelTask[]>([])

const priorityTask = computed(() => allTasks.value[0] ?? null)
const otherTasks = computed(() => allTasks.value.slice(1))

async function loadWorkspaceById(workspaceId: string): Promise<void> {
    try {
        const workspaces = await window.electron.ipcRenderer.invoke('fetch-workspaces')
        const workspace = workspaces.find((w) => w.id === workspaceId) ?? workspaces[0]
        if (!workspace) return
        teamName.value = workspace.name

        const features = await window.electron.ipcRenderer.invoke('fetchFeatures', workspace.id)
        const primaryFeature = features[0]
        if (!primaryFeature) {
            allTasks.value = []
            return
        }

        const tasks = await window.electron.ipcRenderer.invoke('fetchTasks', {
            feature: primaryFeature.id
        })

        allTasks.value = tasks.map((t) => ({
            id: t.id,
            taskTitle: t.title,
            taskText: t.description,
            types: [],
            status: t.status === 'in_progress' ? 'in progress' : t.status,
            priority: t.priority
        }))
    } catch (e) {
        console.error('SidePanel: failed to load workspace', e)
    }
}

let removeWorkspaceChangedListener: (() => void) | null = null
let removeMouseMoveListener: (() => void) | null = null
let removeMouseLeaveListener: (() => void) | null = null
let pendingPointerEvent: MouseEvent | null = null
let pendingFrame: number | null = null
let ignoreMouse: boolean | null = null

function syncHoveringState(hovering: boolean): void {
    if (hoveringInvisBox.value !== hovering) {
        hoveringInvisBox.value = hovering
    }

    const nextIgnoreMouse = !hovering
    if (ignoreMouse !== nextIgnoreMouse) {
        ignoreMouse = nextIgnoreMouse
        window.electron.ipcRenderer.send('set-ignore-mouse', nextIgnoreMouse)
    }
}

onMounted(async () => {
    const sideMenu = document.getElementById('sidemenudiv')!

    removeWorkspaceChangedListener = window.electron.ipcRenderer.on(
        'workspace-changed',
        (_, workspaceId: string) => {
            loadWorkspaceById(workspaceId)
        }
    )

    const flushPointerCheck = (): void => {
        pendingFrame = null
        if (!pendingPointerEvent) return

        const clientX = pendingPointerEvent.clientX
        const clientY = pendingPointerEvent.clientY
        let hovering = false

        const widget = document.querySelector('.floating-widget')
        if (widget) {
            const rect = widget.getBoundingClientRect()
            if (
                clientX >= rect.left &&
                clientX <= rect.right &&
                clientY >= rect.top &&
                clientY <= rect.bottom
            ) {
                hovering = true
            }
        }

        if (!hovering) {
            const target = document.elementFromPoint(clientX, clientY)
            hovering = !!target && (target === sideMenu || sideMenu.contains(target))
        }

        syncHoveringState(hovering)
        pendingPointerEvent = null
    }

    const onMouseMove = (e: MouseEvent): void => {
        pendingPointerEvent = e
        if (pendingFrame !== null) return
        // Coalesce high-frequency mousemove events to one check per frame.
        pendingFrame = window.requestAnimationFrame(flushPointerCheck)
    }

    window.addEventListener('mousemove', onMouseMove, { passive: true })
    removeMouseMoveListener = () => {
        window.removeEventListener('mousemove', onMouseMove)
    }

    const onMouseLeave = (): void => {
        syncHoveringState(false)
    }

    sideMenu.addEventListener('mouseleave', onMouseLeave)
    removeMouseLeaveListener = () => {
        sideMenu.removeEventListener('mouseleave', onMouseLeave)
    }

    syncHoveringState(false)

    const [workspaces, savedId] = await Promise.all([
        window.electron.ipcRenderer.invoke('fetch-workspaces'),
        window.electron.ipcRenderer.invoke('get-active-workspace-id')
    ])
    if (!workspaces.length) return
    const initial = workspaces.find((w: { id: string }) => w.id === savedId) ?? workspaces[0]
    await loadWorkspaceById(initial.id)
})

onUnmounted(() => {
    removeWorkspaceChangedListener?.()
    removeMouseMoveListener?.()
    removeMouseLeaveListener?.()

    if (pendingFrame !== null) {
        window.cancelAnimationFrame(pendingFrame)
        pendingFrame = null
    }
    pendingPointerEvent = null
})

const arrowicon = computed(() => (menuVisible.value ? '/arrow_forward.svg' : '/arrow_back.svg'))
const showButton = computed(() => menuVisible.value || hoveringInvisBox.value)

function toggleMenu(): void {
    menuVisible.value = !menuVisible.value
}

function openMainWindow(): void {
    window.electron.ipcRenderer.send('open-main-window')
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
                <div class="panel-header">
                    <div class="iconbutton" @click="openMainWindow">
                        <img src="/home.svg" />
                    </div>
                    {{ teamName || 'Workspace' }}'s Assigned Tasks
                    <div class="iconbutton">
                        <img src="/filter.svg" />
                    </div>
                </div>
                <PriorityTask
                    v-if="priorityTask"
                    :task-title="priorityTask.taskTitle"
                    :task-text="priorityTask.taskText"
                    :types="priorityTask.types"
                    :status="priorityTask.status"
                    :priority="priorityTask.priority"
                />
                <div v-else class="no-tasks">No tasks for this feature yet.</div>
                <OtherTask
                    v-for="(task, i) in otherTasks"
                    :key="task.id"
                    :task-title="task.taskTitle"
                    :task-text="task.taskText"
                    :team-name="teamName"
                    :types="task.types"
                    :status="task.status"
                    :priority="task.priority"
                    :is-important-task="i === 0"
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

.panel-header {
    font-weight: bold;
    width: 90%;
    min-height: 40px;
    background-color: #ffebba;
    margin: 20px auto 16px;
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
    padding-bottom: 10px;
}

.iconbutton {
    background-color: #25211f;
    border-radius: 10px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    pointer-events: auto;
    width: 25px;
    height: 25px;
    flex-shrink: 0;
    margin-left: 10px;
    margin-right: 10px;
}

.iconbutton img {
    width: 18px;
    height: 18px;
}

.no-tasks {
    margin: 20px;
    padding: 16px;
    background-color: #ffebba;
    border-radius: 15px;
    text-align: center;
    color: #8a7540;
    font-size: 14px;
}
</style>
