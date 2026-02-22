<script setup lang="ts">
import { reactive } from 'vue'

const emit = defineEmits<{
    (
        e: 'create',
        payload: {
            name: string
            description: string
            deadline: string
            members: string[]
        }
    ): void
}>()

const form = reactive({
    name: '',
    description: '',
    deadline: '',
    members: [] as string[],
    newMember: ''
})

function addMember(): void {
    const name = form.newMember.trim()
    if (name && !form.members.includes(name)) {
        form.members.push(name)
    }
    form.newMember = ''
}

function removeMember(member: string): void {
    const idx = form.members.indexOf(member)
    if (idx !== -1) form.members.splice(idx, 1)
}

function submit(): void {
    if (!form.name) return

    emit('create', {
        name: form.name,
        description: form.description,
        deadline: form.deadline,
        members: [...form.members]
    })

    form.name = ''
    form.description = ''
    form.deadline = ''
    form.members = []
    form.newMember = ''
}
</script>

<template>
    <div class="desc-box">
        <h2 class="detail-title">New Feature</h2>
        <input v-model="form.name" class="task-input" type="text" placeholder="Feature name" />
        <textarea
            v-model="form.description"
            class="task-textarea"
            placeholder="Feature description..."
            rows="3"
        ></textarea>
    </div>
    <div class="detail-body">
        <div class="form-row">
            <label class="form-label">Deadline</label>
            <input v-model="form.deadline" class="task-input" type="date" />
        </div>
        <div class="form-row">
            <label class="form-label">Team Members</label>
            <div class="member-input-row">
                <input
                    v-model="form.newMember"
                    class="task-input member-name-input"
                    type="text"
                    placeholder="Member name..."
                    @keyup.enter="addMember"
                />
                <button class="add-member-btn" @click="addMember">+</button>
            </div>
            <div v-if="form.members.length" class="member-list">
                <div
                    v-for="member in form.members"
                    :key="member"
                    class="member-chip member-chip-removable"
                >
                    <img src="/hexagon.svg" alt="icon" class="member-icon" />
                    {{ member }}
                    <button class="remove-member-btn" @click="removeMember(member)">×</button>
                </div>
            </div>
            <div v-else class="detail-value">No members added yet</div>
        </div>
        <button class="create-task-btn" @click="submit">Create Feature</button>
    </div>
</template>

<style scoped>
.desc-box {
    align-self: center;
    width: 80%;
    border-radius: 15px;
    background-color: #ffebba;
    margin-top: 10%;
    padding: 15px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.detail-body {
    align-self: center;
    width: 90%;
    flex: 1;
    border-radius: 15px;
    background-color: #ffebba;
    margin-top: 15px;
    margin-bottom: 20px;
    padding: 15px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.detail-title {
    margin: 0;
    font-size: 20px;
    color: #3a2e0f;
}

.task-input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #cca94e;
    border-radius: 8px;
    background-color: #fff8e7;
    color: black;
    font-family: 'Google Sans Flex';
    font-size: 16px;
    font-weight: bold;
    box-sizing: border-box;
    outline: none;
}
.task-input:focus {
    border-color: #b8860b;
}

.task-textarea {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #cca94e;
    border-radius: 8px;
    background-color: #fff8e7;
    color: black;
    font-family: 'Google Sans Flex';
    font-size: 14px;
    box-sizing: border-box;
    resize: vertical;
    outline: none;
}
.task-textarea:focus {
    border-color: #b8860b;
}

.form-row {
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.form-label {
    font-size: 13px;
    font-weight: bold;
    color: #5a4a1e;
}
.detail-value {
    font-size: 14px;
    color: #4a3d1a;
}

.member-input-row {
    display: flex;
    gap: 8px;
    align-items: center;
}
.member-name-input {
    flex: 1;
}
.add-member-btn {
    width: 36px;
    height: 36px;
    background-color: #d4a030;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 20px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.add-member-btn:hover {
    background-color: #b8860b;
}

.member-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.member-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background-color: #fff8e7;
    border-radius: 10px;
    font-size: 13px;
    color: #3a2e0f;
    font-weight: 500;
}
.member-chip-removable {
    justify-content: space-between;
}
.member-icon {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
}
.remove-member-btn {
    background: none;
    border: none;
    color: #d9534f;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    padding: 0 4px;
    line-height: 1;
}
.remove-member-btn:hover {
    color: #a02020;
}

.create-task-btn {
    margin-top: auto;
    padding: 10px 20px;
    background-color: #d4a030;
    color: white;
    font-family: 'Google Sans Flex';
    font-size: 15px;
    font-weight: bold;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    align-self: center;
    width: 100%;
}
.create-task-btn:hover {
    background-color: #b8860b;
}
</style>
