import { app, shell, BrowserWindow, ipcMain, globalShortcut, screen } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import { exec } from 'child_process'
import { promisify } from 'util'
import fs from 'fs'

// WORKAROUND: For persistent "Access Denied" cache errors on startup.
// This moves the user data directory to a new location to circumvent
// potential permission issues or antivirus locks on the default directory.
// This must be called before the 'ready' event.
try {
  const newPath = join(app.getPath('userData'), '..', `${app.getName()}-data`)
  app.setPath('userData', newPath)
  console.log(`Switched userData path to: ${newPath}`)
} catch (error) {
  console.error('Failed to set new userData path:', error)
}

const execAsync = promisify(exec)

// 停止后台的backend进程
async function stopBackendProcess(): Promise<void> {
  try {
    console.log('Checking for running backend processes...')

    // 检查端口8000是否有进程在监听
    const checkCommand = 'netstat -ano | findstr :8000'
    const { stdout } = await execAsync(checkCommand)

    if (stdout.trim()) {
      // 找到进程ID
      const lines = stdout.trim().split('\n')
      for (const line of lines) {
        const parts = line.trim().split(/\s+/)
        if (parts.length >= 5) {
          const pid = parts[4]
          console.log(`Found process ${pid} listening on port 8000`)

          // 杀死进程
          try {
            await execAsync(`taskkill /PID ${pid} /T /F`)
            console.log(`Successfully killed backend process ${pid}`)
          } catch (killError) {
            console.warn(`Failed to kill process ${pid}:`, killError)
          }
        }
      }
    } else {
      console.log('No backend process found on port 8000')
    }
  } catch (error) {
    console.warn('Error while checking/stopping backend process:', error)
  }
}

let mainWindow: BrowserWindow | null = null
let quickWindow: BrowserWindow | null = null
let isCapturingUrl = false // Add a flag to track capture state

interface BrowserInfo {
  success: boolean
  browser: string
  hasBrowser: boolean
  windowTitle: string
  error?: string
}

interface CaptureUrlResult {
  success: boolean
  url?: string
  error?: string
}

