import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'login',
      component: () => import('@renderer/pages/LoginPage.vue')
    },
    {
      path: '/workspaces',
      name: 'workspaces',
      component: () => import('@renderer/pages/WorkspacesPage.vue')
    },
    {
      path: '/workspace/:id',
      name: 'workspace',
      component: () => import('@renderer/pages/WorkspacePage.vue')
    }
  ]
})

export default router
