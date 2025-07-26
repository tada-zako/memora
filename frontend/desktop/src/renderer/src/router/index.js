import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import CollectionListView from '../views/CollectionListView.vue'
import CollectionDetailView from '../views/CollectionDetailView.vue'
import CollectionAttachmentListView from '../views/CollectionAttachmentListView.vue'
import CollectionAttachmentDetailView from '../views/CollectionAttachmentDetailView.vue'
import CommunityView from '../views/CommunityView.vue'

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

]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
