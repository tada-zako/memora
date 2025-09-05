import api from './api'

// 上传附件
export const uploadAttachment = async (file, description = null) => {
  try {
    const formData = new FormData()
    formData.append('file', file)
    if (description) {
      formData.append('description', description)
    }

    const response = await api.post('/api/v1/attachments/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 获取附件信息
export const getAttachment = async (attachmentId) => {
  try {
    const response = await api.get(`/api/v1/attachments/${attachmentId}`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 获取附件文件 /api/v1/attachments/file/{attachment_id}
export const getAttachmentFile = async (attachmentId) => {
  try {
    const response = await api.get(`/api/v1/attachments/file/${attachmentId}`, {
      responseType: 'blob' // 以二进制流的形式获取文件
    })
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 删除附件
export const deleteAttachment = async (attachmentId) => {
  try {
    const response = await api.delete(`/api/v1/attachments/${attachmentId}`)
    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 上传头像
export const uploadAvatar = async (file) => {
  try {
    const attachment = await uploadAttachment(file, 'avatar')
    return attachment
  } catch (error) {
    throw error
  }
}
