import sys
import os
import time
import threading
import signal
import subprocess
import requests
import psutil
import webview
import reflex as rx

config = rx.Config(
    app_name="reflex_app",
    api_url="http://localhost:8000",
    frontend_port=3000,
    backend_port=8000,
)

backend_proc = None
frontend_proc = None
_cleaned = False

def start_backend():
    global backend_proc
    try:
        backend_proc = subprocess.Popen(
            [sys.executable, "-m", "reflex", "run", "--backend-only", f"--backend-port={config.backend_port}"],
            preexec_fn=os.setsid
        )
        print(f"Backend iniciado, PID: {backend_proc.pid}")
    except Exception as e:
        print(f"Backend error: {str(e)}")
    return backend_proc

def start_frontend():
    global frontend_proc
    try:
        frontend_proc = subprocess.Popen(
            [sys.executable, "-m", "reflex", "run", "--frontend-only", f"--frontend-port={config.frontend_port}"],
            preexec_fn=os.setsid
        )
        print(f"Frontend iniciado, PID: {frontend_proc.pid}")
    except Exception as e:
        print(f"Frontend error: {str(e)}")
    return frontend_proc

def kill_process_by_port(port):
    try:
        for proc in psutil.process_iter():
            try:
                conns = proc.net_connections()
                for conn in conns:
                    if conn.laddr and conn.laddr.port == port:
                        proc.kill()
                        print(f"Proceso {proc.pid} matado en puerto {port}")
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"Error matando proceso en puerto {port}: {str(e)}")

def cleanup():
    global _cleaned, backend_proc, frontend_proc
    if _cleaned:
        return
    _cleaned = True

    def kill_proc_and_children(proc_obj):
        try:
            children = proc_obj.children(recursive=True)
            for child in children:
                child.terminate()
            gone, still_alive = psutil.wait_procs(children, timeout=5)
            for p in still_alive:
                p.kill()
            proc_obj.terminate()
            proc_obj.wait(timeout=5)
        except Exception as e:
            print(f"Error killing process {proc_obj.pid}: {str(e)}")

    try:
        if backend_proc and backend_proc.poll() is None:
            kill_proc_and_children(psutil.Process(backend_proc.pid))
            print(f"Backend PID {backend_proc.pid} terminado.")
        if frontend_proc and frontend_proc.poll() is None:
            kill_proc_and_children(psutil.Process(frontend_proc.pid))
            print(f"Frontend PID {frontend_proc.pid} terminado.")
        try:
            subprocess.run(["pkill", "-f", "reflex"], check=True)
        except subprocess.CalledProcessError:
            pass
        print("Limpieza de procesos completada")
    except Exception as e:
        print(f"Error en cleanup: {str(e)}")

def check_services():
    try:
        resp_back = requests.get(f"http://localhost:{config.backend_port}/ping")
        time.sleep(5)
        resp_front = requests.get(f"http://localhost:{config.frontend_port}")
        return (resp_back.status_code == 200) and (resp_front.status_code == 200)
    except Exception as e:
        print(f"Error checking services: {str(e)}")
        return False

def main():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        os.chdir(base_path)
        print("Ejecutando en modo frozen, base_path:", base_path)
    else:
        base_path = os.getcwd()
        print("Ejecutando en modo normal, base_path:", base_path)
    signal.signal(signal.SIGTERM, lambda *args: (cleanup(), sys.exit(0)))
    signal.signal(signal.SIGINT, lambda *args: (cleanup(), sys.exit(0)))
    cleanup()
    print("Iniciando servicios de Reflex...")
    start_backend()
    start_frontend()
    max_attempts = 30
    attempts = 0
    while not check_services() and attempts < max_attempts:
        time.sleep(1)
        attempts += 1
        print(f"Intentando conectar... ({attempts}/{max_attempts})")
    if attempts >= max_attempts:
        print("Error: No se pudieron iniciar los servicios")
        cleanup()
        sys.exit(1)
    else:
        print("Servicios iniciados correctamente")
    window = webview.create_window(
        "Demo Reflex Desktop",
        f"http://localhost:{config.frontend_port}",
        width=1024,
        height=768,
    )
    window.events.closed += lambda: cleanup()
    try:
        webview.start()
    except Exception as e:
        print(f"Error en webview: {str(e)}")
    finally:
        cleanup()
    print("Aplicación cerrada.")

if __name__ == '__main__':
    main()
