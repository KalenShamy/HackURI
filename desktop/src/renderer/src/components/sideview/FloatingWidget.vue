<script setup lang="ts"></script>

<template>
    <div class="floating-widget"></div>
</template>

<style scoped>
.floating-widget {
    position: fixed;
    top: 30%;
    right: 0;

    /* Size of the widget */
    width: 50px;
    height: 80px;

    /* Create the semi-circle shape facing left */
    border-top-left-radius: 40px;
    border-bottom-left-radius: 40px;

    /* Dark, semi-transparent background from the image */
    background-color: rgba(40, 40, 40, 0.8);

    /* Center the icon */
    display: flex;
    justify-content: center;
    align-items: center;

    cursor: pointer;
    /* Ensure it's always on top of other content */
    z-index: 9999;

    /* Add padding to offset the icon from the edge */
    padding-right: 5px;

    /* A subtle shadow for depth */
    box-shadow: -2px 0 5px rgba(0, 0, 0, 0.2);

    /* Smooth transition for all changing properties */
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* Style for the arrow icon */
.icon {
    width: 24px;
    height: 24px;
    /* Light gray color for the initial state */
    color: #a0a0a0;
    /* Smooth transition for the icon's rotation and color */
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}
</style>
