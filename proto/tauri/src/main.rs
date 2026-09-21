// Cross-platform shell. Rust owns the window, the menu and the polling.
// Every pixel is drawn by ui/index.html; nothing here knows what a mood looks like.
use std::{fs, path::PathBuf, sync::Mutex, thread, time::Duration};
use tauri::{
    menu::{CheckMenuItemBuilder, ContextMenu, MenuBuilder, MenuItemBuilder, SubmenuBuilder},
    Emitter, LogicalSize, Manager,
};

const MOODS: [&str; 10] = [
    "appear", "idle", "thinking", "working", "tool", "waiting", "error", "success", "sleep",
    "goodbye",
];

struct Prefs {
    follow: String,     // Auto | Codex | Claude
    appearance: String, // emoji | cat
    size: String,       // small | medium | large
    gentle: bool,
    pinned: bool,
    hidden: bool,
    demo: Option<String>,
    live_state: String,
    provider: String,
    source: String,
}

impl Default for Prefs {
    fn default() -> Self {
        Prefs {
            follow: "Auto".into(),
            appearance: "emoji".into(),
            size: "large".into(),
            gentle: false,
            pinned: false,
            hidden: false,
            demo: None,
            live_state: "idle".into(),
            provider: "Codex".into(),
            source: "Waiting for agent".into(),
        }
    }
}

struct Shared(Mutex<Prefs>);

/// One directory per platform, shared with the bridge. Keep in sync with
/// data_root() in app/bridge.py: if these two disagree the window opens and
/// never receives a state.
fn data_dir() -> Option<PathBuf> {
    // HOME is not set for every Windows session; USERPROFILE always is.
    let home = || {
        std::env::var("HOME")
            .or_else(|_| std::env::var("USERPROFILE"))
            .ok()
            .map(PathBuf::from)
    };
    if cfg!(target_os = "macos") {
        Some(home()?.join("Library/Application Support/Actor"))
    } else if cfg!(target_os = "windows") {
        let base = std::env::var("APPDATA")
            .ok()
            .map(PathBuf::from)
            .or_else(|| Some(home()?.join("AppData/Roaming")))?;
        Some(base.join("Actor"))
    } else {
        let base = std::env::var("XDG_DATA_HOME")
            .ok()
            .map(PathBuf::from)
            .or_else(|| Some(home()?.join(".local/share")))?;
        Some(base.join("Actor"))
    }
}

fn status_path() -> Option<PathBuf> {
    Some(data_dir()?.join("status.json"))
}

fn window_size(size: &str) -> LogicalSize<f64> {
    match size {
        "small" => LogicalSize::new(156.0, 132.0),
        "medium" => LogicalSize::new(200.0, 168.0),
        _ => LogicalSize::new(250.0, 210.0),
    }
}

/// One event carries everything the renderer draws, so it can never show a mood
/// from one update next to a caption from another.
fn push(app: &tauri::AppHandle) {
    let shared = app.state::<Shared>();
    let prefs = shared.0.lock().unwrap();
    let demo = prefs.demo.is_some();
    let _ = app.emit(
        "update",
        serde_json::json!({
            "state": prefs.demo.clone().unwrap_or_else(|| prefs.live_state.clone()),
            "provider": if demo { "Actor".to_string() } else { prefs.provider.clone() },
            "source": if demo { "Demo".to_string() } else { prefs.source.clone() },
            "appearance": prefs.appearance,
            "gentle": prefs.gentle,
        }),
    );
}

fn build_menu(app: &tauri::AppHandle) -> tauri::Result<tauri::menu::Menu<tauri::Wry>> {
    let prefs = app.state::<Shared>();
    let p = prefs.0.lock().unwrap();

    let mut menu = MenuBuilder::new(app).item(
        &MenuItemBuilder::with_id("header", "Actor · Your tiny coding buddy")
            .enabled(false)
            .build(app)?,
    );
    menu = menu.separator();
    for name in ["Auto", "Codex", "Claude"] {
        menu = menu.item(
            &CheckMenuItemBuilder::with_id(format!("follow:{name}"), format!("Follow {name}"))
                .checked(p.follow == name)
                .build(app)?,
        );
    }
    menu = menu.separator();

    let mut appearance = SubmenuBuilder::new(app, format!("Appearance · {}", title(&p.appearance)));
    for (id, label) in [("emoji", "Emoji 🐣"), ("cat", "Cat 🐱")] {
        appearance = appearance.item(
            &CheckMenuItemBuilder::with_id(format!("appearance:{id}"), label)
                .checked(p.appearance == id)
                .build(app)?,
        );
    }
    menu = menu.item(&appearance.build()?);

    let mut sizes = SubmenuBuilder::new(app, format!("Size · {}", title(&p.size)));
    for id in ["small", "medium", "large"] {
        sizes = sizes.item(
            &CheckMenuItemBuilder::with_id(format!("size:{id}"), title(id))
                .checked(p.size == id)
                .build(app)?,
        );
    }
    menu = menu.item(&sizes.build()?);

    menu = menu
        .item(
            &CheckMenuItemBuilder::with_id("gentle", "Gentle motion")
                .checked(p.gentle)
                .build(app)?,
        )
        .item(
            &CheckMenuItemBuilder::with_id("unpin", "Follow app position")
                .checked(!p.pinned)
                .build(app)?,
        )
        .item(&MenuItemBuilder::with_id("hide", if p.hidden { "Show buddy" } else { "Hide buddy" }).build(app)?)
        .separator();

    let mut moods = SubmenuBuilder::new(app, "Try a mood");
    for mood in MOODS {
        moods = moods.item(&MenuItemBuilder::with_id(format!("mood:{mood}"), title(mood)).build(app)?);
    }
    menu = menu
        .item(&moods.build()?)
        .item(&MenuItemBuilder::with_id("playall", "Play all moods").build(app)?)
        .item(&MenuItemBuilder::with_id("live", "Return to live").build(app)?)
        .separator()
        .item(
            &MenuItemBuilder::with_id("status", format!("{} · {}", p.provider, p.source))
                .enabled(false)
                .build(app)?,
        )
        .item(&MenuItemBuilder::with_id("quit", "Quit Actor").build(app)?);

    menu.build()
}

