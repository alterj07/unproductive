const { app, BrowserWindow, ipcMain } = require('electron/main')
const path = require('node:path')

let mainWindow;

function createWindow () {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, 'preload.js')
    }
  })

  mainWindow.loadFile('templates/index.html')
}

// Function to create child window of parent one
// function createChildWindow() {
//   childWindow = new BrowserWindow({
//     width: 800,
//     height: 600,
//     modal: true,
//     show: false,
//     parent: mainWindow,

//     webPreferences: {
//       nodeIntegration: true,
//       contextIsolation: false,
//       enableRemoteModule: true,
//       preload: path.join(__dirname, 'preload.js')
//     },
//   });

//   childWindow.loadFile("templates/index.html");

//   childWindow.once("ready-to-show", () => {
//     childWindow.show();
//   });
// }

// ipcMain.on("openChildWindow", (event, arg) => {
//   createChildWindow();
// });

// ipcMain.on("closeChildWindow", (event, arg) => {
//   if (childWindow) {
//     childWindow.close();
//   }
// });

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})