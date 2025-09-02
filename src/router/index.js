import {createRouter, createWebHistory} from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/paper',
            children: [
                {
                    path: '',
                    name: 'Papers',
                    meta: {
                        title: 'All Papers'
                    },
                    component: () => import("@/views/papersView.vue")
                },
                {
                    path: 'detail/:doi',
                    name: 'PaperDetail',
                    meta: {
                        title: 'Paper Detail'
                    },
                    component: () => import("@/views/paperDetailView.vue")
                }
            ]
        },
        {
            path: '/',
            redirect: '/paper',
            name: 'home'
        },
        {
            path: '/user',
            name: 'User',
            children: [
                {
                    path: 'login',
                    name: 'Login',
                    meta: {
                        title: 'Login',
                    },
                    component: () => import("@/views/loginView.vue")
                }
            ]
        }
    ],
})

router.beforeEach((to, from, next) => {
    document.title = to.meta.title
    next()
})

export default router
