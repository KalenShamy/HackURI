import { app, shell, BrowserWindow, ipcMain, screen } from 'electron'
import { join } from 'path'
import icon from '../../resources/icon.png?asset'

const isDev = !app.isPackaged
import { emptyData, Store, type User } from './data'

let sidePanelWindow: BrowserWindow | null = null
let mainAppWindow: BrowserWindow | null = null
let displayTrackingInterval: ReturnType<typeof setInterval> | null = null
let lastDisplayId: number | null = null
let isQuitting = false

const store = new Store({
    configName: 'Desktop',
    defaults: emptyData
})

function isSetupDone(): boolean {
    return store.get('init')
}

function getActiveDisplay(): Electron.Display {
    const cursorPoint = screen.getCursorScreenPoint()
    return screen.getDisplayNearestPoint(cursorPoint)
}

export function createSidePanel(): void {
    if (!isSetupDone()) return
    if (mainAppWindow && !mainAppWindow.isDestroyed()) {
        mainAppWindow.close()
        mainAppWindow = null
    }
    const activeDisplay = getActiveDisplay()
    const { x, y, width, height } = activeDisplay.workArea
    lastDisplayId = activeDisplay.id

    // Create the browser window.
    const mainWindow = new BrowserWindow({
        x: x + width - 400,
        y: y + Math.floor((height - 800) / 2),
        width: 400,
        height: 800,
        transparent: true,
        frame: true, // no title bar, close/minimize/etc controls
        icon: icon,
        alwaysOnTop: true,
        skipTaskbar: false,
        webPreferences: {
            preload: join(__dirname, '../preload/index.js'),
            sandbox: false
        }
    })

    mainWindow.on('ready-to-show', () => {
        mainWindow.show()
    })

    mainWindow.webContents.setWindowOpenHandler((details) => {
        shell.openExternal(details.url)
        return { action: 'deny' }
    })
    mainWindow.setIgnoreMouseEvents(true, { forward: true })
    mainWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true })
    // HMR mfor renderer base on electron-vite cli.
    // Load the remote URL for development or the local html file for production.
    if (isDev && process.env['ELECTRON_RENDERER_URL']) {
        mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
    } else {
        mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
    }

    mainWindow.webContents.once('did-finish-load', () => {
        mainWindow.webContents.send('set-view', 'sidepanel')
    })

    sidePanelWindow = mainWindow
    mainWindow.on('closed', () => {
        sidePanelWindow = null
        stopDisplayTracking()
    })

    startDisplayTracking()
}

// Polls every 500ms to check if the cursor moved to a different display,
// and snaps the side panel to that display's right edge.
function startDisplayTracking(): void {
    stopDisplayTracking()
    displayTrackingInterval = setInterval(() => {
        if (!sidePanelWindow || sidePanelWindow.isDestroyed()) {
            stopDisplayTracking()
            return
        }
        const activeDisplay = getActiveDisplay()
        // Only reposition when the display actually changed
        if (activeDisplay.id !== lastDisplayId) {
            lastDisplayId = activeDisplay.id
            const { x, y, width, height } = activeDisplay.workArea
            sidePanelWindow.setBounds({
                x: x + width - 400,
                y: y + Math.floor((height - 800) / 2),
                width: 400,
                height: 800
            })
        }
    }, 500)
}

function stopDisplayTracking(): void {
    if (displayTrackingInterval) {
        clearInterval(displayTrackingInterval)
        displayTrackingInterval = null
    }
}

