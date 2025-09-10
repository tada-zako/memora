import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CollectionListView from '../views/CollectionListView.vue'
import CollectionDetailView from '../views/CollectionDetailView.vue'
import CollectionAttachmentListView from '../views/CollectionAttachmentListView.vue'
import CollectionAttachmentDetailView from '../views/CollectionAttachmentDetailView.vue'
import CommunityView from '../views/CommunityView.vue'
import PostCollectionDetailView from '../views/PostCollectionDetailView.vue'
import LoginView from '../views/LoginView.vue'
import ProfileView from '../views/ProfileView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/community',
    name: 'Community',
    component: CommunityView
  },
  {
    path: '/collection',
    name: 'CollectionList',
    component: CollectionListView,
    props: true
  },
  {
    path: '/collection/:category_id',
    name: 'CollectionList',
    component: CollectionListView,
    props: true
  },
  {
    path: '/collection/:collection_id',
    name: 'CollectionDetail',
    component: CollectionDetailView,
    props: true
  },
  {
    path: '/attachment/:category_id',
    name: 'CollectionAttachmentList',
    component: CollectionAttachmentListView,
    props: true
  },
  {
    path: '/attachment/detail/:collection_id',
    name: 'CollectionAttachmentDetail',
    component: CollectionAttachmentDetailView,
    props: true
  },
  {
    path: '/post/:post_id/collection',
    name: 'PostCollectionDetail',
    component: PostCollectionDetailView,
    props: true
  },
  {
    path: '/collection/public/:collection_id',
    name: 'PublicCollectionDetail',
    component: PostCollectionDetailView,
    props: true
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
