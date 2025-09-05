import { contextBridge, ipcRenderer } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

// Custom APIs for renderer
const api = {
  // 主窗口控制
  showMainWindow: () => ipcRenderer.invoke('show-main-window'),

  // 快速窗口控制
  hideQuickWindow: () => ipcRenderer.invoke('hide-quick-window'),

  // 获取 Edge 浏览器链接
  captureEdgeUrl: () => ipcRenderer.invoke('capture-edge-url'),

  // 检测活跃浏览器
  detectActiveBrowser: () => ipcRenderer.invoke('detect-active-browser'),

  // 获取操作系统信息
  getPlatform: () => process.platform,

  // 其他实用功能
  ping: () => ipcRenderer.send('ping')
}

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI)
    contextBridge.exposeInMainWorld('electronAPI', {
      invoke: (channel, ...args) => ipcRenderer.invoke(channel, ...args),
      send: (channel, ...args) => ipcRenderer.send(channel, ...args),
      on: (channel, func) => ipcRenderer.on(channel, (event, ...args) => func(...args)),
      getPlatform: () => process.platform
    })
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error(error)
  }
} else {
  window.electron = electronAPI
  window.electronAPI = {
    invoke: (channel, ...args) => ipcRenderer.invoke(channel, ...args),
    send: (channel, ...args) => ipcRenderer.send(channel, ...args),
    on: (channel, func) => ipcRenderer.on(channel, (event, ...args) => func(...args)),
    getPlatform: () => process.platform
  }
  window.api = api
}
