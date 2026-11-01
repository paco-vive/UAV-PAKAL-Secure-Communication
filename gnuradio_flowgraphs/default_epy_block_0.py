import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self, samp_rate=10e6, hop_rate=50):
        gr.sync_block.__init__(
            self,
            name='Freq Hopper',
            in_sig=None,
            out_sig=[np.complex64]
        )
        self.samp_rate = samp_rate
        self.hop_rate = hop_rate  # saltos por segundo
        
        # Frecuencias de salto típicas del Skylink en 2.4 GHz
        # Offsets respecto al centro (en Hz)
        self.hop_table = [
            -3e6, -2e6, -1.5e6, -1e6, -0.5e6,
             0,
             0.5e6, 1e6, 1.5e6, 2e6, 3e6
        ]
        
        self.current_hop = 0
        self.samples_per_hop = int(samp_rate / hop_rate)
        self.sample_count = 0
        self.phase = 0.0

    def work(self, input_items, output_items):
        out = output_items[0]
        n = len(out)
        
        for i in range(n):
            # Cambiar frecuencia cuando se cumple el período
            if self.sample_count >= self.samples_per_hop:
                self.current_hop = (self.current_hop + 1) % len(self.hop_table)
                self.sample_count = 0
            
            freq = self.hop_table[self.current_hop]
            self.phase += 2 * np.pi * freq / self.samp_rate
            self.phase %= 2 * np.pi
            out[i] = np.exp(1j * self.phase).astype(np.complex64)
            self.sample_count += 1
        
        return n