export function createMainWindow(): void {
    if (!isSetupDone()) return
    if (sidePanelWindow && !sidePanelWindow.isDestroyed()) {
        sidePanelWindow.close()
        sidePanelWindow = null
    }
    const activeDisplay = getActiveDisplay()
    const { x, y, width, height } = activeDisplay.workArea

    // Create the browser window.
    const mainWindow = new BrowserWindow({
        x: x + Math.floor((width - 950) / 2),
        y: y + Math.floor((height - 650) / 2),
        width: 950,
        height: 650,
        transparent: false,
        frame: true, // no title bar, close/minimize/etc controls
        icon: icon,
        alwaysOnTop: false,
        skipTaskbar: false,
        webPreferences: {
            preload: join(__dirname, '../preload/index.js'),
            sandbox: false
        }
    })

    mainWindow.on('ready-to-show', () => {
        mainWindow.show()
    })

    mainWindow.webContents.setWindowOpenHandler((details) => {
        shell.openExternal(details.url)
        return { action: 'deny' }
    })
    // HMR mfor renderer base on electron-vite cli.
    // Load the remote URL for development or the local html file for production.
    if (isDev && process.env['ELECTRON_RENDERER_URL']) {
        mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
    } else {
        mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
    }

    mainWindow.webContents.once('did-finish-load', () => {
        mainWindow.webContents.send('set-view', 'main')
    })

    mainAppWindow = mainWindow
    mainWindow.on('closed', () => {
        mainAppWindow = null
        if (!isQuitting) createSidePanel()
    })
}

export function createSetupWindow(): void {
    if (isSetupDone()) return
    if (sidePanelWindow && !sidePanelWindow.isDestroyed()) {
        sidePanelWindow.close()
        sidePanelWindow = null
    }
    if (mainAppWindow && !mainAppWindow.isDestroyed()) {
        mainAppWindow.close()
        mainAppWindow = null
    }
    const activeDisplay = getActiveDisplay()
    const { x, y, width, height } = activeDisplay.workArea

    // Create the browser window.
    const mainWindow = new BrowserWindow({
        x: x + Math.floor((width - 800) / 2),
        y: y + Math.floor((height - 600) / 2),
        width: 800,
        height: 600,
        transparent: false,
        frame: true, // no title bar, close/minimize/etc controls
        icon: icon,
        alwaysOnTop: false,
        skipTaskbar: false,
        webPreferences: {
            preload: join(__dirname, '../preload/index.js'),
            sandbox: false
        }
    })

    mainWindow.on('ready-to-show', () => {
        mainWindow.show()
    })

    mainWindow.webContents.setWindowOpenHandler((details) => {
        shell.openExternal(details.url)
        return { action: 'deny' }
    })
    // HMR mfor renderer base on electron-vite cli.
    // Load the remote URL for development or the local html file for production.
    if (isDev && process.env['ELECTRON_RENDERER_URL']) {
        mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
    } else {
        mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
    }

    mainWindow.webContents.once('did-finish-load', () => {
        mainWindow.webContents.send('set-view', 'setup')
    })

    mainWindow.on('closed', () => {
        if (!isQuitting && isSetupDone()) {
            createSidePanel()
        }
    })
}

// Register custom protocol for OAuth callback
if (process.defaultApp) {
    // In development, register with the path to the electron binary
    app.setAsDefaultProtocolClient('hivemind', process.execPath, [app.getAppPath()])
} else {
    app.setAsDefaultProtocolClient('hivemind')
}

function handleProtocolUrl(url: string): void {
    console.log('[PROTOCOL] Received URL:', url)
    const parsed = new URL(url)
    if (parsed.hostname === 'callback') {
        const userJson = parsed.searchParams.get('user')
        const token = parsed.searchParams.get('token')
        const githubToken = parsed.searchParams.get('github_token')
        if (userJson) {
            const user: User = JSON.parse(userJson)
            store.set('user', user)
            if (token) store.setEncrypted('token', token)
            if (githubToken) store.setEncrypted('github_token', githubToken)
            store.set('init', true)
            BrowserWindow.getAllWindows().forEach((win) => win.close())
        }
    }
}

// Ensure single instance — on second launch, focus/recreate the window instead
const gotTheLock = app.requestSingleInstanceLock()

