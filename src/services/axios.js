import axios from 'axios';

const api = axios.create({
    baseURL: 'https://arxiv.py00.top/api/',
    // baseURL: 'http://127.0.0.1:54025/api/',
    timeout: 5000,
    headers: {
        'Content-Type': 'application/json',
    }
});

api.interceptors.request.use(config => {
    const token = localStorage.getItem('authToken');
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
});

api.interceptors.response.use(response => {
    return response.data;
}, error => {
    console.log(error);
    const errorResponse = error.response ? error.response.data : error.message;
    return Promise.reject(errorResponse);
});

export default api;
