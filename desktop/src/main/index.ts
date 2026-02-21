import { app, shell, BrowserWindow, ipcMain, screen } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'

export function createSidePanel(): void {
    const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize

    // Create the browser window.
    const mainWindow = new BrowserWindow({
        x: screenWidth - 400,
        y: Math.floor((screenHeight - 800) / 2),
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
    ipcMain.on('set-ignore-mouse', (_, ignore: boolean) => {
        mainWindow.setIgnoreMouseEvents(ignore, { forward: true })
    })
    // HMR mfor renderer base on electron-vite cli.
    // Load the remote URL for development or the local html file for production.
    if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
        mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
    } else {
        mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
    }
}

export function createWindow(): void {
    const { width: screenWidth, height: screenHeight } = screen.getPrimaryDisplay().workAreaSize

    // Create the browser window.
    const mainWindow = new BrowserWindow({
        x: Math.floor((screenWidth - 800) / 2),
        y: Math.floor((screenHeight - 600) / 2),
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
    mainWindow.setIgnoreMouseEvents(true, { forward: true })
    ipcMain.on('set-ignore-mouse', (_, ignore: boolean) => {
        mainWindow.setIgnoreMouseEvents(ignore, { forward: true })
    })
    // HMR mfor renderer base on electron-vite cli.
    // Load the remote URL for development or the local html file for production.
    if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
        mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
    } else {
        mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
    }

    mainWindow.webContents.once('did-finish-load', () => {
        mainWindow.webContents.send('set-view', 'main')
    })
}

// Ensure single instance — on second launch, focus/recreate the window instead
const gotTheLock = app.requestSingleInstanceLock()

if (!gotTheLock) {
    app.quit()
} else {
    app.on('second-instance', () => {
        const windows = BrowserWindow.getAllWindows()
        if (windows.length <= 1) {
            createWindow()
        } else {
            const mainWin = windows.find((w) => !w.isAlwaysOnTop()) ?? windows[0]
            if (mainWin.isMinimized()) mainWin.restore()
            mainWin.focus()
        }
    })
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
    // Set app user model id for windows
    electronApp.setAppUserModelId('com.electron')

    // Default open or close DevTools by F12 in development
    // and ignore CommandOrControl + R in production.
    // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
    app.on('browser-window-created', (_, window) => {
        optimizer.watchWindowShortcuts(window)
    })

    // IPC test
    ipcMain.on('ping', () => console.log('pong'))

    createSidePanel()

    app.on('activate', function () {
        // create main window if only the setup window is open
        if (BrowserWindow.getAllWindows().length === 1) createWindow()
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

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
// ignoring mouse events but "forward" them to renderer
