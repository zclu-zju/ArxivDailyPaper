import api from '@/services/axios.js';
import {ElMessage} from "element-plus";

const baseURL = 'papers/mark/';

const updateMarkField = (doi, field, value) => {
    api.patch(`/marks/${doi}`, null, {
        params: {field, value}
    }).then(() => {
        if (field === 'note') {
            ElMessage.success(`doi:${doi} Updated ${field} Successfully!`)
        } else {
            ElMessage.success(`doi:${doi} Updated ${field} = ${value}`)
        }
    }).catch(err => {
        ElMessage.error("Update failed: " + err)
    })
}

const updateNote = (doi, value) => {
    api.post(`/marks/${doi}`, {
        note: value,
    }, {
        params: {
            field: 'note'
        }
    }).then(() => {
        ElMessage.success(`doi:${doi} Updated Note Successfully!`)
    }).catch(err => {
        ElMessage.error("Update failed: " + err)
    })
}
export {updateMarkField, updateNote}
