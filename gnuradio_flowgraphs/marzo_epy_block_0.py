import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self, samp_rate=10e6, hop_rate=10, hop_spacing=500e3, pattern=0):
        gr.sync_block.__init__(
            self,
            name='Freq Hopper',
            in_sig=None,
            out_sig=[np.complex64]
        )
        self.samp_rate = samp_rate
        self._hop_rate = hop_rate
        self._hop_spacing = hop_spacing
        self._pattern = pattern
        self.phase = 0.0
        self.sample_count = 0
        self.current_hop = 0
        self._build_table()
        self._update_samples_per_hop()

    def _build_table(self):
        n = 11  # número de frecuencias en la tabla
        spacing = self._hop_spacing
        
        if self._pattern == 0:
            # Escalera izquierda a derecha (lo que tienes ahora)
            self.hop_table = [i * spacing - 5 * spacing for i in range(n)]
        elif self._pattern == 1:
            # Escalera derecha a izquierda
            self.hop_table = [5 * spacing - i * spacing for i in range(n)]
        elif self._pattern == 2:
            # Aleatorio (más realista, como Skylink real)
            rng = np.random.default_rng(42)
            self.hop_table = list(rng.permutation(
                [i * spacing - 5 * spacing for i in range(n)]
            ))
        elif self._pattern == 3:
            # Zigzag: izquierda-derecha alternando
            base = [i * spacing - 5 * spacing for i in range(n)]
            self.hop_table = base[::2] + base[1::2]
        elif self._pattern == 4:
            # Solo extremos: salta entre borde izquierdo y derecho
            self.hop_table = [-5*spacing, 5*spacing] * 5

    def _update_samples_per_hop(self):
        self.samples_per_hop = max(1, int(self.samp_rate / self._hop_rate))

    # Setters para actualizar en caliente desde QT Range
    @property
    def hop_rate(self):
        return self._hop_rate
    @hop_rate.setter
    def hop_rate(self, val):
        self._hop_rate = val
        self._update_samples_per_hop()

    @property
    def hop_spacing(self):
        return self._hop_spacing
    @hop_spacing.setter
    def hop_spacing(self, val):
        self._hop_spacing = val
        self._build_table()

    @property
    def pattern(self):
        return self._pattern
    @pattern.setter
    def pattern(self, val):
        self._pattern = int(val)
        self.current_hop = 0
        self._build_table()

    def work(self, input_items, output_items):
        out = output_items[0]
        n = len(out)
        for i in range(n):
            if self.sample_count >= self.samples_per_hop:
                self.current_hop = (self.current_hop + 1) % len(self.hop_table)
                self.sample_count = 0
            freq = self.hop_table[self.current_hop]
            self.phase += 2 * np.pi * freq / self.samp_rate
            self.phase %= 2 * np.pi
            out[i] = np.exp(1j * self.phase).astype(np.complex64)
            self.sample_count += 1
        return n
