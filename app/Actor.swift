import AppKit
import QuartzCore

let support = FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent("Library/Application Support/Actor")
let poses: [String: (String, String, String)] = [
    "appear": ("👋", "Hey! I'm here", "✨"),
    "idle": ("🐣", "Ready when you are", "♡"),
    "thinking": ("🤔", "Thinking it through…", "💭"),
    "working": ("🧑‍💻", "Making things happen…", "✨"),
    "tool": ("🛠️", "On a tiny mission", "⚡️"),
    "waiting": ("🥺", "Need a little help?", "💬"),
    "error": ("😵‍💫", "Oops! A little hiccup", "🩹"),
    "success": ("🥳", "Yay! All done", "🎉"),
    "sleep": ("😴", "Taking a little nap", "💤"),
    "goodbye": ("👋", "See you, buddy!", "♡")
]
let orderedStates = ["appear", "idle", "thinking", "working", "tool", "waiting", "error", "success", "sleep", "goodbye"]

struct CharacterSkin: Decodable {
    let id: String
    let name: String
    let image: String
    let columns: Int
    let rows: Int
    let states: [String: Int]
}

final class CompanionView: NSView {
    var state = "appear"
    var provider = "Actor"
    var source = "Waiting for agent"
    var entered = CACurrentMediaTime()
    var reduced = false
    var petUntil = 0.0
    var appearance = "emoji"
    var skins: [CharacterSkin] = []
    var spriteImages: [String: NSImage] = [:]

    func loadSkins() {
        guard let root = Bundle.main.resourceURL?.appendingPathComponent("Skins"),
              let data = try? Data(contentsOf: root.appendingPathComponent("skins.json")),
              let manifest = try? JSONDecoder().decode([CharacterSkin].self, from: data) else { return }
        skins = manifest.filter { skin in
            guard skin.columns > 0, skin.rows > 0,
                  skin.states.values.allSatisfy({ $0 >= 0 && $0 < skin.columns * skin.rows }),
                  let image = NSImage(contentsOf: root.appendingPathComponent(skin.image)) else { return false }
            spriteImages[skin.id] = image
            return true
        }
    }

    var appearanceName: String {
        if appearance == "cat" { return "Cat" }
        return skins.first(where: { $0.id == appearance })?.name ?? "Emoji"
    }
    var dragged = false
    var origin = NSPoint.zero
    var mouseOrigin = NSPoint.zero
    var didDrag: (() -> Void)?
    var showMenu: ((NSEvent) -> Void)?
    override var acceptsFirstResponder: Bool { true }

    func transition(_ value: String) {
        guard poses[value] != nil, value != state else { return }
        state = value
        entered = CACurrentMediaTime()
        needsDisplay = true
    }

    func label(_ text: String, _ rect: NSRect, size: CGFloat, color: NSColor, weight: NSFont.Weight = .medium) {
        let paragraph = NSMutableParagraphStyle()
        paragraph.alignment = .center
        (text as NSString).draw(in: rect, withAttributes: [.font: NSFont.systemFont(ofSize: size, weight: weight), .foregroundColor: color, .paragraphStyle: paragraph])
    }

