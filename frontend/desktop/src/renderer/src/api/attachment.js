import api from './api'

// 上传附件
export const uploadAttachmentApi = async (formData) => {
  return await api.post('/api/v1/attachments/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取附件信息
export const getAttachmentApi = async (attachmentId) => {
  return await api.get(`/api/v1/attachments/${attachmentId}`)
}

// 获取附件文件 /api/v1/attachments/file/{attachment_id}
export const getAttachmentFileApi = async (attachmentId) => {
  return await api.get(`/api/v1/attachments/file/${attachmentId}`, {
    responseType: 'blob' // 以二进制流的形式获取文件
  })
}

// 删除附件
export const deleteAttachmentApi = async (attachmentId) => {
  return await api.delete(`/api/v1/attachments/${attachmentId}`)
}
