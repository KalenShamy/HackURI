<script setup lang="ts"></script>

<template>
    <main>
        <div class="whole-box">
            <div id="menu-title">[Insert Team]'s Current Workspace</div>
            <div class="menu-layout">
                <div class="menu-box">
                    <div id="toolbar">
                        <div class="toolbar-boxes">Sort By</div>
                        <div class="toolbar-boxes">Add</div>
                        <div class="toolbar-boxes">Remove</div>
                    </div>
                    <div id="task-label">
                        <details>
                            <summary>Feature #1</summary>
                            <details>
                                <summary>Task #1</summary>
                                <p>Something small enough to escape casual notice.</p>
                            </details>
                            <details>
                                <summary>Task #2</summary>
                                <p>Something small enough to escape casual notice.</p>
                            </details>
                            <details>
                                <summary>Task #3</summary>
                                <p>Something small enough to escape casual notice.</p>
                            </details>
                        </details>
                    </div>
                    <div id="task-label">
                        <details>
                            <summary>Feature #2</summary>
                            <details>
                                <summary>Task #1</summary>
                                <p>Something small enough to escape casual notice.</p>
                            </details>
                            <details>
                                <summary>Task #2</summary>
                                <p>Something small enough to escape casual notice.</p>
                            </details>
                            <details>
                                <summary>Task #3</summary>
                                <p>Something small enough to escape casual notice.</p>
                            </details>
                        </details>
                    </div>
                    <div id="task-label">
                        <details>
                            <summary>Feature #3</summary>
                            <details>
                                <summary>Task #1</summary>
                                <p>Something small enough to escape casual notice.</p>
                            </details>
                            <details>
                                <summary>Task #2</summary>
                                <p>Something small enough to escape casual notice.</p>
                            </details>
                            <details>
                                <summary>Task #3</summary>
                                <p>Something small enough to escape casual notice.</p>
                            </details>
                        </details>
                    </div>
                </div>
                <div class="menu-box">
                    <div id="desc-box"></div>
                    <div id="background-box-2"></div>
                </div>
                <div id="trans" class="menu-box">
                    <div class="menu-box-split">
                        <div id="people" class="people-box">
                            <img src="/star.svg" />
                        </div>
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
details {
    border: 1px solid #aaaaaa;
    padding: 0.5em 0.5em 0;
    background-color: #ffebba;
    color: black;
    width: 90%;
    border-radius: 10px;
}

details > .features {
    border-radius: 15px;
}

summary {
    font-weight: bold;
    margin: -0.5em -0.5em 0;
    padding: 0.5em;
}

details[open] {
    padding: 0.5em;
}
details[open] summary {
    border-bottom: 1px solid #aaaaaa;
    margin-bottom: 0.5em;
}
main {
    background: var(--background-color);
}
.whole-box {
    background-color: #ffebba;
    padding: 20px;
    height: 100vh;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
}
.menu-layout {
    width: calc(100%);
    flex: 1;
    min-height: 0;
    border-radius: 10px;
    align-items: center;
    display: flex;
}
.menu-box {
    height: 100%;
    min-height: 0;
    width: 33%;
    background-color: #e9c17d;
    border-radius: 40px;
    margin: 0.8%;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}

.menu-box-split {
    height: 45%;
    width: 90%;
    background-color: #e9c17d;
    border-radius: 15px;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    gap: 10px;
}
#task-label {
    display: flex;
    flex-direction: column;
    margin-bottom: 20px;
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
    width: 95%;
    height: 70px;
    display: flex;
    text-align: center;
    justify-content: center;
    align-items: center;
    align-self: center;
}
#toolbar .toolbar-boxes {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #ffebba;
    border-radius: 40px;
    width: 65%;
    height: 50px;
    margin: 10px;
    box-sizing: border-box;
    color: black;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
#menu-title {
    text-align: center;
    align-self: flex-start;
    height: 55px;
    width: calc(100% - 50px);
    padding: 20px 25px;
    background-color: #f3bb5b;
    font-size: 40px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    color: black;
}

@media (max-width: 900px) {
    #menu-title {
        height: 35px;
        font-size: 28px;
    }
}

#desc-box {
    align-self: center;
    width: 80%;
    height: 10%;
    border-radius: 15px;
    background-color: #ffebba;
    margin-top: 10%;
}
.item-box {
    display: flex;
    align-self: center;
    width: 80%;
    height: 20%;
    border-radius: 15px;
    background-color: #ffebba;
    align-self: center;
    justify-content: center;
    align-items: center;
    color: black;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.people-box {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 80%;
    height: 10%;
    border-radius: 10px;
    background-color: #ffebba;
    color: black;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
#people {
    margin-top: 28px;
}
#background-box-2 {
    align-self: center;
    width: 90%;
    height: 75%;
    border-radius: 15px;
    background-color: #ffebba;
    margin-top: 30px;
}
</style>
