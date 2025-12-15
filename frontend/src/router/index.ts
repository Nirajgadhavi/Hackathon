import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import CaseDetail from '@/views/CaseDetail.vue'
import Metrics from '@/views/Metrics.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard,
    },
    {
      path: '/case/:id',
      name: 'case-detail',
      component: CaseDetail,
      props: true,
    },
    {
      path: '/metrics',
      name: 'metrics',
      component: Metrics,
    },
  ],
})

export default router