fn title(value: &str) -> String {
    let mut chars = value.chars();
    match chars.next() {
        Some(first) => first.to_uppercase().collect::<String>() + chars.as_str(),
        None => String::new(),
    }
}

#[tauri::command]
fn show_menu(app: tauri::AppHandle, window: tauri::Window) -> Result<(), String> {
    let menu = build_menu(&app).map_err(|e| e.to_string())?;
    menu.popup(window).map_err(|e| e.to_string())
}

/// Dragging is started explicitly rather than with data-tauri-drag-region, because
/// that attribute only fires when the element under the pointer carries it — and the
/// pointer is almost always over the emoji or the caption, which are children.
#[tauri::command]
fn start_drag(window: tauri::Window) -> Result<(), String> {
    window.start_dragging().map_err(|e| e.to_string())
}

#[tauri::command]
fn ready(app: tauri::AppHandle) {
    push(&app);
}

fn handle_menu(app: &tauri::AppHandle, id: &str) {
    let shared = app.state::<Shared>();
    let mut resize = None;
    {
        let mut p = shared.0.lock().unwrap();
        match id.split_once(':') {
            Some(("follow", value)) => p.follow = value.into(),
            Some(("appearance", value)) => p.appearance = value.into(),
            Some(("size", value)) => {
                p.size = value.into();
                resize = Some(window_size(value));
            }
            Some(("mood", value)) => p.demo = Some(value.into()),
            _ => match id {
                "gentle" => p.gentle = !p.gentle,
                "unpin" => p.pinned = !p.pinned,
                "hide" => p.hidden = !p.hidden,
                "live" => p.demo = None,
                _ => {}
            },
        }
    }
    if id == "quit" {
        app.exit(0);
        return;
    }
    if let Some(window) = app.get_webview_window("buddy") {
        if let Some(size) = resize {
            let _ = window.set_size(size);
        }
        if id == "hide" {
            let hidden = shared.0.lock().unwrap().hidden;
            let _ = if hidden { window.hide() } else { window.show() };
        }
        if id == "playall" {
            let handle = app.clone();
            thread::spawn(move || {
                for mood in MOODS {
                    handle.state::<Shared>().0.lock().unwrap().demo = Some(mood.into());
                    push(&handle);
                    thread::sleep(Duration::from_millis(1600));
                }
                handle.state::<Shared>().0.lock().unwrap().demo = None;
                push(&handle);
            });
            return;
        }
    }
    push(app);
}

fn main() {
    tauri::Builder::default()
        .manage(Shared(Mutex::new(Prefs::default())))
        .invoke_handler(tauri::generate_handler![show_menu, ready, start_drag])
        .on_menu_event(|app, event| handle_menu(app, event.id().as_ref()))
        .setup(|app| {
            let handle = app.handle().clone();
            thread::spawn(move || {
                let path = status_path();
                loop {
                    if let Some(path) = &path {
                        if let Ok(text) = fs::read_to_string(path) {
                            if let Ok(value) = serde_json::from_str::<serde_json::Value>(&text) {
                                let follow = handle.state::<Shared>().0.lock().unwrap().follow.clone();
                                let record = match follow.as_str() {
                                    "Codex" => value.get("Codex"),
                                    "Claude" => value.get("Claude"),
                                    _ => value.get("Codex").or_else(|| value.get("Claude")),
                                };
                                if let Some(record) = record {
                                    let state = record.get("state").and_then(|v| v.as_str()).unwrap_or("idle");
                                    let provider = record.get("provider").and_then(|v| v.as_str()).unwrap_or("Codex");
                                    let source = record.get("source").and_then(|v| v.as_str()).unwrap_or("");
                                    let shared = handle.state::<Shared>();
                                    let mut p = shared.0.lock().unwrap();
                                    let changed = p.live_state != state || p.provider != provider || p.source != source;
                                    p.live_state = state.into();
                                    p.provider = provider.into();
                                    p.source = source.into();
                                    drop(p);
                                    if changed {
                                        push(&handle);
                                    }
                                }
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
