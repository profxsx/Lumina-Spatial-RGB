// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/

#[tauri::command]
fn minimize_window(window: tauri::Window) {
    let _ = window.minimize();
}

#[tauri::command]
fn maximize_window(window: tauri::Window) {
    if let Ok(is_max) = window.is_maximized() {
        if is_max {
            let _ = window.unmaximize();
        } else {
            let _ = window.maximize();
        }
    }
}

#[tauri::command]
fn close_window(window: tauri::Window) {
    let _ = window.close();
}

#[tauri::command]
fn resize_window(window: tauri::Window, dx: i32, dy: i32) {
    if let Ok(size) = window.inner_size() {
        // Enforce the standard minimum application size limits
        let new_w = (size.width as i32 + dx).max(1024);
        let new_h = (size.height as i32 + dy).max(768);
        let _ = window.set_size(tauri::Size::Physical(tauri::PhysicalSize {
            width: new_w as u32,
            height: new_h as u32,
        }));
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![minimize_window, maximize_window, close_window, resize_window])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
