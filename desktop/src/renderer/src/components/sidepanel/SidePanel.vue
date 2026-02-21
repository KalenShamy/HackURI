<script setup lang="ts">
import { onMounted } from 'vue'

onMounted(() => {
    const invisbox = document.getElementById('invisbox')!

    invisbox.addEventListener('mouseenter', () => {
        window.electron.ipcRenderer.send('set-ignore-mouse', false)
    })

    invisbox.addEventListener('mouseleave', () => {
        window.electron.ipcRenderer.send('set-ignore-mouse', true)
    })
})
</script>

<template>
    <div id="invisbox" class="invisible-box">
        <div class="floating-widget">
            <img src="/arrow_back.svg" alt="open arrow" />
        </div>
        <div class="sidemenu"></div>
    </div>
</template>

<style scoped>
.sidemenu {
    background-color: bisque;
}
h1 {
    color: white;
}
.invisible-box {
    position: fixed;
    top: 0;
    right: 0;
    background-color: transparent;
    border: rgb(255, 255, 255);
    border-width: 1px;
    border-style: solid;
    pointer-events: none;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: flex-end;
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

    /* Dark, semi-transparent background from the image */
    background-color: var(--dark-gray-pink);

    /* Center the icon */
    display: flex;
    justify-content: center;
    align-items: center;

    cursor: pointer;
    pointer-events: auto;
    /* Ensure it's always on top of other content */
    z-index: 9999;

    /* Add padding to offset the icon from the edge */
    padding-right: 0px;

    /* A subtle shadow for depth */
    box-shadow: -2px 0 5px rgba(0, 0, 0, 0.2);

    /* Smooth transition for all changing properties */
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* Change icon color when the parent widget is hovered */
.floating-widget:hover .icon {
    color: #ffffff;
}

/* Style for the arrow icon */
.icon {
    width: 30px;
    height: 30px;
    /* Initial color */
    color: #a0a0a0;
    /* Smooth transition for the icon's rotation and color */
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}
</style>
