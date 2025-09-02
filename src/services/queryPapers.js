import api from '@/services/axios.js';
import {ElMessage} from "element-plus";

const baseURL = 'papers/';
const queryPapers = async (page, size, kw, subjects, marks, filters = {}) => {
    try {
        const response = await api.get(baseURL, {
            params: {
                page,
                page_size: size,
                search: kw,
                subjects: subjects,
                marks: marks,
                ...filters
            },
        })
        return response
    } catch (error) {
        ElMessage.error({
            message: "Query papers: " + error,
        })
        return {total: 0, items: []}
    }
}


const getPaperDetail = async (doi) => {
    try {
        const response = await api.get(
            `/papers/${encodeURIComponent(doi)}`,
            {
                params: {
                    marks: true
                }
            }
        )
        return response
    } catch (error) {
        ElMessage.error({
            message: "Get paper detail: " + error,
        })
        return null
    }
}


export {queryPapers, getPaperDetail};