import api from './api'
import type { ApiResponse, Attachment } from '@/types'

// 上传附件
export const uploadAttachmentApi = async (formData: FormData) => {
  const response: ApiResponse<Attachment> = await api.post(
    '/api/v1/attachments/upload/',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
  )
  return response
}

// 获取附件信息
export const getAttachmentApi = async (attachmentId: string | number) => {
  const response: ApiResponse<Attachment> = await api.get(`/api/v1/attachments/${attachmentId}`)
  return response
}

// 获取附件文件 /api/v1/attachments/file/{attachment_id}
export const getAttachmentFileApi = async (attachmentId: string | number): Promise<Blob> => {
  const response: Blob = await api.get(`/api/v1/attachments/file/${attachmentId}`, {
    responseType: 'blob' // 以二进制流的形式获取文件
  })
  return response
}

// 删除附件
export const deleteAttachmentApi = async (attachmentId: string | number) => {
  const response: null = await api.delete(`/api/v1/attachments/${attachmentId}`)
  return response
}
