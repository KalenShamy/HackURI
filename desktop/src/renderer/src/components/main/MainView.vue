<script setup lang="ts"></script>

<template>
    <main>
        <div class="whole-box">
            <div class="menu-title">[Insert Team]'s Current Workspace</div>
            <div id="trans" class="menu-layout">
                <div class="menu-box">
                    <div id="toolbar">
                        <div class="toolbar-boxes">Sort By</div>
                        <div class="toolbar-boxes">Add</div>
                        <div class="toolbar-boxes">Remove</div>
                    </div>
                    <div id="task-label">
                        <div class="box-label">Feature #1</div>
                        <div class="box-label">Feature #2</div>
                        <div class="box-label">Feature #3</div>
                        <div class="box-label">Feature #4</div>
                        <div class="box-label">Feature #5</div>
                    </div>
                </div>
                <div class="menu-box">
                    <div id="desc-box"></div>
                    <div id="background-box-2"></div>
                </div>
                <div id="trans" class="menu-box">
                    <div class="menu-box-split">
                        <div id="people" class="people-box">PEOPLE</div>
                        <div id="people" class="people-box">Hai-bien Nguyen</div>
                        <div class="people-box">Hannah Ritchie</div>
                        <div class="people-box">Paul Fang Li</div>
                        <div class="people-box">Kaylen Shamey</div>
                    </div>
                    <div class="menu-box-split">
                        <div class="item-box">Undo last task</div>
                        <div class="item-box">Past tasks</div>
                        <div class="item-box">Placeholder idk</div>
                    </div>
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

.menu-box-split {
    height: 45%;
    width: 90%;
    background-color: #e9c17d;
    border-radius: 15px;
    margin: 20px;
}
#task-label {
    display: flex;
    flex-direction: column;
    gap: 20px;
    align-items: center;
}
#task-label .box-label {
    width: min(90%, 400px);
    height: 50px;
    background-color: #ffebba;
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
    text-align: center;
    justify-content: center;
    align-items: center;
}
#toolbar .toolbar-boxes {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #ffebba;
    border-radius: 40px;
    width: 80%;
    height: 40%;
    margin: 10px;
    box-sizing: border-box;
    color: black;
}
.menu-title {
    position: absolute;
    text-align: center;
    align-self: flex-start;
    width: 87.5%;
    height: 10%;
    padding: 25px;
    background-color: #f3bb5b;
    border-radius: 40px;
    margin: 20px;
    font-size: 45px;
}

#desc-box {
    align-self: center;
    width: 80%;
    height: 5%;
    border-radius: 15px;
    background-color: #ffebba;
    margin-top: 50px;
}
.item-box {
    display: flex;
    align-self: center;
    width: 80%;
    height: 20%;
    border-radius: 15px;
    background-color: #ffebba;
    margin-left: 40px;
    margin-top: 30px;
    margin-bottom: 30px;
    justify-content: center;
    align-items: center;
    font-size: 24px;
    color: black;
}
.people-box {
    display: flex;
    align-self: center;
    width: 80%;
    height: 10%;
    border-radius: 15px;
    background-color: #ffebba;
    margin-left: 40px;
    margin-top: 20px;
    margin-bottom: 20px;
    justify-content: center;
    align-items: center;
    font-size: 24px;
    color: black;
}
#people {
    margin-top: 28px;
}
#background-box-2 {
    align-self: center;
    width: 75%;
    height: 75%;
    border-radius: 15px;
    background-color: #ffebba;
    margin-top: 55px;
}
</style>
