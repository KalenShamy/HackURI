import { defineStore } from 'pinia'
import { ref } from 'vue'

interface User {
  id: number
  username: string
  email: string
  github_avatar: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(null)
  const githubToken = ref<string | null>(null)
  const user = ref<User | null>(null)

  function setAuth(data: { token: string; github_token: string; user: User }) {
    token.value = data.token
    githubToken.value = data.github_token
    user.value = data.user
  }

  function logout() {
    token.value = null
    githubToken.value = null
    user.value = null
  }

  const isAuthenticated = () => !!token.value

  return { token, githubToken, user, setAuth, logout, isAuthenticated }
})
