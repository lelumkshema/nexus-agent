"""
NEXUS-AGENT: Academic Telemetry Bridge Server
Lightweight Python HTTP server serving the interactive research dashboard
and providing REST API endpoints to execute the research engine live.
"""

import http.server
import socketserver
import json
import os
import sys
import traceback

# Ensure workspace root is in path
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from src.orchestrator import UnifiedNexusOrchestrator
from benchmarks.tasks import get_academic_benchmark_tasks


PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class AcademicTelemetryHandler(http.server.SimpleHTTPRequestHandler):
    """Handles static files and API requests for research experiments."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            status = {
                "status": "online",
                "python_version": sys.version,
                "framework": "NEXUS-AGENT",
                "candidate": "AGY-PHD-2026",
            }
            self.wfile.write(json.dumps(status).encode("utf-8"))
            return

        elif self.path == "/api/run-task":
            try:
                orchestrator = UnifiedNexusOrchestrator()
                tasks = get_academic_benchmark_tasks()
                result = orchestrator.solve_task(tasks[2])  # Run synthesis task
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result, indent=2).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                err = {"error": str(e), "traceback": traceback.format_exc()}
                self.wfile.write(json.dumps(err).encode("utf-8"))
            return

        super().do_GET()


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), AcademicTelemetryHandler) as httpd:
        print(f"================================================================================")
        print(f"NEXUS-AGENT Research Telemetry Workbench Server active on http://localhost:{PORT}")
        print(f"Academic Viva Defense Portal: http://localhost:{PORT}/index.html")
        print(f"================================================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down research server...")
            httpd.server_close()


if __name__ == "__main__":
    run_server()
