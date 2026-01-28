// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]


fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|_app| {
            // In a real build, we would launch the bundled sidecar.
            // For MVP dev mode, we might want to launch the python script manually
            // or use the sidecar feature if we bundle python.
            
            // Example of launching a sidecar (requires 'sidecar' binary to be bundled)
            /*
            let sidecar = app.shell().sidecar("sidecar").unwrap();
            let (mut rx, mut _child) = sidecar.spawn().unwrap();
            
            tauri::async_runtime::spawn(async move {
                while let Some(event) = rx.recv().await {
                    if let CommandEvent::Stdout(line) = event {
                         println!("Sidecar: {:?}", String::from_utf8(line));
                    }
                }
            });
            */
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
