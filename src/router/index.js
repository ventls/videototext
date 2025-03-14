import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/market-trading',
      name: 'marketTrading',
      component: () => import('../views/MarketTradingView.vue'),
    },
    {
      path: '/market-sentiment',
      name: 'marketSentiment',
      component: () => import('../views/MarketSentimentView.vue'),
    },
    {
      path: '/my-stocks',
      name: 'myStocks',
      component: () => import('../views/MyStocksView.vue'),
    }
  ],
})

export default router