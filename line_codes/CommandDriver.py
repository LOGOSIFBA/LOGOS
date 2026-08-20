import threading

class LatestCommandDriver:
    """
    Roda em thread própria; sempre envia o comando de velocidade mais
    recente para o motor, descartando qualquer correção intermediária
    que tenha ficado obsoleta enquanto o BLE ainda processava a anterior.
    Evita o acúmulo de comandos atrasados na fila interna do TractionModule.
    """
    def _init_(self, motor):
        self.motor = motor
        self._lock = threading.Lock()
        self._pending = None
        self._wake = threading.Event()
        self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def set_speed(self, value):
        with self._lock:
            self._pending = -value
        self._wake.set()

    def _run(self):
        while not self._stop:
            self._wake.wait()
            self._wake.clear()
            with self._lock:
                value = self._pending
                self._pending = None
            if value is not None:
                try:
                    self.motor._move_impl(value)
                except Exception as exc:
                    print(f"[driver] move failed: {exc}", flush=True)

    def stop(self):
        with self._lock:
            self._pending = None

            try:
                self.motor._move_impl(0)
            except Exception as exc:
                print(f"[driver] stop failed: {exc}", flush=True)