    override func draw(_ dirtyRect: NSRect) {
        let now = CACurrentMediaTime()
        let t = now - entered
        let still = reduced || NSWorkspace.shared.accessibilityDisplayShouldReduceMotion
        let phase = still ? 0 : t
        let palette = provider == "Claude" ? NSColor(calibratedRed: 0.92, green: 0.62, blue: 0.43, alpha: 1) : NSColor(calibratedRed: 0.48, green: 0.80, blue: 0.68, alpha: 1)
        let floating = still ? 0 : sin(phase * 2.8) * 4
        let jump = state == "success" && !still ? abs(sin(phase * 5)) * 16 : floating
        let tilt: Double = still ? 0 : (state == "error" ? sin(phase * 19) * max(0, 1-t) * 9 : sin(phase * 2) * (state == "thinking" ? 7 : 3))
        let appear = still ? 1 : min(1, max(0.15, t / 0.35))
        let shadow = NSBezierPath(ovalIn: NSRect(x: 60 + jump/3, y: 65, width: 70-jump*0.6, height: 9))
        NSColor.black.withAlphaComponent(0.12).setFill(); shadow.fill()

        // Small translucent caption, deliberately separate from the unframed emoji.
        let pill = NSBezierPath(roundedRect: NSRect(x: 10, y: 5, width: 170, height: 53), xRadius: 18, yRadius: 18)
        NSColor(calibratedWhite: 0.10, alpha: 0.91).setFill(); pill.fill()
        palette.withAlphaComponent(0.3).setStroke(); pill.lineWidth = 1; pill.stroke()
        let pose = poses[state] ?? poses["idle"]!
        label(now < petUntil ? "You've got this ♡" : pose.1, NSRect(x: 14, y: 28, width: 162, height: 20), size: 12, color: .white)
        let suffix = source == "Demo" ? " · Demo" : (source == "Live hooks" || source == "Local events" ? " · Live" : " · Ready")
        label(provider + suffix, NSRect(x: 19, y: 12, width: 152, height: 15), size: 10, color: palette, weight: .semibold)

        NSGraphicsContext.saveGraphicsState()
        let transform = NSAffineTransform()
        transform.translateX(by: 95, yBy: 115 + jump)
        transform.rotate(byDegrees: CGFloat(tilt))
        transform.scale(by: CGFloat(appear))
        transform.concat()
        let cats = ["appear": "😺", "idle": "🐱", "thinking": "🧐", "working": "😼", "tool": "🐾", "waiting": "🥺", "error": "🙀", "success": "😻", "sleep": "😴", "goodbye": "😽"]
        if let skin = skins.first(where: { $0.id == appearance }), let image = spriteImages[skin.id] {
            let cell = skin.states[state] ?? skin.states["idle"] ?? 0
            let width = image.size.width / CGFloat(skin.columns)
            let height = image.size.height / CGFloat(skin.rows)
            // Atlas indices run left-to-right from the top row; AppKit is bottom-up.
            let source = NSRect(x: CGFloat(cell % skin.columns) * width,
                                y: CGFloat(skin.rows - 1 - cell / skin.columns) * height,
                                width: width, height: height)
            let maxSize = NSSize(width: 144, height: 138)
            let scale = min(maxSize.width / width, maxSize.height / height)
            let destination = NSRect(x: -width * scale / 2, y: -48, width: width * scale, height: height * scale)
            NSGraphicsContext.current?.imageInterpolation = .high
            image.draw(in: destination, from: source, operation: .sourceOver, fraction: 1)
        } else {
            label(appearance == "cat" ? (cats[state] ?? pose.0) : pose.0, NSRect(x: -55, y: -48, width: 110, height: 105), size: 80, color: .white)
        }
        NSGraphicsContext.restoreGraphicsState()
        let sparkle = now < petUntil ? "💖" : pose.2
        label(sparkle, NSRect(x: 135, y: 150 + floating, width: 36, height: 36), size: 25, color: .white)
        if state == "thinking" || state == "working" || state == "tool" {
            for i in 0..<3 {
                let opacity = still ? 0.7 : 0.25 + 0.75 * (sin(phase * 4 - Double(i)) + 1) / 2
                palette.withAlphaComponent(opacity).setFill()
                NSBezierPath(ovalIn: NSRect(x: 80 + i*12, y: 190, width: 5, height: 5)).fill()
            }
        }
        if state == "success" {
            for i in 0..<7 {
                let angle = Double(i) * 0.9
                let distance = 50 + (still ? 8 : fmod(phase * 28 + Double(i*7), 36))
                palette.withAlphaComponent(0.8).setFill()
                NSBezierPath(ovalIn: NSRect(x: 94 + cos(angle)*distance, y: 120 + sin(angle)*distance, width: 4, height: 4)).fill()
            }
        }
    }
    override func mouseDown(with event: NSEvent) {
        origin = window?.frame.origin ?? .zero
        mouseOrigin = NSEvent.mouseLocation
        dragged = false
    }
    override func mouseDragged(with event: NSEvent) {
        let p = NSEvent.mouseLocation
        if hypot(p.x-mouseOrigin.x, p.y-mouseOrigin.y) > 4 { dragged = true }
        guard dragged else { return }
        window?.setFrameOrigin(NSPoint(x: origin.x+p.x-mouseOrigin.x, y: origin.y+p.y-mouseOrigin.y))
    }
    override func mouseUp(with event: NSEvent) {
        if dragged { didDrag?() } else { petUntil = CACurrentMediaTime() + 2 }
    }
    override func rightMouseDown(with event: NSEvent) { showMenu?(event) }
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    var panel: NSPanel!
    let view = CompanionView(frame: NSRect(x: 0, y: 0, width: 190, height: 220))
    var item: NSStatusItem!
    var timer: Timer?
    var painter: Timer?
    var bridge: Process?
    var preferred = "Auto"
    var demoUntil = 0.0
    var pinned = false
    var hidden = false
    var lastProvider = "Codex"
    var pendingState = "idle"
    var pendingSince = CACurrentMediaTime()
    var demoTimer: Timer?

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        view.loadSkins()
        let savedAppearance = UserDefaults.standard.string(forKey: "appearance") ?? "emoji"
        let available = ["emoji", "cat"] + view.skins.map { $0.id }
        view.appearance = available.contains(savedAppearance) ? savedAppearance : "emoji"
        panel = NSPanel(contentRect: view.frame, styleMask: [.borderless, .nonactivatingPanel], backing: .buffered, defer: false)
        panel.isOpaque = false
        panel.backgroundColor = .clear
        panel.hasShadow = false
        panel.level = .floating
        panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
        panel.hidesOnDeactivate = false
        panel.contentView = view
        view.setAccessibilityElement(true)
        view.setAccessibilityRole(.image)
        view.toolTip = "Drag to move · Click for a little love · Right-click for settings"
        view.didDrag = { [weak self] in self?.pinned = true }
        view.showMenu = { [weak self] event in
            guard let self = self else { return }
            NSMenu.popUpContextMenu(self.makeMenu(), with: event, for: self.view)
        }
        item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        item.button?.title = "🐣"
        item.menu = makeMenu()
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/usr/bin/python3")
        process.arguments = [Bundle.main.resourceURL!.appendingPathComponent("bridge.py").path, "monitor"]
        process.standardOutput = FileHandle.nullDevice
        process.standardError = FileHandle.nullDevice
        do { try process.run(); bridge = process } catch { view.source = "Bridge unavailable" }
        place(near: nil)
        panel.orderFrontRegardless()
        timer = Timer.scheduledTimer(withTimeInterval: 0.6, repeats: true) { [weak self] _ in self?.update() }
        painter = Timer.scheduledTimer(withTimeInterval: 1/30, repeats: true) { [weak self] _ in
            guard let self = self, self.panel.isVisible else { return }
            self.view.needsDisplay = true
        }
        update()
    }
    func applicationWillTerminate(_ notification: Notification) { bridge?.terminate() }

    func makeMenu() -> NSMenu {
        let menu = NSMenu()
        func add(_ title: String, _ action: Selector, value: String? = nil, checked: Bool = false) {
            let entry = NSMenuItem(title: title, action: action, keyEquivalent: "")
            entry.target = self; entry.representedObject = value; entry.state = checked ? .on : .off
            menu.addItem(entry)
        }
        let heading = NSMenuItem(title: "Actor · Your tiny coding buddy", action: nil, keyEquivalent: "")
        menu.addItem(heading); menu.addItem(.separator())
        for name in ["Auto", "Codex", "Claude"] { add("Follow " + name, #selector(selectProvider(_:)), value: name, checked: preferred == name) }
        menu.addItem(.separator())
        let appearanceItem = NSMenuItem(title: "Appearance · " + view.appearanceName, action: nil, keyEquivalent: "")
        let appearances = NSMenu()
        let choices = [("emoji", "Emoji 🐣"), ("cat", "Cat 🐱")] + view.skins.map { ($0.id, $0.name) }
        for (id, name) in choices {
            let entry = NSMenuItem(title: name, action: #selector(selectAppearance(_:)), keyEquivalent: "")
            entry.target = self; entry.representedObject = id
            entry.state = view.appearance == id ? .on : .off
            appearances.addItem(entry)
        }
        appearanceItem.submenu = appearances; menu.addItem(appearanceItem)
        add("Gentle motion", #selector(toggleMotion), checked: view.reduced)
        add("Follow app position", #selector(resetPosition), checked: !pinned)
        add(hidden ? "Show buddy" : "Hide buddy", #selector(toggleHidden))
        menu.addItem(.separator())
        let demo = NSMenuItem(title: "Try a mood", action: nil, keyEquivalent: "")
        let submenu = NSMenu()
        for state in orderedStates {
            let entry = NSMenuItem(title: poses[state]!.0 + "  " + state.capitalized, action: #selector(tryMood(_:)), keyEquivalent: "")
            entry.target = self; entry.representedObject = state; submenu.addItem(entry)
        }
        demo.submenu = submenu; menu.addItem(demo)
        add("Play all moods", #selector(playDemo))
        add("Return to live", #selector(returnLive))
        menu.addItem(.separator())
        let connection = NSMenuItem(title: view.provider + " · " + view.source, action: nil, keyEquivalent: "")
        menu.addItem(connection)
        add("Quit Actor", #selector(quit))
        return menu
    }
    func refreshMenu() { item.menu = makeMenu() }
    @objc func selectProvider(_ sender: NSMenuItem) { preferred = sender.representedObject as? String ?? "Auto"; returnLive() }
    @objc func selectAppearance(_ sender: NSMenuItem) {
        guard let id = sender.representedObject as? String,
              (["emoji", "cat"] + view.skins.map { $0.id }).contains(id) else { return }
        view.appearance = id
        UserDefaults.standard.set(id, forKey: "appearance")
        view.entered = CACurrentMediaTime()
        view.needsDisplay = true
        refreshMenu()
    }
    @objc func toggleMotion() { view.reduced.toggle(); refreshMenu() }
    @objc func resetPosition() { pinned = false; update(); refreshMenu() }
    @objc func toggleHidden() { hidden.toggle(); update(); refreshMenu() }
    @objc func quit() { NSApp.terminate(nil) }
    @objc func returnLive() { demoUntil = 0; demoTimer?.invalidate(); update(); refreshMenu() }
    @objc func tryMood(_ sender: NSMenuItem) {
        demoTimer?.invalidate()
        showDemo(sender.representedObject as? String ?? "idle")
    }
    func showDemo(_ state: String) {
        demoUntil = CACurrentMediaTime() + 10
        hidden = false; view.source = "Demo"; view.provider = "Actor"
        view.transition(state); panel.orderFrontRegardless(); refreshMenu()
    }
    @objc func playDemo() {
        demoTimer?.invalidate()
        var index = 0
        showDemo(orderedStates[index])
        demoTimer = Timer.scheduledTimer(withTimeInterval: 2.5, repeats: true) { [weak self] timer in
            index += 1
            guard let self = self, index < orderedStates.count else { timer.invalidate(); self?.returnLive(); return }
            self.showDemo(orderedStates[index])
        }
    }

    func apps() -> [NSRunningApplication] {
        NSWorkspace.shared.runningApplications.filter {
            let name = $0.localizedName ?? ""
            return ["Codex", "ChatGPT", "Claude"].contains(name) && $0.activationPolicy == .regular
        }
    }
    func update() {
        if hidden { panel.orderOut(nil); return }
        if CACurrentMediaTime() < demoUntil { return }
        let running = apps().filter { preferred == "Auto" || (preferred == "Claude" ? $0.localizedName == "Claude" : $0.localizedName != "Claude") }
        let front = NSWorkspace.shared.frontmostApplication
        let chosen = running.first { app in
            preferred == "Auto" ? app.processIdentifier == front?.processIdentifier : (preferred == "Claude" ? app.localizedName == "Claude" : app.localizedName != "Claude")
        } ?? running.first { lastProvider == "Claude" ? $0.localizedName == "Claude" : $0.localizedName != "Claude" } ?? running.first
        var status: [String: [String: Any]] = [:]
        if let data = try? Data(contentsOf: support.appendingPathComponent("status.json")), let decoded = try? JSONSerialization.jsonObject(with: data) as? [String: [String: Any]] { status = decoded }
        let provider = preferred == "Auto" ? (chosen?.localizedName == "Claude" ? "Claude" : "Codex") : preferred
        lastProvider = provider
        let modified = (try? FileManager.default.attributesOfItem(atPath: support.appendingPathComponent("status.json").path)[.modificationDate]) as? Date
        let bridgeAlive = modified.map { Date().timeIntervalSince($0) < 5 } ?? false
        let record = bridgeAlive ? status[provider] : nil
        let recentlyActive = Date().timeIntervalSince1970 - (record?["at"] as? Double ?? 0) < 90
        // CLI work can keep the buddy visible even without a desktop app.
        guard chosen != nil || recentlyActive else { panel.orderOut(nil); return }
        if !panel.isVisible { view.transition("appear") }
        view.provider = provider
        view.source = record?["source"] as? String ?? (bridgeAlive ? "Waiting for agent" : "Bridge unavailable")
        let target = record?["state"] as? String ?? "idle"
        if target != pendingState { pendingState = target; pendingSince = CACurrentMediaTime() }
        let urgent = target == "waiting" || target == "error"
        if urgent || (CACurrentMediaTime() - view.entered >= 0.7 && CACurrentMediaTime() - pendingSince >= 0.25) { view.transition(target) }
        if !pinned { place(near: chosen) }
        panel.orderFrontRegardless()
        view.setAccessibilityLabel(view.provider + ": " + (poses[view.state]?.1 ?? view.state))
        item.button?.title = poses[view.state]?.0 ?? "🐣"
        refreshMenu()
    }
    func place(near app: NSRunningApplication?) {
        let screen = NSScreen.main ?? NSScreen.screens[0]
        var visible = screen.visibleFrame
        var point = NSPoint(x: visible.maxX - 205, y: visible.minY + 35)
        if let app = app,
           let windows = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]],
           let window = windows.first(where: { ($0[kCGWindowOwnerPID as String] as? Int32) == app.processIdentifier && ($0[kCGWindowLayer as String] as? Int) == 0 && (($0[kCGWindowBounds as String] as? [String: CGFloat])?["Width"] ?? 0) > 300 }),
           let bounds = window[kCGWindowBounds as String] as? [String: CGFloat] {
            let desktopHeight = NSScreen.screens.first?.frame.height ?? screen.frame.height
            let rect = NSRect(x: bounds["X"] ?? 0, y: desktopHeight - (bounds["Y"] ?? 0) - (bounds["Height"] ?? 0), width: bounds["Width"] ?? 0, height: bounds["Height"] ?? 0)
            visible = NSScreen.screens.first(where: { $0.frame.intersects(rect) })?.visibleFrame ?? visible
            let outside = rect.maxX - 10
            point = NSPoint(x: outside + 190 <= visible.maxX ? outside : rect.maxX - 190, y: rect.minY + 25)
        }
        point.x = min(max(point.x, visible.minX), visible.maxX - 190)
        point.y = min(max(point.y, visible.minY), visible.maxY - 220)
        panel.setFrameOrigin(point)
    }
}
let application = NSApplication.shared
let delegate = AppDelegate()
application.delegate = delegate
application.run()
