import SwiftUI
import WebKit

@main
struct EzerStudioApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 1000, minHeight: 680)
        }
        .windowStyle(.hiddenTitleBar)
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    var serverProcess: Process?

    func applicationDidFinishLaunching(_ notification: Notification) {
        startBackendServer()
    }

    func applicationWillTerminate(_ notification: Notification) {
        serverProcess?.terminate()
    }

    private func startBackendServer() {
        // Automatically start the embedded Python FastAPI backend server on port 8888
        let process = Process()
        let pipe = Pipe()
        
        let fileManager = FileManager.default
        let currentPath = Bundle.main.bundlePath
        
        process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
        process.arguments = ["zsh", "-c", "lsof -i:8888 > /dev/null || (cd \(currentPath)/../.. && ./setup.sh && venv/bin/python -m uvicorn gateways.web_ui:app --host 0.0.0.0 --port 8888)"]
        process.standardOutput = pipe
        process.standardError = pipe
        
        do {
            try process.run()
            self.serverProcess = process
        } catch {
            print("Failed to start backend server: \(error)")
        }
    }
}

struct ContentView: View {
    var body: some View {
        ZStack {
            Color(red: 0.05, green: 0.06, blue: 0.08).ignoresSafeArea()
            WebView(url: URL(string: "http://localhost:8888")!)
                .ignoresSafeArea()
        }
    }
}

struct WebView: NSViewRepresentable {
    let url: URL

    func makeNSView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.preferences.setValue(true, forKey: "developerExtrasEnabled")
        
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.setValue(false, forKey: "drawsBackground") // Transparent background
        webView.load(URLRequest(url: url))
        return webView
    }

    func updateNSView(_ nsView: WKWebView, context: Context) {}
}
