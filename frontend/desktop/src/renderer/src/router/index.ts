import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/community',
    name: 'Community',
    component: () => import('../views/CommunityView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/collection',
    children: [
      {
        path: '/collection/:category_id',
        name: 'CollectionList',
        component: () => import('../views/CollectionListView.vue'),
        meta: { requiresAuth: true },
        props: true
      }
      // 以下页面暂不开放
      // {
      //   path: '/collection/:collection_id',
      //   name: 'CollectionDetail',
      //   component: CollectionDetailView,
      //   props: true
      // },
      // {
      //   path: '/attachment/:category_id',
      //   name: 'CollectionAttachmentList',
      //   component: CollectionAttachmentListView,
      //   props: true
      // },
      // {
      //   path: '/attachment/detail/:collection_id',
      //   name: 'CollectionAttachmentDetail',
      //   component: CollectionAttachmentDetailView,
      //   props: true
      // },
      // {
      //   path: '/post/:post_id/collection',
      //   name: 'PostCollectionDetail',
      //   component: PostCollectionDetailView,
      //   props: true
      // },
      // {
      //   path: '/collection/public/:collection_id',
      //   name: 'PublicCollectionDetail',
      //   component: PostCollectionDetailView,
      //   props: true
      // },
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/SettingsView.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach(async (to, from) => {
  const isAuthenticated = !!localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !isAuthenticated && to.name !== 'Login') {
    console.log('未认证用户，重定向到登录页')
    return { name: 'Login' }
  }
  return true
})

export default router