function createWindow(): void {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    minWidth: 800,
    minHeight: 600,
    show: false,
    center: true,
    autoHideMenuBar: true,
    resizable: true,
    maximizable: true,
    fullscreenable: false,
    title: 'Memora',
    titleBarStyle: process.platform === 'darwin' ? 'default' : 'default',
    icon: join(__dirname, '../../resources/icon-L.png'),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false,
      contextIsolation: true
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow?.show()
    console.log('Main window shown')
  })

  mainWindow.on('closed', () => {
    console.log('Main window closed')
    // 关闭小窗进程
    if (quickWindow && !quickWindow.isDestroyed()) {
      quickWindow.destroy()
      quickWindow = null
    }
    // 在非macOS平台上，强制退出应用以避免残留进程
    if (process.platform !== 'darwin') {
      app.quit()
    }
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

// 调整 createQuickWindow 函数，确保窗口尺寸一致
function createQuickWindow(): BrowserWindow | null {
  try {
    console.log('Creating quick window...')

    const primaryDisplay = screen.getPrimaryDisplay()
    const { workAreaSize } = primaryDisplay
    const windowWidth = 320
    const windowHeight = 480 // 统一窗口高度

    quickWindow = new BrowserWindow({
      width: windowWidth,
      height: windowHeight,
      x: workAreaSize.width - windowWidth - 20,
      y: workAreaSize.height - windowHeight - 20,
      show: false,
      frame: false,
      alwaysOnTop: true,
      skipTaskbar: true,
      resizable: false,
      backgroundColor: '#fff',
      hasShadow: false,
      icon: join(__dirname, '../../resources/icon.png'),
      webPreferences: {
        preload: join(__dirname, '../preload/index.js'),
        sandbox: false,
        contextIsolation: true,
        nodeIntegration: false
      }
    })

    console.log('Quick window created')

    // 设置窗口失去焦点时隐藏
    quickWindow.on('blur', () => {
      console.log('Quick window lost focus')
      if (quickWindow && !quickWindow.webContents.isDevToolsOpened() && !isCapturingUrl) {
        quickWindow.hide()
      }
    })

    // 在窗口级别处理F11事件，阻止全屏但允许彩蛋功能
    quickWindow.webContents.on('before-input-event', (event, input) => {
      if (input.key === 'F11') {
        event.preventDefault()
        // 这里可以添加彩蛋功能的代码
        console.log('F11 pressed - Easter egg trigger!')
      }
    })

    quickWindow.on('ready-to-show', () => {
      console.log('Quick window ready to show')
    })

    quickWindow.on('show', () => {
      console.log('Quick window shown')
    })

    quickWindow.on('hide', () => {
      console.log('Quick window hidden')
    })

    quickWindow.on('closed', () => {
      console.log('Quick window closed')
      quickWindow = null
    })

    // 加载快速窗口内容
    const quickUrl =
      is.dev && process.env['ELECTRON_RENDERER_URL']
        ? `${process.env['ELECTRON_RENDERER_URL']}#/quick`
        : `file://${join(__dirname, '../renderer/index.html')}#/quick`

    console.log('Loading quick window URL:', quickUrl)

    quickWindow
      .loadURL(quickUrl)
      .then(() => {
        console.log('Quick window loaded successfully')
      })
      .catch((error) => {
        console.error('Failed to load quick window:', error)
      })

    return quickWindow
  } catch (error) {
    console.error('Error creating quick window:', error)
    return null
  }
}

async function toggleQuickWindow(): Promise<void> {
  try {
    if (quickWindow && quickWindow.isVisible()) {
      quickWindow.hide()
      return
    }

    // 1. Ensure window exists
    if (!quickWindow) {
      createQuickWindow()
      // Wait for the window to be ready to receive messages
      await new Promise<void>((resolve) => {
        const checkWindow = () => {
          if (quickWindow && quickWindow.webContents) {
            resolve()
          } else {
            setTimeout(checkWindow, 100)
          }
        }
        checkWindow()
      })
    }

    if (!quickWindow) {
      console.error('Failed to create or find the quick window.')
      return
    }

    // 2. Show window immediately
    const { workAreaSize } = screen.getPrimaryDisplay()
    const windowWidth = 320
    const windowHeight = 480
    quickWindow.setSize(windowWidth, windowHeight)
    const newX = workAreaSize.width - windowWidth - 20
    const newY = workAreaSize.height - windowHeight - 20
    quickWindow.setPosition(newX, newY)

    quickWindow.show()
    quickWindow.focus()

    // 3. Asynchronously detect browser and send result
    // Wait a bit for the Vue component to mount
    setTimeout(() => {
      // Notify renderer that detection is starting
      if (quickWindow && !quickWindow.isDestroyed()) {
        quickWindow.webContents.send('browser-detection-start')
      }

      // Set a fallback timeout to ensure detection doesn't hang indefinitely
      const detectionTimeout = setTimeout(() => {
        if (quickWindow && !quickWindow.isDestroyed()) {
          quickWindow.webContents.send('browser-detected', {
            success: false,
            browser: 'TIMEOUT',
            hasBrowser: false,
            windowTitle: '',
            error: 'Detection timed out'
          })
        }
      }, 5000)

      detectActiveBrowser()
        .then((browserInfo) => {
          clearTimeout(detectionTimeout)
          if (quickWindow && !quickWindow.isDestroyed()) {
            quickWindow.webContents.send('browser-detected', browserInfo)
          }
        })
        .catch((error) => {
          clearTimeout(detectionTimeout)
          console.error('Browser detection failed:', error)
          if (quickWindow && !quickWindow.isDestroyed()) {
            quickWindow.webContents.send('browser-detected', {
              success: false,
              browser: 'ERROR',
              hasBrowser: false,
              windowTitle: '',
              error: error.message
            })
          }
        })
    }, 500) // Wait 500ms for Vue component to mount
  } catch (error) {
    console.error('Error in toggleQuickWindow:', error)
  }
}

// 检测前台是否有浏览器窗口的函数
async function detectActiveBrowser(): Promise<BrowserInfo> {
  try {
    console.log('=== BROWSER DETECTION START ===')

    // Try PowerShell method first
    try {
      // Use app's userData directory for temporary scripts (writable in production)
      const userDataDir = app.getPath('userData')
      const scriptPath = join(userDataDir, 'detect_browser.ps1')

      const psScript = `
# Simplified Browser Detection Script
$ErrorActionPreference = 'SilentlyContinue'

Write-Host 'Starting browser detection...' -ForegroundColor Yellow

try {
    # Get all browser processes with main window titles
    $browserNames = @('msedge', 'chrome', 'firefox', 'opera', 'brave', 'vivaldi', 'iexplore')
    Write-Host 'Looking for browser processes...' -ForegroundColor Green

    $browsers = Get-Process | Where-Object {
        $_.ProcessName.ToLower() -in $browserNames -and
        $_.MainWindowTitle -and
        $_.MainWindowTitle.Trim() -ne ''
    }

    Write-Host "Found $($browsers.Count) browser processes with windows" -ForegroundColor Green

    if ($browsers) {
        # Get the first browser with a window title (simplify selection)
        $activeBrowser = $browsers | Select-Object -First 1
        Write-Host "Selected browser: $($activeBrowser.ProcessName)" -ForegroundColor Green

        if ($activeBrowser.MainWindowTitle) {
            $output = 'SUCCESS:' + $activeBrowser.ProcessName.ToLower() + ':' + $activeBrowser.MainWindowTitle
            Write-Host "Returning: $output" -ForegroundColor Green
            Write-Output $output
        } else {
            $output = 'SUCCESS:' + $activeBrowser.ProcessName.ToLower() + ':'
            Write-Host "Returning: $output" -ForegroundColor Green
            Write-Output $output
        }
    } else {
        Write-Host 'No browser windows found' -ForegroundColor Yellow
        Write-Output 'NO_BROWSER:unknown:'
    }
} catch {
    $errorMsg = 'ERROR:' + $_.Exception.Message
    Write-Host "Error occurred: $errorMsg" -ForegroundColor Red
    Write-Output $errorMsg
}

Write-Host 'Browser detection completed.' -ForegroundColor Yellow`

      // Try to write and execute the script, but handle file locking gracefully
      let scriptExecuted = false
      let scriptPathUsed = ''
      try {
        // Ensure directory exists
        const userDataDir = app.getPath('userData')
        if (!fs.existsSync(userDataDir)) {
          fs.mkdirSync(userDataDir, { recursive: true })
        }

        const scriptPath = join(userDataDir, 'detect_browser.ps1')
        scriptPathUsed = scriptPath

        fs.writeFileSync(scriptPath, psScript, 'utf8')
        scriptExecuted = true
        console.log('PowerShell script written successfully')
      } catch (writeError) {
        console.warn('Failed to write PowerShell script file, trying inline execution:', writeError)
        // Fall back to inline execution if file write fails
      }

      let stdout: string, stderr: string
      if (scriptExecuted && scriptPathUsed) {
        console.log('Executing PowerShell script from file...')
        console.log('Script path:', scriptPathUsed)

        // Use double quotes around the path to handle spaces
        const command = `powershell.exe -ExecutionPolicy Bypass -File "${scriptPathUsed}"`
        console.log('Executing command:', command)

        const result = await execAsync(command, {
          encoding: 'utf8',
          timeout: 10000,
          windowsHide: true
        })
        stdout = result.stdout
        stderr = result.stderr
        console.log('PowerShell file execution completed')

        // Clean up temporary file after a short delay to ensure execution is complete
        setTimeout(() => {
          try {
            if (fs.existsSync(scriptPathUsed)) {
              fs.unlinkSync(scriptPathUsed)
              console.log('Cleaned up script file:', scriptPathUsed)
            }
          } catch (e) {
            console.warn('Failed to clean up script file:', e)
          }
        }, 1000)
      } else {
        // Execute PowerShell script inline
        console.log('Executing PowerShell script inline...')
        const result = await execAsync(
          `powershell.exe -ExecutionPolicy Bypass -Command "${psScript.replace(/"/g, '""')}"`,
          {
            encoding: 'utf8',
            timeout: 10000,
            windowsHide: true
          }
        )
        stdout = result.stdout
        stderr = result.stderr
        console.log('PowerShell inline execution completed')
      }

      if (stderr) {
        console.warn('Browser detection stderr:', stderr)
      }

      const output = stdout.trim()
      console.log('=== PowerShell RAW OUTPUT ===')
      console.log('STDOUT:', JSON.stringify(stdout))
      console.log('STDERR:', JSON.stringify(stderr))
      console.log('TRIMMED OUTPUT:', JSON.stringify(output))
      console.log('=== END RAW OUTPUT ===')

      // Handle multi-line output by looking for our expected patterns
      const lines = output
        .split('\n')
        .map((line) => line.trim())
        .filter((line) => line.length > 0)
      const lastLine = lines[lines.length - 1] || ''

      console.log('=== OUTPUT PARSING ===')
      console.log('Lines:', lines)
      console.log('Last line:', JSON.stringify(lastLine))
      console.log('=== END PARSING ===')

      // Look for SUCCESS line in the output
      const successLine = lines.find((line) => line.startsWith('SUCCESS:'))

      if (successLine) {
        const parts = successLine.split(':')
        const browser = parts[1] || 'UNKNOWN'
        const windowTitle = parts.slice(2).join(':') || ''

        console.log('SUCCESS detected - Browser:', browser, 'Title:', windowTitle)
        console.log('Full success line:', JSON.stringify(successLine))

        return {
          success: true,
          browser: browser.toUpperCase(),
          hasBrowser: true,
          windowTitle: windowTitle
        }
      } else {
        console.log('No SUCCESS line found in output')
        console.log('Looking for other patterns...')

        if (lastLine === 'ERROR:AddType failed') {
          return {
            success: true,
            browser: 'NONE',
            hasBrowser: false,
            windowTitle: 'Browser detection unavailable'
          }
        } else if (lastLine.startsWith('ERROR:')) {
          return {
            success: true,
            browser: 'NONE',
            hasBrowser: false,
            windowTitle: 'Detection error: ' + lastLine.substring(6)
          }
        } else if (lastLine.startsWith('NO_BROWSER:')) {
          console.log('NO_BROWSER detected')
          return {
            success: true,
            browser: 'NONE',
            hasBrowser: false,
            windowTitle: 'No browser windows found'
          }
        } else if (lastLine === 'ELECTRON_WINDOW') {
          console.log('ELECTRON_WINDOW detected')
          return {
            success: true,
            browser: 'NONE',
            hasBrowser: false,
            windowTitle: 'Only Electron app running'
          }
        } else {
          console.error('Unexpected PowerShell output:', JSON.stringify(output))
          return {
            success: true,
            browser: 'NONE',
            hasBrowser: false,
            windowTitle: 'Unexpected detection result'
          }
        }
      }
    } catch (psError) {
      console.error('=== PowerShell method failed ===')
      console.error('Error:', psError)
      console.error('Error message:', psError instanceof Error ? psError.message : String(psError))
      console.error('=== End PowerShell error ===')

      // Fallback: Check if any browser processes are running
      try {
        const { stdout } = await execAsync(
          'tasklist /FI "IMAGENAME eq msedge.exe" /FI "IMAGENAME eq chrome.exe" /FI "IMAGENAME eq firefox.exe" /NH',
          { timeout: 3000, windowsHide: true }
        )

        if (stdout && stdout.includes('.exe')) {
          return {
            success: true,
            browser: 'DETECTED',
            hasBrowser: true,
            windowTitle: 'Browser process found'
          }
        } else {
          return {
            success: true,
            browser: 'NONE',
            hasBrowser: false,
            windowTitle: 'No browser processes'
          }
        }
      } catch (fallbackError) {
        console.error('Fallback detection failed:', fallbackError)
        throw psError
      }
    }
  } catch (error) {
    console.error('Error detecting browser:', error)
    return {
      success: false,
      browser: 'NONE',
      hasBrowser: false,
      windowTitle: '',
      error: error instanceof Error ? error.message : String(error)
    }
  }
}

// 获取活跃浏览器当前网页链接的函数
async function captureBrowserUrl(): Promise<CaptureUrlResult> {
  try {
    console.log('Attempting to capture browser URL using Win32 API...')

    // This script now finds the foreground browser on its own,
    // so no need to call detectActiveBrowser() here first.
    // Use app's userData directory for temporary scripts (writable in production)
    const userDataDir = app.getPath('userData')
    const scriptPath = join(userDataDir, 'capture_url.ps1')

    // 通用浏览器URL抓取脚本
    const psScript = `
# Universal Browser URL Capture Script
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
using System.Text;

public class BrowserCapture {
    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    [DllImport("user32.dll")]
    public static extern int GetWindowTextLength(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
}
'@

# Browser process names to look for
$browserProcesses = @("msedge", "chrome", "firefox", "opera", "brave", "vivaldi", "iexplore")

# Global variables
$browserWindows = @()
$currentForegroundWindow = [BrowserCapture]::GetForegroundWindow()

# Callback function for EnumWindows
$enumCallback = {
    param($hWnd, $lParam)

    if ([BrowserCapture]::IsWindowVisible($hWnd)) {
        $processId = 0
        [BrowserCapture]::GetWindowThreadProcessId($hWnd, [ref]$processId)

        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($process -and $process.ProcessName.ToLower() -in $browserProcesses) {
            $titleLength = [BrowserCapture]::GetWindowTextLength($hWnd)
            if ($titleLength -gt 0) {
                $title = New-Object System.Text.StringBuilder($titleLength + 1)
                [BrowserCapture]::GetWindowText($hWnd, $title, $title.Capacity)

                $windowInfo = @{
                    Handle = $hWnd
                    Title = $title.ToString()
                    ProcessId = $processId
                    ProcessName = $process.ProcessName.ToLower()
                }
                $script:browserWindows += $windowInfo
            }
        }
    }
    return $true
}

try {
    # Check if any browser is running
    $runningBrowsers = Get-Process -Name $browserProcesses -ErrorAction SilentlyContinue
    if (-not $runningBrowsers) {
        Write-Output "ERROR:No browser processes running"
        exit
    }

    # Enumerate all browser windows
    [BrowserCapture]::EnumWindows($enumCallback, [IntPtr]::Zero)

    if ($browserWindows.Count -eq 0) {
        Write-Output "ERROR:No browser windows found"
        exit
    }

    # Find the best browser window (prefer foreground or first visible)
    $targetWindow = $null
    foreach ($window in $browserWindows) {
        if ($window.Handle -eq $currentForegroundWindow) {
            $targetWindow = $window
            break
        }
    }

    if (-not $targetWindow) {
        # Use the first browser window if no foreground match
        $targetWindow = $browserWindows[0]
    }

    Write-Host "Found browser window: $($targetWindow.ProcessName) - $($targetWindow.Title)" -ForegroundColor Green

    # Bring the target window to foreground
    [BrowserCapture]::SetForegroundWindow($targetWindow.Handle)
    Start-Sleep -Milliseconds 500

    # Backup clipboard
    $originalClipboard = ""
    try {
        $originalClipboard = Get-Clipboard -ErrorAction SilentlyContinue
    } catch {}

    # Clear clipboard
    try {
        Set-Clipboard -Value "" -ErrorAction SilentlyContinue
    } catch {}
    Start-Sleep -Milliseconds 200

    # Send keys to copy URL
    Add-Type -AssemblyName System.Windows.Forms

    # Different key combinations for different browsers
    switch ($targetWindow.ProcessName) {
        "firefox" {
            # Firefox might need different approach
            [System.Windows.Forms.SendKeys]::SendWait("^l")
            Start-Sleep -Milliseconds 600
            [System.Windows.Forms.SendKeys]::SendWait("^c")
            Start-Sleep -Milliseconds 600
        }
        default {
            # Standard approach for Chrome-based browsers (Edge, Chrome, etc.)
            [System.Windows.Forms.SendKeys]::SendWait("^l")
            Start-Sleep -Milliseconds 500
            [System.Windows.Forms.SendKeys]::SendWait("^c")
            Start-Sleep -Milliseconds 500
        }
    }

    # Get URL from clipboard
    $capturedUrl = ""
    try {
        $capturedUrl = Get-Clipboard -ErrorAction SilentlyContinue
    } catch {}

    # Restore clipboard
    try {
        if ($originalClipboard) {
            Set-Clipboard -Value $originalClipboard -ErrorAction SilentlyContinue
        }
    } catch {}

    # Restore original foreground window
    [BrowserCapture]::SetForegroundWindow($currentForegroundWindow)

    # Output result
    if ($capturedUrl -and ($capturedUrl.StartsWith("http://") -or $capturedUrl.StartsWith("https://"))) {
        Write-Output $capturedUrl.Trim()
    } else {
        Write-Output "ERROR:No valid URL captured from $($targetWindow.ProcessName) - got: $capturedUrl"
    }

} catch {
    Write-Output "ERROR:Script execution failed - $($_.Exception.Message)"
}
`

    // 写入临时脚本文件
    let scriptExecuted = false
    try {
      fs.writeFileSync(scriptPath, psScript, 'utf8')
      scriptExecuted = true
    } catch (writeError) {
      console.warn('Failed to write PowerShell script file, trying inline execution:', writeError)
      // Fall back to inline execution if file write fails
    }

    console.log('Executing browser URL capture script...')

    // 执行脚本
    let stdout: string, stderr: string
    if (scriptExecuted) {
      const result = await execAsync(
        `powershell.exe -ExecutionPolicy Bypass -File "${scriptPath}"`,
        {
          encoding: 'utf8',
          timeout: 12000,
          windowsHide: true
        }
      )
      stdout = result.stdout
      stderr = result.stderr

      // 清理临时文件
      try {
        fs.unlinkSync(scriptPath)
      } catch (e) {
        console.warn('Failed to clean up script file:', e)
      }
    } else {
      // Execute PowerShell script inline
      const result = await execAsync(
        `powershell.exe -ExecutionPolicy Bypass -Command "${psScript.replace(/"/g, '""')}"`,
        {
          encoding: 'utf8',
          timeout: 12000,
          windowsHide: true
        }
      )
      stdout = result.stdout
      stderr = result.stderr
    }

    console.log('Browser capture output:', JSON.stringify(stdout))
    console.log('Browser capture error:', JSON.stringify(stderr))

    const lines = stdout
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0)

    // 找到 URL 行
    for (const line of lines) {
      if (line.startsWith('http://') || line.startsWith('https://')) {
        return {
          success: true,
          url: line
        }
      } else if (line.startsWith('ERROR:')) {
        throw new Error(line.substring(6))
      }
    }

    throw new Error('No valid URL found in output')
  } catch (error) {
    console.error('Error capturing browser URL:', error)

    // 用户友好的错误消息
    let errorMessage = error instanceof Error ? error.message : String(error)

    if (errorMessage.includes('No browser processes running')) {
      errorMessage = 'No browser is currently running'
    } else if (errorMessage.includes('No browser windows found')) {
      errorMessage = 'No browser windows are currently open'
    } else if (errorMessage.includes('No valid URL captured')) {
      errorMessage = 'Could not capture URL from the current browser tab'
    } else if (errorMessage.includes('timeout')) {
      errorMessage = 'URL capture timed out - please try again'
    }

    return {
      success: false,
      error: errorMessage
    }
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  console.log('App ready, setting up...')

  // Set app user model id for windows
  electronApp.setAppUserModelId('com.memora.app')

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // 注意：不在这里注册全局F11快捷键，避免影响其他应用
  // 只在窗口级别禁用全屏功能即可

  // 注册全局快捷键 - Windows 使用 Ctrl+Space，macOS 使用 Cmd+Space
  console.log('Registering global shortcuts...')

  const shortcutKey = process.platform === 'darwin' ? 'Cmd+K' : 'Ctrl+Space'
  console.log('Attempting to register:', shortcutKey)

  const ret = globalShortcut.register(shortcutKey, () => {
    console.log(`Global shortcut triggered: ${shortcutKey}`)
    toggleQuickWindow()
  })

  if (ret) {
    console.log(`Global shortcut ${shortcutKey} registered successfully`)
  } else {
    console.log(`Failed to register ${shortcutKey}, trying Alt+Space`)
    const altRet = globalShortcut.register('Alt+Space', () => {
      console.log('Alt+Space shortcut triggered')
      toggleQuickWindow()
    })

    if (altRet) {
      console.log('Alt+Space registered successfully')
    } else {
      console.error('Failed to register any global shortcut')
    }
  }

  // 检查快捷键是否注册成功
  const isRegistered =
    globalShortcut.isRegistered(shortcutKey) || globalShortcut.isRegistered('Alt+Space')
  console.log('Global shortcut registered:', isRegistered)

  // IPC handlers
  ipcMain.on('ping', () => console.log('pong'))

  ipcMain.handle('show-main-window', () => {
    console.log('IPC: show-main-window called')
    try {
      if (!mainWindow) {
        createWindow()
      } else {
        mainWindow.show()
        mainWindow.focus()
      }
      return { success: true }
    } catch (error) {
      console.error('Error showing main window:', error)
      return { success: false, error: error instanceof Error ? error.message : String(error) }
    }
  })

  ipcMain.handle('hide-quick-window', () => {
    console.log('IPC: hide-quick-window called')
    try {
      if (quickWindow && quickWindow.isVisible()) {
        quickWindow.hide()
      }
      return { success: true }
    } catch (error) {
      console.error('Error hiding quick window:', error)
      return { success: false, error: error instanceof Error ? error.message : String(error) }
    }
  })

  // 添加测试用的 IPC 处理器
  ipcMain.handle('test-quick-window', () => {
    console.log('IPC: test-quick-window called')
    toggleQuickWindow()
    return { success: true }
  })

  // 添加获取浏览器 URL 的 IPC 处理器
  ipcMain.handle('capture-edge-url', async () => {
    console.log('IPC: capture-browser-url called')
    return await captureBrowserUrl()
  })

  // 添加新的 IPC handlers
  ipcMain.on('capture-url-start', () => {
    console.log('IPC: capture-url-start received')
    isCapturingUrl = true
    if (quickWindow) {
      quickWindow.setAlwaysOnTop(true)
    }
  })

  ipcMain.on('capture-url-end', () => {
    console.log('IPC: capture-url-end received')
    isCapturingUrl = false
    if (quickWindow) {
      quickWindow.setAlwaysOnTop(true)
    }
  })

  // 添加浏览器检测的 IPC 处理器
  ipcMain.handle('detect-active-browser', async () => {
    console.log('IPC: detect-active-browser called')
    return await detectActiveBrowser()
  })

  // 添加打开外部链接的 IPC 处理器
  ipcMain.handle('open-external-url', async (_event, url: string) => {
    console.log('IPC: open-external-url called with URL:', url)
    try {
      await shell.openExternal(url)
      return { success: true }
    } catch (error) {
      console.error('Error opening external URL:', error)
      return { success: false, error: error instanceof Error ? error.message : String(error) }
    }
  })

  createWindow()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('will-quit', () => {
  // 注销所有全局快捷键
  console.log('Unregistering all global shortcuts')
  globalShortcut.unregisterAll()

  // 关闭小窗进程
  if (quickWindow && !quickWindow.isDestroyed()) {
    console.log('Closing quick window')
    quickWindow.destroy()
    quickWindow = null
  }

  // 停止后台的backend进程
  stopBackendProcess()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