if (!gotTheLock) {
    app.quit()
} else {
    app.on('second-instance', (_event, argv) => {
        // On Windows/Linux, the protocol URL is passed as the last argument
        const protocolUrl = argv.find((arg) => arg.startsWith('hivemind://'))
        if (protocolUrl) {
            handleProtocolUrl(protocolUrl)
            return
        }

        const windows = BrowserWindow.getAllWindows()
        if (windows.length <= 1) {
            createMainWindow()
        } else {
            const mainWin = windows.find((w) => !w.isAlwaysOnTop()) ?? windows[0]
            if (mainWin.isMinimized()) mainWin.restore()
            mainWin.focus()
        }
    })

    // macOS: handle protocol URL when app is already running
    app.on('open-url', (event, url) => {
        event.preventDefault()
        handleProtocolUrl(url)
    })
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
    // Set app user model id for windows
    if (process.platform === 'win32') app.setAppUserModelId('com.hivemind.app')
    // Ensure the app icon is visible in the Dock (macOS) / taskbar
    if (process.platform === 'darwin') {
        app.dock?.show()
        app.dock?.setIcon(icon)
    }

    // Default open or close DevTools by F12 in development
    // and ignore CommandOrControl + R in production.
    // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
    app.on('browser-window-created', (_, window) => {
        window.webContents.on('before-input-event', (event, input) => {
            if (input.key === 'F12') {
                if (isDev) window.webContents.toggleDevTools()
                event.preventDefault()
            }
            if (!isDev && input.control && input.key === 'r') {
                event.preventDefault()
            }
        })
    })

    // window triggers
    ipcMain.on('open-main-window', () => {
        createMainWindow()
    })
    ipcMain.on('open-side-window', () => {
        createSidePanel()
    })
    ipcMain.on('init', (_, user: User) => {
        store.set('user', user)
        store.set('init', true)
        BrowserWindow.getAllWindows().forEach((win) => win.close())
    })

    ipcMain.on('start-oauth', () => {
        shell.openExternal('https://github.com/apps/hackuri-hivemind/installations/new')
    })

    ipcMain.on('set-ignore-mouse', (_, ignore: boolean) => {
        if (sidePanelWindow && !sidePanelWindow.isDestroyed()) {
            sidePanelWindow.setIgnoreMouseEvents(ignore, { forward: true })
        }
    })

    ipcMain.on('workspace-changed', (_, workspaceId: string) => {
        store.set('activeWorkspaceId', workspaceId)
        if (sidePanelWindow && !sidePanelWindow.isDestroyed()) {
            sidePanelWindow.webContents.send('workspace-changed', workspaceId)
        }
    })

    ipcMain.handle('get-active-workspace-id', () => store.get('activeWorkspaceId'))

    ipcMain.handle('fetch-workspaces', async () => {
        try {
            return await store.fetchWorkspaces()
        } catch (e) {
            if (e instanceof Error && e.message === 'UNAUTHORIZED') {
                BrowserWindow.getAllWindows().forEach((win) => win.close())
                createSetupWindow()
            }
            throw e
        }
    })
    ipcMain.handle('fetch-workspace', async (_, id: string) => await store.fetchWorkspace(id))
    ipcMain.handle(
        'fetchFeatures',
        async (_, workspaceId: string) => await store.fetchFeatures(workspaceId)
    )
    ipcMain.handle(
        'fetchTasks',
        async (_, params: { workspace?: string; feature?: string }) =>
            await store.fetchTasks(params)
    )
    ipcMain.handle(
        'create-task',
        async (
            _,
            payload: {
                feature: string
                title: string
                description: string
                status: string
                priority: string
            }
        ) => await store.createTask(payload)
    )
    ipcMain.handle(
        'create-feature',
        async (_, payload: { workspace: string; name: string; description: string }) =>
            await store.createFeature(payload)
    )
    ipcMain.handle('fetch-github-repos', async () => await store.fetchGitHubRepos())
    ipcMain.handle(
        'create-workspace',
        async (
            _,
            data: {
                name: string
                github_repo_url: string
                github_repo_owner: string
                github_repo_name: string
            }
        ) => await store.createWorkspace(data)
    )

    if (isSetupDone()) {
        createSidePanel()
    } else {
        createSetupWindow()
    }

    app.on('activate', function () {
        // create main window if only the setup window is open
        if (!isSetupDone() && BrowserWindow.getAllWindows().length === 0) {
            createSetupWindow()
        }
        if (BrowserWindow.getAllWindows().length <= 1) createMainWindow()
    })
})

app.on('before-quit', () => {
    isQuitting = true
})

// Quit when all windows are closed. The side panel is invisible/non-interactive,
// so keeping the process alive after the user closes all windows would leave a
// ghost process that blocks relaunching (single-instance lock).
app.on('window-all-closed', () => {
    app.quit()
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
// ignoring mouse events but "forward" them to renderer
