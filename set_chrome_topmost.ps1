param([string]$port)

# set_chrome_topmost.ps1
# Waits for a Chrome main window to appear and sets it to topmost using user32 SetWindowPos.

Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class Win {
    [DllImport("user32.dll")]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
}
"@

$HWND_TOPMOST = -1
$SWP_NOSIZE = 0x0001
$SWP_NOMOVE = 0x0002
$SWP_SHOWWINDOW = 0x0040
$flags = $SWP_NOSIZE -bor $SWP_NOMOVE -bor $SWP_SHOWWINDOW

# Try repeatedly for a short time to find a Chrome process with a main window handle
for ($i = 0; $i -lt 50; $i++) {
    $p = Get-Process -Name chrome -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if ($p) {
        try {
            $hwnd = [IntPtr]$p.MainWindowHandle
            [Win]::SetWindowPos($hwnd, [IntPtr]$HWND_TOPMOST, 0, 0, 0, 0, $flags) | Out-Null
            break
        } catch {
            # ignore and retry
        }
    }
    Start-Sleep -Milliseconds 200
}

# End of script
