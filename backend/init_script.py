import subprocess
import threading

# Funzione per eseguire un comando e mostrare l'output
def run_command(command):
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Comando '{' '.join(command)}' eseguito con successo:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di '{' '.join(command)}':\n{e.stderr}")

# Funzione per eseguire un comando in un thread separato
def run_command_in_thread(command):
    def target():
        subprocess.run(command)
    thread = threading.Thread(target=target)
    thread.start()
    return thread

# Esegui il comando per popolare i fornitori
run_command(['python', 'fornitori.py'])

# Esegui il comando per avviare l'app Flask in un thread separato
flask_thread = run_command_in_thread(['flask', '--app', 'app', 'run'])

# Attendi che il thread Flask termini (se necessario)
flask_thread.join()
