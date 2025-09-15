import {
  uploadAttachmentApi,
  getAttachmentApi,
  getAttachmentFileApi,
  deleteAttachmentApi,
  updateUserProfileApi
} from '@/api'

// 上传附件
export const uploadAttachment = async (file, description = null) => {
  try {
    const formData = new FormData()
    formData.append('file', file)
    if (description) {
      formData.append('description', description)
    }

    const response = await uploadAttachmentApi(formData)

    if (response.code !== 200) {
      throw new Error(response.message || '上传附件失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 获取附件信息
export const getAttachment = async (attachmentId) => {
  try {
    const response = await getAttachmentApi(attachmentId)

    if (response.code !== 200) {
      throw new Error(response.message || '获取附件信息失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 获取附件文件 /api/v1/attachments/file/{attachment_id}
export const getAttachmentFile = async (attachmentId) => {
  try {
    const response = await getAttachmentFileApi(attachmentId)
    const fileBlob = new Blob([response], { type: 'application/octet-stream' })
    const fileURL = URL.createObjectURL(fileBlob)
    const link = document.createElement('a')
    link.href = fileURL
    link.download = '' // Let the browser decide the filename
    link.click()
    URL.revokeObjectURL(fileURL)
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 删除附件
export const deleteAttachment = async (attachmentId) => {
  try {
    const response = await deleteAttachmentApi(attachmentId)

    if (response.code !== 200) {
      throw new Error(response.message || '删除附件失败')
    }

    return response.data
  } catch (error) {
    throw error.response?.data || error.message
  }
}

// 上传用户头像-> 由 ./auth.js 的 uploadUserAvatar 处理
// export const uploadAvatar = async (file) => {
//   try {
//     // 验证上传文件类型
//     const allowedTypes = [
//       'image/jpeg',
//       'image/jpg',
//       'image/png',
//       'image/gif',
//       'image/webp',
//       'image/bmp'
//     ]

//     if (!allowedTypes.includes(file.type)) {
//       throw new Error('不支持的文件类型，请上传 JPG、PNG、GIF、WebP 或 BMP 格式的图片')
//     }

//     // 验证上传文件大小 (10MB)
//     const maxSize = 10 * 1024 * 1024
//     if (file.size > maxSize) {
//       throw new Error('文件大小不能超过 10MB')
//     }

//     // 上传头像
//     const formData = new FormData()
//     formData.append('file', file)
//     formData.append('description', 'avatar')

//     const attachment = await uploadAttachmentApi(formData)

//     if (attachment.code !== 200) {
//       throw new Error(attachment.message || '上传头像失败')
//     }

//     // 更新用户头像信息
//     const attachmentData = attachment.data

//     const response = await updateUserProfileApi({
//       avatar_attachment_id: attachmentData.attachment_id
//     })

//     return response.data
//   } catch (error) {
//     throw error.response?.data || error.message
//   }
// }
