<script setup lang="ts"></script>

<template>
    <main>
        <div class="whole-box">
            <div class="menu-title"></div>
            <div id="trans" class="menu-layout">
                <div class="menu-box">
                    <div id="toolbar">
                        <div class="toolbar-boxes"></div>
                        <div class="toolbar-boxes"></div>
                        <div class="toolbar-boxes"></div>
                    </div>
                    <div id="task-label">
                        <div class="box-label">Task1</div>
                        <div class="box-label">Task2</div>
                        <div class="box-label">Task3</div>
                        <div class="box-label">Task4</div>
                        <div class="box-label">Task5</div>
                    </div>
                </div>
                <div class="menu-box">
                    <div id="typing-box"></div>
                    <div id="background-box-2"></div>
                </div>
                <div class="menu-box">
                    <div class="menu-box-dos"></div>
                    <div class="menu-box-dos"></div>
                </div>
            </div>
        </div>
    </main>
</template>

<style scoped>
main {
    background: var(--background-color);
}
.whole-box {
    background-color: #ffebba;
    width: 100vw;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: flex-end;
}
#trans {
    background-color: transparent;
}
.menu-layout {
    width: 92.5%;
    height: 80%;
    border-radius: 15px;
    align-items: center;
    display: flex;
}
.menu-box {
    height: 100%;
    width: 33%;
    background-color: #e9c17d;
    border-radius: 40px;
    margin: 20px;
    display: flex;
    flex-direction: column;
}
#task-label {
    display: flex;
    flex-direction: column;
    gap: 12px; /* space between the rows */
    align-items: center;
}

#task-label .box-label {
    width: min(90%, 400px);
    height: 50px;
    background-color: #ffebba; /* make box visible */
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: black;
}

#toolbar {
    background-color: transparent;
    width: 100%;
    height: 20%;
    display: flex;
    justify-content: center;
    align-items: center;
}
#toolbar .toolbar-boxes {
    background-color: #ffebba;
    border-radius: 40px;
    width: 80%;
    height: 50%;
    margin: 10px;
}
.menu-title {
    position: absolute;
    align-self: flex-start;
    width: 92.5%;
    height: 15%;
    background-color: #f3bb5b;
    border-radius: 40px;
    margin: 20px;
}
#typing-box {
    align-self: center;
    width: 80%;
    height: 5%;
    border-radius: 15px;
    background-color: #ffebba;
    margin-top: 50px;
}
#background-box-2 {
    align-self: center;
    width: 75%;
    height: 75%;
    border-radius: 15px;
    background-color: #ffebba;
    margin-top: 55px;
}
#menu-box-dos {
    height: 45%;
    width: 20%;
    background-color: #e9c17d;
    border-radius: 40px;
    margin: 20px;
    display: flex;
    flex-direction: column;
}
</style>
