// Cross-platform shell. Rust owns the window and the polling; every pixel is
// drawn by ui/index.html, which is generated from the same geometry as the
// macOS sheets. Nothing here knows what a mood looks like.
use std::{fs, path::PathBuf, thread, time::Duration};
use tauri::Emitter;

fn status_path() -> Option<PathBuf> {
    let home = PathBuf::from(std::env::var("HOME").ok()?);
    // Same file bridge.py writes. Windows would read %APPDATA% instead.
    Some(home.join("Library/Application Support/Actor/status.json"))
}

/// Codex owns the character when it is present; Claude is the fallback, matching
/// the precedence the macOS app already uses.
fn current_state(text: &str) -> Option<String> {
    let value: serde_json::Value = serde_json::from_str(text).ok()?;
    let record = value.get("Codex").or_else(|| value.get("Claude"))?;
    Some(record.get("state")?.as_str()?.to_string())
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let handle = app.handle().clone();
            thread::spawn(move || {
                let path = status_path();
                let mut last = String::new();
                loop {
                    if let Some(path) = &path {
                        if let Some(state) = fs::read_to_string(path).ok().as_deref().and_then(current_state) {
                            if state != last {
                                last = state.clone();
                                let _ = handle.emit("state", state);
                            }
                        }
                    }
                    thread::sleep(Duration::from_millis(600));
                }
            });
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("failed to start");
}
