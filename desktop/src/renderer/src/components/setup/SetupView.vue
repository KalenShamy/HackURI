<script setup lang="ts">
function connectToGithub(): void {
    window.electron.ipcRenderer.send('start-oauth')
}
</script>

<template>
    <main>
        <div class="setup-card">
            <div class="logo-area">
                <img src="/LOGO FLAT.png" alt="Hivemind" class="logo-img" />
            </div>

            <div class="title-pill">Welcome to Hivemind</div>

            <div class="description-box">
                <p>GitHub-integrated task management, powered by AI.</p>
                <ul class="feature-list">
                    <li>Sync tasks with GitHub Issues &amp; PRs</li>
                    <li>AI-powered task prioritization</li>
                    <li>Team coordination in one place</li>
                </ul>
            </div>

            <button class="cta-button" @click="connectToGithub">
                <svg
                    width="20"
                    height="20"
                    viewBox="0 0 98 96"
                    fill="currentColor"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        fill-rule="evenodd"
                        clip-rule="evenodd"
                        d="M48.854 0C21.839 0 0 22 0 49.217c0 21.756 13.993 40.172 33.405 46.69 2.427.49 3.316-1.059 3.316-2.362 0-1.141-.08-5.052-.08-9.127-13.59 2.934-16.42-5.867-16.42-5.867-2.184-5.704-5.42-7.17-5.42-7.17-4.448-3.015.324-3.015.324-3.015 4.934.326 7.523 5.052 7.523 5.052 4.367 7.496 11.404 5.378 14.235 4.074.404-3.178 1.699-5.378 3.074-6.6-10.839-1.141-22.243-5.378-22.243-24.283 0-5.378 1.94-9.778 5.014-13.2-.485-1.222-2.184-6.275.486-13.038 0 0 4.125-1.304 13.426 5.052a46.97 46.97 0 0 1 12.214-1.63c4.125 0 8.33.571 12.213 1.63 9.302-6.356 13.427-5.052 13.427-5.052 2.67 6.763.97 11.816.485 13.038 3.155 3.422 5.015 7.822 5.015 13.2 0 18.905-11.404 23.06-22.324 24.283 1.78 1.548 3.316 4.481 3.316 9.126 0 6.6-.08 11.897-.08 13.526 0 1.304.89 2.853 3.316 2.364 19.412-6.52 33.405-24.935 33.405-46.691C97.707 22 75.788 0 48.854 0z"
                    />
                </svg>
                Connect to GitHub
            </button>

            <p class="footer-hint">Opens GitHub in your browser</p>
        </div>
    </main>
</template>

<style scoped>
main {
    width: 100vw;
    height: 100vh;
    background-color: var(--side-background-biege);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0;
    overflow: hidden;
}

.setup-card {
    width: 520px;
    max-width: calc(100% - 60px);
    background-color: var(--light-beige);
    border-radius: 40px;
    padding: 44px 50px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    box-shadow: 0 8px 32px rgba(37, 33, 31, 0.15);
    animation: cardEntrance 0.6s cubic-bezier(0.25, 0.8, 0.25, 1) both;
}

/* --- Logo area --- */
.logo-area {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 4px;
}

.logo-img {
    width: 100px;
    height: 100px;
    border-radius: 24px;
    object-fit: cover;
}

/* --- Title --- */
.title-pill {
    background-color: var(--textbox-yellow);
    border-radius: 50px;
    padding: 10px 32px;
    font-size: 26px;
    font-weight: 700;
    color: var(--Text-brown);
    text-align: center;
    letter-spacing: -0.3px;
}

/* --- Description --- */
.description-box {
    background-color: var(--whitish-yellow);
    border-radius: 20px;
    padding: 18px 26px;
    width: 100%;
    box-sizing: border-box;
    color: var(--Text-brown);
    font-size: 14px;
    line-height: 1.6;
}

.description-box p {
    margin: 0 0 12px 0;
    font-size: 15px;
    font-weight: 500;
    color: var(--brownish);
}

.feature-list {
    margin: 0;
    padding-left: 0;
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.feature-list li::before {
    content: '\u25C6  ';
    color: var(--pullout-yellow);
    font-size: 10px;
}

/* --- CTA Button --- */
.cta-button {
    background-color: var(--off-black);
    color: var(--off-white);
    border: none;
    border-radius: 50px;
    padding: 14px 36px;
    font-size: 16px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
    letter-spacing: 0.2px;
    box-shadow: 0 4px 14px rgba(37, 33, 31, 0.3);
    margin-top: 4px;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.cta-button:hover {
    background-color: var(--brownish);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(37, 33, 31, 0.35);
}

.cta-button:active {
    transform: translateY(0);
    box-shadow: 0 2px 8px rgba(37, 33, 31, 0.25);
    transition-duration: 0.1s;
}

/* --- Footer --- */
.footer-hint {
    font-size: 12px;
    color: var(--brownish);
    opacity: 0.7;
    margin: 0;
    text-align: center;
}

/* --- Animations --- */
@keyframes cardEntrance {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

</style>
