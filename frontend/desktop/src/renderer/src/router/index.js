import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CollectionListView from '../views/CollectionListView.vue'
import CollectionDetailView from '../views/CollectionDetailView.vue'
import CollectionAttachmentListView from '../views/CollectionAttachmentListView.vue'
import CollectionAttachmentDetailView from '../views/CollectionAttachmentDetailView.vue'
import CommunityView from '../views/CommunityView.vue'
import LoginView from '../views/LoginView.vue'
import ProfileView from '../views/ProfileView.vue'

const routes = [
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
