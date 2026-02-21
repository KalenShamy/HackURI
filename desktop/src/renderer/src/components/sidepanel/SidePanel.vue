<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'

const menuVisible = ref(false)

onMounted(() => {
    const invisbox = document.getElementById('invisbox')!

    window.addEventListener('mousemove', (e) => {
        const children = invisbox.getElementsByTagName('*')
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
        window.electron.ipcRenderer.send('set-ignore-mouse', !hovering)
    })

    invisbox.addEventListener('mouseleave', () => {
        window.electron.ipcRenderer.send('set-ignore-mouse', true)
    })
})
const arrowicon = computed(() => (menuVisible.value ? '/arrow_forward.svg' : '/arrow_back.svg'))
function toggleMenu(): void {
    menuVisible.value = !menuVisible.value
}
</script>

<template>
    <div id="invisbox" class="invisible-box">
        <!-- side menu panel, slides in/out -->
        <div class="sidemenudiv" :class="{ visible: menuVisible }">
            <div id="buttonbox">
                <div class="floating-widget" @click="toggleMenu">
                    <img :src="arrowicon" alt="close arrow" />
                </div>
            </div>
            <div class="sidemenu">
                <h1>Menu</h1>
            </div>
        </div>
    </div>
</template>

<style scoped>
.invisible-box {
    position: fixed;
    top: 0;
    right: 0;
    background-color: transparent;
    border-width: 1px;
    border-style: solid;
    pointer-events: none;
    width: 100%;
    height: 100%;
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
    transform: translateX(calc(100% - 50px));
    transition: transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.sidemenudiv.visible {
    transform: translateX(0%);
}

#buttonbox {
    display: flex;
    flex-direction: column;
    gap: 8px;
    align-items: center;
    justify-content: center;
    pointer-events: auto;
}

.sidemenu {
    background-color: bisque;
    width: 350px;
    height: 100%;
    border-radius: 30px;
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
    background-color: var(--dark-gray-pink);
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    pointer-events: auto;
    z-index: 9999;
    box-shadow: -2px 0 5px rgba(0, 0, 0, 0.2);
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

h1 {
    color: white;
}

.icon {
    width: 30px;
    height: 30px;
    color: #a0a0a0;
}
</style>
