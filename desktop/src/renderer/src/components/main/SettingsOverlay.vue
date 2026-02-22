<script setup lang="ts">
defineProps<{
    show: boolean
    teamName: string
}>()

defineEmits<{
    (e: 'close'): void
    (e: 'update:teamName', value: string): void
}>()
</script>

<template>
    <div v-if="show" class="settings-overlay" @click.self="$emit('close')">
        <div class="settings-panel">
            <div class="settings-header">
                <span class="settings-title">SETTINGS</span>
                <button class="settings-close-btn" @click="$emit('close')">
                    <img src="/settings.png" alt="Settings" class="settings-header-icon" />
                </button>
            </div>
            <div class="settings-body">
                <div class="settings-section">
                    <label class="settings-label">Team Name</label>
                    <input
                        :value="teamName"
                        class="settings-input"
                        type="text"
                        placeholder="Enter team name"
                        @input="$emit('update:teamName', ($event.target as HTMLInputElement).value)"
                    />
                </div>
                <div class="settings-section">
                    <label class="settings-label">Theme</label>
                    <div class="settings-placeholder">Default (Honey)</div>
                </div>
                <div class="settings-section">
                    <label class="settings-label">GitHub Integration</label>
                    <div class="settings-placeholder">Connected</div>
                </div>
                <div class="settings-section">
                    <label class="settings-label">Slack Integration</label>
                    <div class="settings-placeholder">Not connected</div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.settings-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 100;
    background-color: rgba(0, 0, 0, 0.4);
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    padding: 20px;
}

.settings-panel {
    width: clamp(280px, 30vw, 360px);
    max-height: calc(100vh - 40px);
    background-color: #5a4226;
    border-radius: 20px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.settings-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: clamp(10px, 1.5vw, 16px) clamp(14px, 1.8vw, 20px);
    background-color: #4a3520;
    border-bottom: 2px solid #3a2815;
}

.settings-title {
    font-size: clamp(18px, 2.5vw, 28px);
    font-weight: bold;
    color: #ffebba;
    letter-spacing: 2px;
}

.settings-close-btn {
    background: none;
    border: 2px solid #d4a030;
    border-radius: 50%;
    width: clamp(30px, 3.5vw, 40px);
    height: clamp(30px, 3.5vw, 40px);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
}

.settings-header-icon {
    width: clamp(16px, 2vw, 22px);
    height: clamp(16px, 2vw, 22px);
}

.settings-body {
    padding: clamp(12px, 1.8vw, 20px);
    display: flex;
    flex-direction: column;
    gap: clamp(12px, 1.5vw, 18px);
    overflow-y: auto;
}

.settings-section {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.settings-label {
    font-size: clamp(11px, 1.2vw, 13px);
    font-weight: bold;
    color: #d4a030;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.settings-input {
    width: 100%;
    padding: clamp(6px, 1vw, 10px) clamp(8px, 1.2vw, 12px);
    border: 2px solid #7a5c3a;
    border-radius: 10px;
    background-color: #ffebba;
    color: black;
    font-family: 'Google Sans Flex';
    font-size: clamp(12px, 1.3vw, 14px);
    box-sizing: border-box;
    outline: none;
}
.settings-input:focus {
    border-color: #d4a030;
}

.settings-placeholder {
    padding: clamp(6px, 1vw, 10px) clamp(8px, 1.2vw, 12px);
    border: 2px solid #7a5c3a;
    border-radius: 10px;
    background-color: #ffebba;
    color: #5a4a1e;
    font-size: clamp(12px, 1.3vw, 14px);
}
</style>
