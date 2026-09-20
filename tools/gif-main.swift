// Appended to a copy of Actor.swift (with its app launch stripped) so the GIF is
// rendered by the very same draw() the shipped app uses — no reimplementation.
import ImageIO
import UniformTypeIdentifiers

_ = NSApplication.shared

let fps = 15.0
let zoom: CGFloat = 1.6
let provider = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "Claude"
let output = URL(fileURLWithPath: CommandLine.arguments.count > 2 ? CommandLine.arguments[2] : "actor.gif")

// state, seconds
let timeline: [(String, Double)] = [
    ("thinking", 2.0), ("working", 2.0), ("tool", 1.6), ("success", 2.2), ("idle", 1.6)
]

let size = NSSize(width: (CompanionView.base.width * zoom).rounded(),
                  height: (CompanionView.base.height * zoom).rounded())
let view = CompanionView(frame: NSRect(origin: .zero, size: size))
view.scale = zoom
view.provider = provider
view.source = "Live hooks"

guard let destination = CGImageDestinationCreateWithURL(
    output as CFURL, UTType.gif.identifier as CFString,
    Int(timeline.reduce(0) { $0 + $1.1 } * fps), nil) else {
    FileHandle.standardError.write(Data("cannot create \(output.path)\n".utf8)); exit(1)
}
CGImageDestinationSetProperties(destination, [
    kCGImagePropertyGIFDictionary: [kCGImagePropertyGIFLoopCount: 0]
] as CFDictionary)

var count = 0
for (state, seconds) in timeline {
    for frame in 0..<Int(seconds * fps) {
        let local = Double(frame) / fps
        view.state = state
        view.entered = CACurrentMediaTime() - local
        guard let rep = view.bitmapImageRepForCachingDisplay(in: view.bounds) else { continue }
        // Opaque card: GIF has only 1-bit alpha, so a soft shadow over transparency would fringe.
        NSGraphicsContext.saveGraphicsState()
        NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
        NSColor(calibratedRed: 0.063, green: 0.075, blue: 0.102, alpha: 1).setFill()
        NSBezierPath(rect: view.bounds).fill()
        NSGraphicsContext.restoreGraphicsState()
        view.cacheDisplay(in: view.bounds, to: rep)
        guard let image = rep.cgImage else { continue }
        CGImageDestinationAddImage(destination, image, [
            kCGImagePropertyGIFDictionary: [kCGImagePropertyGIFDelayTime: 1.0 / fps]
        ] as CFDictionary)
        count += 1
    }
}
if !CGImageDestinationFinalize(destination) {
    FileHandle.standardError.write(Data("failed to write gif\n".utf8)); exit(1)
}
print("wrote \(output.path) — \(count) frames, \(Int(size.width))x\(Int(size.height))")
