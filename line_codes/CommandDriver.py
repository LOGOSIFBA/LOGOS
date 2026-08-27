import threading
import time


class LatestCommandDriver:

    def __init__(self, motor):
        self.motor = motor
        self._lock = threading.Lock()
        self._pending = None
        self._wake = threading.Event()
        self._stop = False

        self._thread = threading.Thread(
            target=self._run,
            daemon=True
        )
        self._thread.start()

    def set_speed(self, value):
        if self._stop:
            return

        with self._lock:
            self._pending = value

        self._wake.set()

    def stop(self):
        self.set_speed(0)

    def shutdown(self):
        # Impede novos comandos
        self._stop = True

        # Descarta comando pendente
        with self._lock:
            self._pending = None

        # Acorda a thread para ela terminar
        self._wake.set()

        # Espera a thread terminar
        self._thread.join(timeout=1.0)

        # Só depois que a thread terminou,
        # manda o comando de parada.
        try:
            self.motor._move_impl(0)
        except Exception as exc:
            print(
                f"[driver] shutdown stop failed: {exc}",
                flush=True
            )

    def _run(self):
        while not self._stop:
            self._wake.wait()

            self._wake.clear()

            if self._stop:
                break

            with self._lock:
                value = self._pending
                self._pending = None

            if value is None:
                continue

            try:
                self.motor._move_impl(value)
            except Exception as exc:
                print(
                    f"[driver] move failed: {exc}",
                    flush=True
                )
